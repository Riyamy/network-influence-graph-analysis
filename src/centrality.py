"""
Compute centrality measures with optional parallelization.
"""
import networkx as nx
from joblib import Parallel, delayed

def degree_centrality(G):
    return dict(G.degree(weight='weight'))

def pagerank(G, **kwargs):
    return nx.pagerank(G, weight='weight', **kwargs)

def betweenness_approx(G, k=100, seed=42):
    # approximate betweenness using k node samples
    return nx.betweenness_centrality(G, k=k, seed=seed, weight='weight')

def eigenvector(G, max_iter=100, tol=1e-06):
    try:
        return nx.eigenvector_centrality_numpy(G, weight='weight')
    except Exception:
        return nx.eigenvector_centrality(G, max_iter=max_iter, tol=tol, weight='weight')
