import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

DATASETS_DIR = "datasets"
TOPOLOGIES = ["euro28", "us26"]

METHODS = [
    "graph_stat_dg",
    "graph_stat_mdg",
]

for topology in TOPOLOGIES:
    for method in METHODS:
        df = pd.read_csv(os.path.join(DATASETS_DIR, topology, f"{method}-full.csv"))

        df = df.drop(columns=["set_id", "n_requests"])

        features = df.columns[:-4].values
        targets = df.columns[-4:].values

        corr = df.corr()

        corr = corr[:-4]

        # Generate a mask for the upper triangle
        mask = np.triu(np.ones_like(corr, dtype=bool))

        mask[:,-4:] = False

        # Set up the matplotlib figure
        f, ax = plt.subplots(figsize=(14 * 1.164, 14))

        # Generate a custom diverging colormap
        cmap = sns.diverging_palette(230, 20, as_cmap=True)

        # Draw the heatmap with the mask and correct aspect ratio
        plot = sns.heatmap(
            corr,
            mask=mask,
            cmap=cmap,
            vmax= 1.0,
            vmin=-1.0,
            center=0,
            square=True,
            linewidths=0.5,
            annot=True,
        )

        plt.tight_layout()
        plot.figure.savefig(os.path.join('correlation', f"{topology}-{method}.png"))
