

from src.data import generate_synthetic_graph
from src.graph_analysis import GraphAnalyzer

if __name__ == "__main__":
    G = generate_synthetic_graph(n_nodes=3000, n_edges=10000, seed=42)
    analyzer = GraphAnalyzer(G)
    analyzer.compute_communities()
    analyzer.compute_centralities(betweenness_k=200)
    print("Top 10 by degree:\n", analyzer.top_n_by_metric('degree', n=10))
