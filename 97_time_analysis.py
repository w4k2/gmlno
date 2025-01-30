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

data = pd.read_csv("00_times.csv")

# fig, ax = plt.subplots(1, 1, figsize=(7, 7))
# data = []

for topology, df in data.groupby("topology"):
    topology = topology.split("'")[1]
    for graph, df in df.groupby("graph"):

        fig_b, ax_b = plt.subplots(1, 1, figsize=(7, 7))

        cumul = []
        for fn_name, df in df.groupby("fn_name"):
            measures = []

            for n_requsts, df in df.groupby("n_requests"):
                measures.append(df["time"])

            measures = np.array(measures)
            mean_measures = np.mean(measures, axis=1)

            ax_b.plot(mean_measures * 1000, label=fn_name, ls=next(linecycler))
            cumul.append(measures)

            # print(fn_name)
            # print(np.mean(measures * 1000))


        ax_b.grid(ls=':')
        ax_b.set_yscale('log')
        ax_b.set_xlabel("n or equests")
        ax_b.set_ylabel("time [ms] (logscale)")
        ax_b.set_title("Preprocessing time")

        # Shrink current axis by 20%
        box = ax_b.get_position()
        ax_b.set_position([box.x0, box.y0, box.width * 0.8, box.height])

        # Put a legend to the right of the current axis
        ax_b.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        plt.tight_layout()
        plt.savefig(f"{topology}-{graph}-times.png")
        plt.close()
        plt.clf()

        cumul = np.array(cumul)
        sum_data = np.sum(cumul, axis=0)
        # ax.plot(n_requests_config, sum_data.mean(axis=-1) * 1000, label=f"{topology}-{graph}")

        # print(sum_data.mean(axis=-1) * 1000)

# ax.legend()
# ax.grid(ls=':')
# ax.set_xlabel("n or equests")
# ax.set_ylabel("time [ms]")
# ax.set_title("Preprocessing time")
# plt.figure(fig.nuber)
# plt.tight_layout()
# plt.savefig(f"times.png")
# plt.close()
# plt.clf()
