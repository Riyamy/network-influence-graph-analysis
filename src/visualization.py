from pyvis.network import Network
import networkx as nx
import plotly.express as px
import pandas as pd
import os

def create_pyvis_network(G, partition=None, output_path='network.html', notebook=False, max_nodes=1000):
    """
    Create interactive HTML using PyVis. If graph is large, sample top-degree nodes.
    Automatically disables notebook mode when saving to file.
    """
    # Downsample if too many nodes
    if G.number_of_nodes() > max_nodes:
        degrees = dict(G.degree())
        top_nodes = sorted(degrees, key=degrees.get, reverse=True)[:max_nodes]
        H = G.subgraph(top_nodes).copy()
    else:
        H = G

    # Force notebook=False when writing standalone HTML
    net = Network(height='750px', width='100%', notebook=False)

    # Add nodes
    for n in H.nodes():
        title = f"Node {n}"
        group = partition.get(n, 0) if partition else None
        net.add_node(int(n), label=str(n), title=title, group=group)

    # Add edges
    for u, v in H.edges():
        net.add_edge(int(u), int(v))

    # Ensure output folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save as HTML file
    net.write_html(output_path, notebook=False)
    print(f"✅ PyVis network saved at: {output_path}")

def plot_centralities_summary(df):
    """
    Plot distribution of centrality metrics using Plotly.
    """
    df2 = df.melt(
        id_vars='node',
        value_vars=['degree', 'betweenness', 'closeness', 'eigenvector'],
        var_name='metric',
        value_name='value'
    )
    fig = px.box(df2, x='metric', y='value', title='Centrality metrics distribution')
    return fig
