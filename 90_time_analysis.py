import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

from itertools import cycle
lines = ["-","--",":"]
linecycler = cycle(lines)

n_requests_config = [
    100, 125, 150, 175,
    200, 225, 250, 275,
    300, 325, 350, 375,
    400, 425, 450, 475,
    500, 525, 550, 575,
    600, 625, 650,
]

preprocessing_data = pd.read_csv("00_times.csv")
us_data = pd.read_csv("00_timestable_us.csv", index_col=0)
euro_data = pd.read_csv("00_timestable_euro.csv", index_col=0)

simulation = {
    "us26": us_data, "euro28": euro_data
}

# fig, ax = plt.subplots(1, 1, figsize=(7, 7))
# data = []
df = preprocessing_data


fig, axs = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
axs[0].set_ylabel("time [ms]")
axs_i = iter(axs)

ax = axs[0]
ax.grid(ls=':')
ax.set_xlabel("n or equests")

for topology in simulation:
    sim_curve = np.array(simulation[topology])
    sim_curve_mean = np.mean(sim_curve, axis=0)
    # ax.axhline(y=np.mean(sim_curve), color='k', linestyle='--')
    ax.plot(n_requests_config, sim_curve_mean)


ax = axs[1]

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
        ax.plot(n_requests_config, sum_mean * 1000)
        print(sum_mean)

ax.grid(ls=':')
ax.set_xlabel("n or equests")
ax.set_title(f"{topology}")
# ax.set_yscale('log')

plt.tight_layout()
plt.savefig(f"00_{topology}-times.png")
plt.close()
plt.clf()