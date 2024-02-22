import networkx as nx
import numpy as np
import pandas as pd
import os
from tqdm import tqdm

data_dir = 'data'

functions = [
    ("average_node_connectivity", nx.average_node_connectivity),
    ("degree_assortativity_coefficient", nx.degree_assortativity_coefficient),
    ("degree_pearson_correlation_coefficient", nx.degree_pearson_correlation_coefficient),
    ("density", nx.density),
    ("edge_connectivity", nx.edge_connectivity),
    ("flow_hierarchy", nx.flow_hierarchy),
    ("global_reaching_centrality", nx.global_reaching_centrality),
    ("is_aperiodic", nx.is_aperiodic),
    ("is_attracting_component", nx.is_attracting_component),
    ("is_multigraphical", nx.is_multigraphical),
    ("is_pseudographical", nx.is_pseudographical),
    ("is_semiconnected", nx.is_semiconnected),
    ("is_strongly_connected", nx.is_strongly_connected),
    ("is_weakly_connected", nx.is_weakly_connected),
    ("node_connectivity", nx.node_connectivity),
    ("number_attracting_components", nx.number_attracting_components),
    ("number_of_edges", nx.number_of_edges),
    ("number_of_isolates", nx.number_of_isolates),
    ("number_of_nodes", nx.number_of_nodes),
    ("number_strongly_connected_components", nx.number_strongly_connected_components),
    ("number_weakly_connected_components", nx.number_weakly_connected_components),
    ("overall_reciprocity", nx.overall_reciprocity),
    ("reciprocity", nx.reciprocity),
    ("s_metric", nx.s_metric),
    ("wiener_index", nx.wiener_index),
]

# name, nodes, request-sets
topologies = [
    ('euro28', 28, 100, 1000),
    ('us26', 26, 100, 1000),
]

rows = []

for topology in topologies:
    topology_name, n_nodes, n_request_sets, n_demands = topology

    for request_set_id in tqdm(range(n_request_sets)):
        request_set_path = os.path.join(data_dir, topology_name, f"request-set-{request_set_id}")
        demands_path = os.path.join(request_set_path, f"demands_{request_set_id}")

        demands = []
        for i in range(n_demands):
            with open(os.path.join(demands_path, f"{i}.txt"), 'r') as fp:
                line = fp.readline()
                if line.startswith('#'):
                    line = fp.readline()

                src = int(line.rstrip())
                dst = int(fp.readline().rstrip())
                cat = fp.readline().rstrip()
                requests = np.asarray([line.rstrip() for line in fp]).astype(float)

            demands.append((src, dst, cat, requests))

        results = pd.read_csv(os.path.join(request_set_path, 'results.csv'))

        for r in tqdm(results.iterrows(), total=23, leave=False):
            request_set_features = r[1].to_dict()

            G = nx.MultiDiGraph()
            G.add_nodes_from(range(0, n_nodes))

            # górna granica z pliku results, albo definiujemy globalnie.
            for demand in demands[:int(request_set_features["n_requests"])]:
                src, dst, cat, requests = demand
                G.add_edge(src, dst, cat=cat, requests=requests)

            graph_features = {}

            for fn_name, fn in functions:
                graph_features[fn_name] = fn(G)

            row = {
                **{"topology": topology_name},
                **request_set_features,
                **graph_features
            }
            rows.append(row)

df = pd.DataFrame(rows)
df.to_csv('data.csv', index=False)




