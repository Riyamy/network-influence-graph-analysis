import networkx as nx
import pandas as pd
import numpy as np

def generate_synthetic_graph(n_nodes=10000, n_edges=150000, seed=None):
    """
    Generate an undirected synthetic graph.
    For scale-free social-like graphs, Barabasi-Albert is used for realism.
    If you need exact edge count, we fall back to gnm_random_graph.
    """
    rng = np.random.RandomState(seed)
    # use Barabasi-Albert if feasible
    try:
        # choose m parameter (edges to attach) roughly edges/n_nodes
        m_param = max(1, int(n_edges // n_nodes))
        G = nx.barabasi_albert_graph(n_nodes, m_param, seed=seed)
        # If edges are far from desired, patch by adding random edges
        if G.number_of_edges() < n_edges:
            extra = int(n_edges - G.number_of_edges())
            nodes = list(G.nodes())
            while extra > 0:
                u, v = rng.choice(nodes), rng.choice(nodes)
                if u != v and not G.has_edge(u, v):
                    G.add_edge(u, v)
                    extra -= 1
    except Exception:
        # fallback to G(n, m)
        max_edges = n_nodes*(n_nodes-1)//2
        m = min(n_edges, max_edges)
        G = nx.gnm_random_graph(n_nodes, m, seed=seed)
    # add small labels
    nx.set_node_attributes(G, {n: str(n) for n in G.nodes()}, name='label')
    return G

def load_graph_from_csv(path_or_buffer, source_col=None, target_col=None):
    """
    Load edge list CSV into NetworkX Graph.
    Expects two columns; can accept file path or file-like object (Streamlit uploader).
    """
    df = pd.read_csv(path_or_buffer)
    if df.shape[1] < 2:
        raise ValueError("CSV must contain at least two columns for edges.")
    if source_col is None or target_col is None:
        u, v = df.columns[0], df.columns[1]
    else:
        u, v = source_col, target_col
    G = nx.from_pandas_edgelist(df, u, v)
    return G
