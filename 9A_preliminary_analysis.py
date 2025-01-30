import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

df = pd.read_csv("0A_results.csv")

n_splits = 10
topology = "euro28"
target="avg_transceivers"

metrics = [
    "mae",
    "fit.time",
    "pred.time"
]

regressors = [
    "SVR",
    "MLPRegressor",
    "DecisionTreeRegressor",
    "KNeighborsRegressor",
]

n_requests = [
    100, 300, 500
]

df = df[df['topology'] == topology]
df = df.drop('topology', axis=1)
df = df[df['target'] == target]
df = df.drop('target', axis=1)

for metric in metrics:
    mask = df.columns.str.contains(f'{metric}_*')
    columns = df.columns[mask].values
    std_name, mean_name = f"{metric}_std", f"{metric}_mean"
    mean_val = df.loc[:, mask].values.mean(axis=1)
    std_val = df.loc[:, mask].values.std(axis=1)
    df = df.drop(df.columns[mask].values, axis=1)
    if "time" in metric:
        mean_val *= 1000
        std_val *= 1000
    df[mean_name] = mean_val
    df[std_name] = std_val
    df[f"{metric}_str"] = df.apply(lambda x: f"{x[f'{mean_name}']:.2f} ({x[f'{std_name}']:.2f}) ", axis=1)
    df = df.drop([mean_name, std_name], axis=1)


# print(df.pivot(index=["representation, n_requests"], columns="mae_str"))

print(tabulate(df, tablefmt='grid', headers=df.columns))

