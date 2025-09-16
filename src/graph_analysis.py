import networkx as nx
import pandas as pd
from collections import Counter
import time

# try to import python-louvain (community) and igraph if available
try:
    import community as community_louvain
except Exception:
    community_louvain = None

try:
    import igraph as ig
except Exception:
    ig = None

class GraphAnalyzer:
    def __init__(self, G):
        self.G = G
        self.partition = None
        self.centrality_df = None

    def compute_communities(self, method='louvain'):
        if method == 'louvain':
            if community_louvain is None:
                raise ImportError("python-louvain (`community` package) is required for Louvain.")
            # partition: node -> community id
            self.partition = community_louvain.best_partition(self.G)
        elif method == 'igraph_multilevel':
            if ig is None:
                raise ImportError("python-igraph is required for igraph_multilevel.")
            # convert to igraph, run multilevel community detection
            mapping = {n: i for i, n in enumerate(self.G.nodes())}
            edges = [(mapping[u], mapping[v]) for u, v in self.G.edges()]
            g_igraph = ig.Graph(edges=edges, directed=False)
            parts = g_igraph.community_multilevel()
            # build partition dict back to original node keys
            membership = parts.membership
            inv_map = {i: n for n, i in mapping.items()}
            self.partition = {inv_map[i]: membership[i] for i in range(len(membership))}
        else:
            raise ValueError("Unsupported community detection method")

    def compute_centralities(self, betweenness_k=None):
        G = self.G
        # degree
        deg = dict(G.degree())
        # betweenness: approximate if k provided (samples k nodes)
        if betweenness_k is None:
            try:
                bc = nx.betweenness_centrality(G)
            except Exception:
                bc = {n: 0.0 for n in G.nodes()}
        else:
            n = G.number_of_nodes()
            k = min(int(betweenness_k), n-1)
            if k <= 0 or k >= n:
                try:
                    bc = nx.betweenness_centrality(G)
                except Exception:
                    bc = {n: 0.0 for n in G.nodes()}
            else:
                try:
                    bc = nx.betweenness_centrality(G, k=k, seed=42)
                except TypeError:
                    # older networkx versions might not accept seed
                    bc = nx.betweenness_centrality(G, k=k)
        # closeness
        try:
            cc = nx.closeness_centrality(G)
        except Exception:
            cc = {n: 0.0 for n in G.nodes()}
        # eigenvector (may fail for large disconnected graphs)
        try:
            ev = nx.eigenvector_centrality_numpy(G)
        except Exception:
            ev = {n: 0.0 for n in G.nodes()}

        df = pd.DataFrame({
            'node': list(G.nodes()),
            'degree': [deg.get(n, 0) for n in G.nodes()],
            'betweenness': [bc.get(n, 0.0) for n in G.nodes()],
            'closeness': [cc.get(n, 0.0) for n in G.nodes()],
            'eigenvector': [ev.get(n, 0.0) for n in G.nodes()],
        })
        if self.partition is not None:
            df['community'] = df['node'].map(self.partition)
        self.centrality_df = df.sort_values('degree', ascending=False).reset_index(drop=True)

    def top_n_by_metric(self, metric='degree', n=10):
        if self.centrality_df is None:
            self.compute_centralities()
        return self.centrality_df[['node', metric]].head(n)

    def community_sizes(self):
        if self.partition is None:
            return pd.DataFrame(columns=['community', 'size'])
        counts = Counter(self.partition.values())
        items = [{'community': k, 'size': v} for k, v in counts.items()]
        return pd.DataFrame(items).sort_values('size', ascending=False).reset_index(drop=True)
