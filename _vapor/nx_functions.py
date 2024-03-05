import networkx as nx
import numpy as np
import numbers
import matplotlib.pyplot as plt

from inspect import getmembers

rs = np.random.RandomState(50210)

G = nx.MultiDiGraph()
G.add_nodes_from(range(0, 10))
G.add_weighted_edges_from([(a, b, c) for (a, b), c in zip(rs.randint(0, 10, size=(10, 2)), rs.rand(10))])

nx.draw_kamada_kawai(G)
plt.savefig("foo.png")
plt.close()
plt.clf()

for fn in getmembers(nx):
    # print(fn[0])

    try:
        ret = fn[1](G)
    except Exception as e:
        # print(":", e)
        pass
    else:
        if isinstance(ret, numbers.Number):
        # if isinstance(ret, list):
            print(fn[0])
            # print('+', ret)
        else:
            # print("- It is complicated")
            pass