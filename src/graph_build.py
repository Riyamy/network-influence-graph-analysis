"""
Build graph from an edge list CSV. Expected columns: source,target,weight,timestamp,interaction_type
Produces a NetworkX Graph and saves as gpickle for downstream analysis.
"""
import argparse
import pandas as pd
import networkx as nx
from tqdm import tqdm

def load_edges(path, chunksize=100000):
    for chunk in pd.read_csv(path, chunksize=chunksize):
        yield chunk

def build_graph(edge_csv, directed=False, weight_col='weight'):
    G = nx.DiGraph() if directed else nx.Graph()
    for chunk in load_edges(edge_csv):
        for _, row in chunk.iterrows():
            u = row['source']
            v = row['target']
            w = row.get(weight_col, 1) if 'weight' in row else 1
            if G.has_edge(u, v):
                G[u][v]['weight'] += w
            else:
                G.add_edge(u, v, weight=float(w))
    return G

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--directed', action='store_true')
    args = parser.parse_args()

    G = build_graph(args.input, directed=args.directed)
    nx.write_gpickle(G, args.output)
    print(f"Saved graph: {args.output} | nodes={G.number_of_nodes()} edges={G.number_of_edges()}")

if __name__ == '__main__':
    main()
