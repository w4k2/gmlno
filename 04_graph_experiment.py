import pandas as pd
from sklearn.model_selection import RepeatedKFold

from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor

from sklearn.metrics import mean_absolute_error, r2_score
from tqdm import tqdm
from aobt import aobt

import os

topologies = ["euro28", "us26"]

representation = [
    "graph_raw_conn",
    "graph_raw_mean",
    "graph_stat_dg",
    "graph_stat_mdg",
]

metrics = [
    ('mae', mean_absolute_error),
    ('r2', r2_score),
    ('aobt', aobt),
]

targets = ["avg_transceivers", "max_transceivers", "sum_slots", "avg_max_slot"]

# @ Janiszewskiego 7, Wrocław
rkf = RepeatedKFold(n_splits=5, n_repeats=5, random_state=50372)

results = []

n_components = len(topologies) * len(representation) * len(targets) * rkf.get_n_splits()
p_bar = tqdm(range(n_components), desc="Progress")

for top in topologies:
    for rep in representation:
        csv_path = os.path.join('datasets', top, f"{rep}-full.csv")

        # if not os.path.exists(csv_path):
        #     print(f"File {csv_path} does not exist")
        #     continue

        data = pd.read_csv(csv_path)

        # Won't be used -- for more sophisticated protocols only
        data = data.drop(columns=["set_id", "n_requests"])
        data = data.values

        # Last 4 are targets
        X = data[:, :-4]
        y_ = data[:, -4:]

        for target_i, target in enumerate(targets):
            config = {
                "topology": top,
                "representation": rep,
                "target": target,
            }

            y = y_[:, target_i]
            scores = {}

            # each row is same request_set in csv
            for split_idx, (train, test) in enumerate(rkf.split(X, y)):
                model = DecisionTreeRegressor()
                model.fit(X[train], y[train])
                y_pred = model.predict(X[test])

                for metric, m_fn in metrics:
                    scores[f"{metric}_{split_idx}"] = m_fn(y[test], y_pred)

                p_bar.update(1)

            results.append({**config, **scores})

results_df = pd.DataFrame(results)
results_df.to_csv("04_graph_results.csv", index=False)
