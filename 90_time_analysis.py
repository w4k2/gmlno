import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from scipy.signal import medfilt

from itertools import cycle

lines = ["-", "-.", ":"]
linecycler = cycle(lines)

colors = ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d"]
colorcycler = cycle(colors)

n_requests_config = [
    100,
    125,
    150,
    175,
    200,
    225,
    250,
    275,
    300,
    325,
    350,
    375,
    400,
    425,
    450,
    475,
    500,
    525,
    550,
    575,
    600,
    625,
    650,
]

preprocessing_data = pd.read_csv("00_times.csv")
us_data = pd.read_csv("00_timestable_us.csv", index_col=0)
euro_data = pd.read_csv("00_timestable_euro.csv", index_col=0)

simulation = {"us26": us_data, "euro28": euro_data}

# fig, ax = plt.subplots(1, 1, figsize=(7, 7))
# data = []
df = preprocessing_data
df = df.iloc[:, 1:]  # drop file index

fig = plt.figure(figsize=(15, 4))

ax1 = fig.add_subplot(1, 3, 1)
ax2 = fig.add_subplot(1, 3, 2, sharey=ax1)
ax3 = fig.add_subplot(1, 3, 3)

ax1.set_ylabel("time [ms]")

ax = ax1
ax.set_title(f"Simulation Time")
ax.grid(ls=":")
ax.set_xlabel("# requests")

for topology in simulation:
    sim_curve = np.array(simulation[topology])
    sim_curve_mean = np.mean(sim_curve, axis=0)
    # ax.axhline(y=np.mean(sim_curve), color='k', linestyle='--')
    ax.plot(n_requests_config, sim_curve_mean, c=next(colorcycler), label=f"{topology}")

ax.legend(loc='upper left', fontsize=8)

ax = ax2
ax.grid(ls=":")
ax.set_title(f"Regresson Preprocessing Time")
ax.set_xlabel("# requests")

df = preprocessing_data

for topology, df in df.groupby("topology"):
    for graph, df in df.groupby("graph"):
        time_sum = []

        for fn_name, df in df.groupby("fn_name"):
            measures = []

            for n_requsts, df in df.groupby("n_requests"):
                measures.append(df["time"])

            measures = np.array(measures)
            # mean_measures = np.mean(measures, axis=1)
            time_sum.append(measures)

        time_sum = np.array(time_sum)
        sum_mean = np.mean(np.sum(time_sum, axis=0), axis=1)
        # ax.axhline(y=np.mean(sum_mean) * 1000, color='r', linestyle='--')
        ax.plot(n_requests_config, sum_mean * 1000, c=next(colorcycler), label=f"{topology}-{graph}")
        # print(sum_mean)

ax.legend(loc='upper left', fontsize=8)

ax = ax3
ax.grid(ls=":")
ax.set_xlabel("# requests")
ax.set_yscale("log")

df = preprocessing_data
colorcycler = cycle(colors)

for topology, df in df.groupby("topology"):
    for graph, df in df.groupby("graph"):
        ax.set_title(f"Preprocessing Components Time ({topology}-{graph})")

        time_sum = []

        for fn_name, df in df.groupby("fn_name"):
            measures = []

            for n_requsts, df in df.groupby("n_requests"):
                measures.append(df["time"])

            measures = np.array(measures)
            mean_measures = np.mean(measures, axis=1)
            time_sum.append(measures)
            ax.plot(
                n_requests_config,
                medfilt(mean_measures * 1000, kernel_size=5),
                ls=next(linecycler),
                label=fn_name,
                c=next(colorcycler),
            )

        time_sum = np.array(time_sum)
        sum_mean = np.mean(np.sum(time_sum, axis=0), axis=1)
        # ax.axhline(y=np.mean(sum_mean) * 1000, color='r', linestyle='--')
        ax.plot(n_requests_config, sum_mean * 1000, color="k", ls="--", lw=2, label="Accumulated Components")

        break

    break

# Shrink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 1.1, box.height])

# Put a legend to the right of the current axis
ax.legend(loc='center left', bbox_to_anchor=(1.1, 0.47), fontsize=8)

plt.tight_layout()
plt.savefig(f"00_times.png")
plt.close()
plt.clf()
