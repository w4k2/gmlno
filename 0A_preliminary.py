import pandas as pd
from sklearn.model_selection import RepeatedKFold

from sklearn.svm import SVR
from sklearn.neural_network import MLPRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.base import clone

import time

from sklearn.metrics import mean_absolute_error, r2_score
from tqdm import tqdm
from aobt import aobt
import os

topologies = ["euro28", "us26"]

representation = [
    "graph_raw_conn",
    "graph_stat_dg",
    "mean",
]

n_requests = [
    100,
    # 125, 150, 175,
    # 200, 225, 250, 275,
    300,  # 325, 350, 375,
    # 400, 425, 450, 475,
    500,  # 525, 550, 575,
    # 600, 625, 650,
]

metrics = [
    ("mae", mean_absolute_error),
    # ('r2', r2_score),
    # ('aobt', aobt),
]

targets = [
    "avg_transceivers",
    # "max_transceivers",
    # "sum_slots",
    # "avg_max_slot"
]

base_regrssors = [
    SVR(),
    MLPRegressor(max_iter=2000),
    DecisionTreeRegressor(),
    KNeighborsRegressor(),
]

# @ Janiszewskiego 7, Wrocław
rkf = RepeatedKFold(n_splits=5, n_repeats=2, random_state=50372)

results = []

n_components = (
    len(topologies)
    * len(representation)
    * len(n_requests)
    * len(targets)
    * len(base_regrssors)
    * rkf.get_n_splits()
)
p_bar = tqdm(range(n_components), desc="Progress")

for top in topologies:
    for rep in representation:
        for nr in n_requests:
            csv_path = os.path.join("datasets", top, f"{rep}-{nr}.csv")

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

                for base_reg in base_regrssors:
                    # each row is same request_set in csv
                    for split_idx, (train, test) in enumerate(rkf.split(X, y)):
                        p_bar.set_description("Training...")
                        model = clone(base_reg)

                        s_time = time.process_time()
                        model.fit(X[train], y[train])
                        fit_time = time.process_time() - s_time

                        scores[f"fit.time_{split_idx}"] = fit_time

                        s_time = time.process_time()
                        y_pred = model.predict(X[test])
                        pred_time = time.process_time() - s_time

                        scores[f"pred.time_{split_idx}"] = pred_time

                        p_bar.set_description("Storing...")

                        for metric, m_fn in metrics:
                            scores[f"{metric}_{split_idx}"] = m_fn(y[test], y_pred)

                        p_bar.update(1)

                    results.append({**config, "regressor": type(model).__name__ ,**scores})

results_df = pd.DataFrame(results)
results_df.to_csv("0A_preliminary_results.csv", index=False)
