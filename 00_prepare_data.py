import networkx as nx
import numpy as np
import os
import pandas as pd
from PIL import Image
from tqdm import tqdm
from collections import defaultdict
import time

DATA_DIR = "data"
DEMANDS_IN_REQUEST_SET = 1000

TARGETS = ["avg_transceivers", "max_transceivers", "sum_slots", "avg_max_slot"]

timeit_storage = []

def timeit(fn, meta, *args, **kw_args):
    s_time = time.process_time()
    ret = fn(*args, **kw_args)
    fn_time = time.process_time() - s_time
    print(fn_time)
    timeit_storage.append({"fn_name": fn.__name__, **meta, "time": fn_time})
    return ret

# topology_name, n_nodes, n_request_sets
topologies = [
    ("euro28", 28, 100),
    ("us26", 26, 100),
]

n_requests_config = [
    100, 125, 150, 175,
    200, 225, 250, 275,
    300, 325, 350, 375,
    400, 425, 450, 475,
    500, 525, 550, 575,
    600, 625, 650,
]

stat_functions = [np.mean, np.std, np.median, np.var, np.min, np.max, np.sum]
stat_functions_name = [fn.__name__ for fn in stat_functions]

graph_functions = [
    nx.average_node_connectivity,
    nx.degree_assortativity_coefficient,
    nx.degree_pearson_correlation_coefficient,
    nx.density,
    nx.edge_connectivity,
    nx.flow_hierarchy,
    nx.global_reaching_centrality,
    nx.is_aperiodic,
    nx.is_attracting_component,
    nx.is_semiconnected,
    nx.is_strongly_connected,
    nx.node_connectivity,
    nx.number_attracting_components,
    nx.number_of_edges,
    nx.number_strongly_connected_components,
    nx.overall_reciprocity,
    nx.reciprocity,
    nx.s_metric,
]

graph_functions_name = [fn.__name__ for fn in graph_functions]

def img_from_array(arr):
    return Image.fromarray(np.uint8(arr * 255.0 / arr.max()))


def parse_demands_file(file_path):
    with open(file_path, "r") as fp:
        line = fp.readline()
        if line.startswith("#"):
            line = fp.readline()
        src = int(line.rstrip())
        dst = int(fp.readline().rstrip())
        cat = fp.readline().rstrip()
        requests = np.asarray([line.rstrip() for line in fp]).astype(float)

    return src, dst, cat, requests


for topology in topologies:
    topology_name, n_nodes, n_request_sets = topology

    raw_tables = defaultdict(list)
    stat_tables = defaultdict(lambda: defaultdict(list))
    graph_raw_conn_tables = defaultdict(list)
    graph_raw_mean_tables = defaultdict(list)
    graph_mdg_stats_tables = defaultdict(list)
    graph_dg_stats_tables = defaultdict(list)

    for request_set_id in tqdm(range(n_request_sets), desc=topology_name):
        request_set_path = os.path.join(
            DATA_DIR, topology_name, f"request-set-{request_set_id}"
        )

        results = pd.read_csv(
            os.path.join(request_set_path, "results.csv"), index_col=0
        )

        demands_path = os.path.join(request_set_path, f"demands_{request_set_id}")
        demands = [
            parse_demands_file(os.path.join(demands_path, f"{i}.txt"))
            for i in range(DEMANDS_IN_REQUEST_SET)
        ]

        demands_raw = np.stack([demand[-1] for demand in demands], axis=0)

        for n_requests in n_requests_config:
            timeit_meta = {
                "topology": topology_name,
                "request_id": request_set_id,
                "n_requests": n_requests
            }

            # raw_tables[n_requests].append([*demands_raw[:n_requests].ravel(), *results.loc[n_requests][TARGETS]])

            # Stat Features
            demands_stats = np.stack(
                [fn(demands_raw[:n_requests], axis=1) for fn in stat_functions], axis=1
            )

            for stat_i, stat_name in enumerate(stat_functions_name):
                stat_tables[n_requests][stat_name].append([*demands_stats[:, stat_i].ravel(), *results.loc[n_requests][TARGETS]])

            s_time = time.process_time()
            mdg = nx.MultiDiGraph()
            mdg.add_nodes_from(range(0, n_nodes))
            mdg.add_edges_from(
                [
                    (src, dst, dict(zip(stat_functions_name, stats)))
                    for (src, dst, _, _), stats in zip(
                        demands[:n_requests], demands_stats[:n_requests]
                    )
                ]
            )

            graph_raw_conn = nx.to_numpy_array(mdg)
            graph_raw_conn_tables[n_requests].append([*graph_raw_conn.ravel(), *results.loc[n_requests][TARGETS]])

            graph_raw_weighted = nx.to_numpy_array(mdg, weight="mean")
            graph_raw_mean_tables[n_requests].append([*graph_raw_weighted.ravel(), *results.loc[n_requests][TARGETS]])

            graph_mdg_stats_tables[n_requests].append([*[timeit(fn,{**timeit_meta, "graph": "mdg"}, mdg) for fn in graph_functions], *results.loc[n_requests][TARGETS]])

            dg = nx.DiGraph(graph_raw_weighted)
            graph_dg_stats_tables[n_requests].append([*[timeit(fn,{**timeit_meta, "graph": "dg"}, dg) for fn in graph_functions], *results.loc[n_requests][TARGETS]])

        # # Make demands image
        # img = img_from_array(demands_raw)
        # img.save(
        #     os.path.join(
        #         "images", "demands", f"{topology_name}-{request_set_id:03}.png"
        #     )
        # )

    # Store Tables
    datasets_dir = os.path.join("datasets", topology_name)

    for n_requests in n_requests_config:
        # table = pd.DataFrame(raw_tables[n_requests])
        # n_features = table.shape[1] - len(TARGETS)
        # table.to_csv(os.path.join(datasets_dir, f"raw-{n_requests}.csv"), index=False, header=[*range(n_features), *TARGETS])

        for stat in stat_functions_name:
            table = pd.DataFrame(stat_tables[n_requests][stat])
            table.to_csv(os.path.join(datasets_dir, f"{stat}-{n_requests}.csv"), index=False, header=[*range(n_requests), *TARGETS])

        table = pd.DataFrame(graph_raw_conn_tables[n_requests])
        n_features = n_nodes * n_nodes
        table.to_csv(os.path.join(datasets_dir, f"graph_raw_conn-{n_requests}.csv"), index=False, header=[*range(n_features), *TARGETS])

        table = pd.DataFrame(graph_raw_mean_tables[n_requests])
        n_features = n_nodes * n_nodes
        table.to_csv(os.path.join(datasets_dir, f"graph_raw_mean-{n_requests}.csv"), index=False, header=[*range(n_features), *TARGETS])

        table = pd.DataFrame(graph_mdg_stats_tables[n_requests])
        n_features = len(graph_functions)
        table.to_csv(os.path.join(datasets_dir, f"graph_stat_mdg-{n_requests}.csv"), index=False, header=[*graph_functions_name, *TARGETS])

        table = pd.DataFrame(graph_dg_stats_tables[n_requests])
        n_features = len(graph_functions)
        table.to_csv(os.path.join(datasets_dir, f"graph_stat_dg-{n_requests}.csv"), index=False, header=[*graph_functions_name, *TARGETS])


df = pd.DataFrame(timeit_storage)
df.to_csv("00_times.csv")