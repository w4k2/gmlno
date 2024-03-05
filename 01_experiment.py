import pandas as pd
from sklearn.model_selection import RepeatedKFold

from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor

from sklearn.metrics import mean_squared_error, r2_score
from tqdm import tqdm
from aobt import aobt
import os

topologies = ["euro28", "us26"]

representation = [
    "graph_raw_conn",
    "graph_raw_mean",
    "graph_stat_dg",
    "graph_stat_mdg",
    "max",
    "mean",
    "median",
    "min",
    "std",
    "sum",
    "var",
]

n_requests = [
    100,
    125, 150, 175,
    200, 225, 250, 275,
    300, 325, 350, 375,
    400, 425, 450, 475,
    500, 525, 550, 575,
    600, 625, 650,
]

metrics = [
    ('mse', mean_squared_error),
    ('r2', r2_score),
    ('aobt', aobt),
]

targets = ["avg_transceivers", "max_transceivers", "sum_slots", "avg_max_slot"]

# @ Janiszewskiego 7, Wrocław
rkf = RepeatedKFold(n_splits=5, n_repeats=5, random_state=50372)

results = []

n_components = len(topologies) * len(representation) * len(n_requests) * len(metrics) * rkf.get_n_splits()
p_bar = tqdm(range(n_components), desc="Progress")

for top in topologies:
    for rep in representation:
        for nr in n_requests:
            csv_path = os.path.join('datasets', top, f"{rep}-{nr}.csv")

            # if not os.path.exists(csv_path):
            #     print(f"File {csv_path} does not exist")
            #     continue

            data = pd.read_csv(csv_path).values

            # Last 4 are targets
            X = data[:, :-4]
            y_ = data[:, -4:]

            for target_i, target in enumerate(targets):
                config = {
                    "topology": top,
                    "representation": rep,
                    "n_requests": nr,
                    "target": target,
                }

                y = y_[:, target_i]
                scores = {}

                # each row is same request_set in csv
                for split_idx, (train, test) in enumerate(rkf.split(X, y)):
                    p_bar.set_description("Training...")
                    model = DecisionTreeRegressor()
                    model.fit(X[train], y[train])
                    y_pred = model.predict(X[test])

                    p_bar.set_description("Storing...")

                    for metric, m_fn in metrics:
                        scores[f"{metric}_{split_idx}"] = m_fn(y[test], y_pred)

                    p_bar.update(1)

                results.append({**config, **scores})

results_df = pd.DataFrame(results)
results_df.to_csv("01_experiment_results.csv", index=False)
