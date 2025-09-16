"""
Louvain community detection wrapper using python-louvain (community package).
"""
import community as community_louvain
import networkx as nx

def run_louvain(G, weight='weight', resolution=1.0):
    # convert to undirected weighted graph for Louvain
    if G.is_directed():
        U = G.to_undirected()
    else:
        U = G
    partition = community_louvain.best_partition(U, weight=weight, resolution=resolution)
    # partition: dict node -> community_id
    return partition

def summarize_partition(partition):
    from collections import Counter
    cnt = Counter(partition.values())
    sizes = sorted(cnt.items(), key=lambda x: -x[1])
    return sizes
