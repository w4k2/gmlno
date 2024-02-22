import networkx as nx
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

data_dir = 'data'

# name, nodes, request-sets
topologies = [
    ('euro28', 28, 100, 1000),
    ('us26', 26, 100, 1000),
]

for topology in topologies:
    topology_name, n_nodes, n_request_sets, n_demands = topology

    for request_set_id in range(n_request_sets):
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

        G = nx.MultiDiGraph()
        G.add_nodes_from(range(0, n_nodes))

        # górna granica z pliku results, albo definiujemy globalnie.
        for demand in demands[:]:
            src, dst, cat, requests = demand
            G.add_edge(src, dst, cat=cat, requests=requests)

        nx.draw_kamada_kawai(G)
        plt.savefig("foo.png")
        plt.close()
        plt.clf()

        density = nx.density(G)
        reciprocity = nx.reciprocity(G)
        average_node_connectivity = nx.average_node_connectivity(G)

        print(density)
        print(reciprocity)
        print(average_node_connectivity)

        exit()



