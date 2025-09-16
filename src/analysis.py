"""
End-to-end analysis: loads graph, computes communities and centralities, writes summary CSVs.
"""
import argparse
import networkx as nx
import pandas as pd
from community_detection import run_louvain, summarize_partition
from centrality import degree_centrality, pagerank, betweenness_approx, eigenvector

def write_node_table(G, partition, centralities, outpath):
    data = []
    for node in G.nodes():
        row = {'node': node, 'community': partition.get(node, -1)}
        for k, d in centralities.items():
            row[k] = d.get(node, None)
        data.append(row)
    df = pd.DataFrame(data)
    df.to_csv(outpath, index=False)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--graph', required=True)
    parser.add_argument('--outdir', required=True)
    parser.add_argument('--pagerank_tol', type=float, default=1e-6)
    args = parser.parse_args()

    G = nx.read_gpickle(args.graph)

    print('Running Louvain...')
    partition = run_louvain(G)
    print('Partition sizes:', summarize_partition(partition)[:10])

    print('Computing centralities...')
    central = {}
    central['degree'] = degree_centrality(G)
    central['pagerank'] = pagerank(G, tol=args.pagerank_tol)
    central['betweenness'] = betweenness_approx(G, k=200)
    try:
        central['eigenvector'] = eigenvector(G)
    except Exception as e:
        print('Eigenvector failed', e)

    write_node_table(G, partition, central, f"{args.outdir}/node_metrics.csv")
    # export community-level summary
    import pandas as pd
    df = pd.read_csv(f"{args.outdir}/node_metrics.csv")
    comm_summary = df.groupby('community').agg({
        'node': 'count',
        'degree': 'mean',
        'pagerank': 'mean'
    }).rename(columns={'node': 'size'})
    comm_summary.to_csv(f"{args.outdir}/community_summary.csv")
    print('Analysis written to', args.outdir)

if __name__ == '__main__':
    main()
