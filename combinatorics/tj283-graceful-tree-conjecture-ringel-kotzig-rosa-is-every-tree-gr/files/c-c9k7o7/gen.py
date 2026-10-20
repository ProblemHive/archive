import sys
import networkx as nx
# writes one tree per line: n then parent array of a BFS order (vertex i>0 has parent p[i] < i)
n = int(sys.argv[1])
out = open(f"trees{n}.txt", "w")
cnt = 0
for T in nx.nonisomorphic_trees(n):
    # relabel in BFS order from vertex 0
    order = list(nx.bfs_tree(T, 0))
    idx = {v: i for i, v in enumerate(order)}
    par = [-1] * n
    for u, v in T.edges():
        a, b = idx[u], idx[v]
        if a > b:
            a, b = b, a
        par[b] = a
    out.write(" ".join(map(str, par[1:])) + "\n")
    cnt += 1
out.close()
print(n, cnt)
