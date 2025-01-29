import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

n_requests_config = [
    100, 125, 150, 175,
    200, 225, 250, 275,
    300, 325, 350, 375,
    400, 425, 450, 475,
    500, 525, 550, 575,
    600, 625, 650,
]

data = pd.read_csv("00_times.csv")

fig, ax = plt.subplots(1, 1, figsize=(7, 7))


for topology, df in data.groupby("topology"):
    for graph, df in df.groupby("graph"):

        # ax.set_xticks(n_requests_config)

        data = []

        for fn_name, df in df.groupby("fn_name"):
            measures = []

            for n_requsts, df in df.groupby("n_requests"):
                measures.append(df["time"])

            # ax.plot(n_requests_config,measures, label=fn_name)
            data.append(measures)

        data = np.array(data)
        sum_data = np.sum(data, axis=0)

        ax.plot(n_requests_config, sum_data.mean(axis=-1) * 1000)

        print(sum_data.mean(axis=-1) * 1000)

# ax.set_yscale('log')
ax.grid(ls=':')
plt.tight_layout()
plt.savefig(f"time.png")
