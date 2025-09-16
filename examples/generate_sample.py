from src.data import generate_synthetic_graph
from src.graph_analysis import GraphAnalyzer
from src.visualization import create_pyvis_network
import os

if __name__ == "__main__":
    # small demo so it runs locally fast
    G = generate_synthetic_graph(n_nodes=2000, n_edges=8000, seed=123)
    analyzer = GraphAnalyzer(G)
    analyzer.compute_communities(method='louvain')
    analyzer.compute_centralities(betweenness_k=200)
    os.makedirs('demos', exist_ok=True)
    create_pyvis_network(G, analyzer.partition, output_path=os.path.join('demos', 'sample_network.html'), max_nodes=500)
    print("Demo created at demos/sample_network.html")
