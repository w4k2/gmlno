from collections import defaultdict
import os
import pandas as pd

DATASETS_DIR = 'datasets'
TOPOLOGIES = ['euro28', 'us26']

N_REQUESTS_CONFIG = [
    100, 125, 150, 175,
    200, 225, 250, 275,
    300, 325, 350, 375,
    400, 425, 450, 475,
    500, 525, 550, 575,
    600, 625, 650,
]

METHODS = [
    "graph_raw_conn",
    "graph_raw_mean",
    "graph_stat_dg",
    "graph_stat_mdg",
]

for topology in TOPOLOGIES:
    for method in METHODS:
        table = []

        for n_requests in N_REQUESTS_CONFIG:
            data = pd.read_csv(os.path.join(DATASETS_DIR, topology, f"{method}-{n_requests}.csv"))
            data["set_id"] = range(len(data))
            data["n_requests"] = n_requests

            table.append(data)

        table = pd.concat(table)
        table.to_csv(os.path.join(DATASETS_DIR, topology, f"{method}-full.csv"), index=False)
