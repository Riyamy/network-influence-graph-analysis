"""
A Streamlit dashboard to visualize communities and top influencers using pyvis for network preview.
Run with: streamlit run src/dashboard_streamlit.py -- --graph outputs/graph.gpickle
"""
import streamlit as st
import networkx as nx
import pandas as pd
from pyvis.network import Network
import tempfile

@st.cache_data
def load_graph(path):
    return nx.read_gpickle(path)

def make_pyvis(G, partition, top_n=100):
    net = Network(height='700px', width='100%', notebook=False)
    # choose top_n nodes by degree
    deg = dict(G.degree(weight='weight'))
    nodes_sorted = sorted(deg.items(), key=lambda x: -x[1])[:top_n]
    nodes_set = set(n for n, _ in nodes_sorted)
    for n in nodes_set:
        net.add_node(n, label=str(n), title=str(n), group=partition.get(n, -1))
    for u, v, d in G.edges(data=True):
        if u in nodes_set and v in nodes_set:
            net.add_edge(u, v, value=d.get('weight', 1))
    net.force_atlas_2based()
    return net

def main():
    st.title('Network Influence Analysis')
    st.sidebar.header('Settings')
    graph_path = st.sidebar.text_input('Graph gpickle path', 'outputs/graph.gpickle')
    if st.sidebar.button('Load'):
        G = load_graph(graph_path)
        st.sidebar.success(f'Loaded graph: nodes={G.number_of_nodes()} edges={G.number_of_edges()}')
        # try to load node metrics
        try:
            df = pd.read_csv('outputs/node_metrics.csv')
        except Exception:
            df = None

        # Try to load partition from node metrics
        partition = {}
        if df is not None and 'community' in df.columns:
            partition = pd.Series(df.community.values,index=df.node.values).to_dict()

        st.subheader('Top influencers (by PageRank)')
        if df is not None and 'pagerank' in df.columns:
            top = df.sort_values('pagerank', ascending=False).head(20)
            st.table(top[['node','community','pagerank','degree']])

        st.subheader('Network preview (pyvis)')
        net = make_pyvis(G, partition)
        path = tempfile.NamedTemporaryFile(delete=False, suffix='.html').name
        net.save_graph(path)
        st.components.v1.html(open(path, 'r', encoding='utf-8').read(), height=700)

if __name__ == '__main__':
    main()
