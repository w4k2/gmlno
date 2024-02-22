import networkx as nx
import numpy as np
import numbers
import matplotlib.pyplot as plt

from inspect import getmembers

rs = np.random.RandomState(50210)

G = nx.MultiDiGraph()
G.add_nodes_from(range(0, 10))
# weights = rs.random(20)
# nx.set_edge_attributes(G, values = weights, name = 'weight')

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
            print(fn[0])
            # print('+', ret)
        else:
            # print("- It is complicated")
            pass