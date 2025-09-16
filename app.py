import streamlit as st
from src.data import load_graph_from_csv, generate_synthetic_graph
from src.graph_analysis import GraphAnalyzer
from src.visualization import create_pyvis_network, plot_centralities_summary
import os
import time
import io
import zipfile

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Network Influence Analysis", layout="wide")
st.title("🌐 Network Influence Analysis — Graph Theory Dashboard")

# ------------------- DATA SOURCE -------------------
st.sidebar.header("📂 Data source")
data_source = st.sidebar.selectbox(
    "Choose", 
    ["Generate synthetic graph", "Upload edge CSV (source,target)"]
)

if data_source == "Generate synthetic graph":
    n = st.sidebar.number_input("Nodes", min_value=100, max_value=200000, value=1000, step=100)
    m = st.sidebar.number_input("Edges", min_value=100, max_value=1000000, value=3000, step=100)
    seed = st.sidebar.number_input("Random seed", min_value=0, value=42)
    
    if st.sidebar.button("Generate"):
        with st.spinner("🔄 Generating synthetic graph..."):
            G = generate_synthetic_graph(n_nodes=int(n), n_edges=int(m), seed=int(seed))
            st.session_state["graph"] = G
            st.success(f"✅ Generated graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

else:
    uploaded = st.sidebar.file_uploader("Upload CSV (two columns: source,target)", type=["csv"])
    if uploaded is not None:
        with st.spinner("📥 Loading CSV..."):
            G = load_graph_from_csv(uploaded)
            st.session_state["graph"] = G
            st.success(f"✅ Loaded graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# ------------------- RETRIEVE GRAPH -------------------
if "graph" not in st.session_state:
    st.info("👉 Choose a data source and generate or upload a CSV to begin.")
    st.stop()
else:
    G = st.session_state["graph"]

# ------------------- ANALYSIS OPTIONS -------------------
st.sidebar.header("⚙️ Analysis options")
method = st.sidebar.selectbox("Community method", ["louvain", "igraph_multilevel"])
approx_betw = st.sidebar.slider("Approximate betweenness: sample k nodes (0 = exact)", 0, 1000, 200)
max_vis_nodes = st.sidebar.number_input("Max nodes to visualize (PyVis)", min_value=100, max_value=5000, value=1000, step=100)

# ------------------- RUN ANALYSIS -------------------
if st.sidebar.button("🚀 Run analysis"):
    analyzer = GraphAnalyzer(G)

    # --- Community Detection ---
    with st.spinner("🧩 Computing communities..."):
        t0 = time.time()
        try:
            analyzer.compute_communities(method=method)
            n_comms = len(set(analyzer.partition.values()))
            st.success(f"✅ Community detection complete: {n_comms} communities found in {time.time()-t0:.1f}s")
        except Exception as e:
            st.error(f"❌ Community detection failed: {e}")
            analyzer.partition = None

    # --- Centralities ---
    with st.spinner("📊 Computing centralities..."):
        t0 = time.time()
        analyzer.compute_centralities(betweenness_k=(None if approx_betw == 0 else int(approx_betw)))
        st.success(f"✅ Centralities computed in {time.time()-t0:.1f}s")

    # Save results for download
    top_df = analyzer.top_n_by_metric('degree', n=20).set_index('node')
    comm_df = analyzer.community_sizes().head(30).set_index('community')
    centrality_df = analyzer.centrality_df

    # --- Tabs for results ---
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Influencers", "👥 Communities", "📊 Centralities", "🌐 Network"])

    # --- Influencers ---
    with tab1:
        st.subheader("🏆 Top Influencers (by Degree)")
        st.dataframe(top_df)
        st.download_button("📥 Download Influencers (CSV)", top_df.to_csv().encode('utf-8'), "top_influencers.csv", "text/csv")

    # --- Communities ---
    with tab2:
        st.subheader("👥 Community Sizes (Top 30)")
        st.bar_chart(comm_df)
        st.download_button("📥 Download Communities (CSV)", comm_df.to_csv().encode('utf-8'), "community_sizes.csv", "text/csv")

    # --- Centralities ---
    with tab3:
        st.subheader("📈 Centrality Metrics Distribution")
        fig = plot_centralities_summary(centrality_df)
        st.plotly_chart(fig, use_container_width=True)
        st.download_button("📥 Download Centralities (CSV)", centrality_df.to_csv(index=False).encode('utf-8'), "centralities.csv", "text/csv")

    # --- Interactive Network ---
    with tab4:
        st.subheader("🌐 Interactive Network (PyVis)")
        demo_dir = "demos"
        os.makedirs(demo_dir, exist_ok=True)
        net_path = os.path.join(demo_dir, "network.html")
        create_pyvis_network(G, analyzer.partition, output_path=net_path, max_nodes=int(max_vis_nodes))

        with open(net_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=600, scrolling=True)

        st.download_button("📥 Download Network (HTML)", html_content.encode('utf-8'), "network_visualization.html", "text/html")

    # ------------------- ZIP ALL RESULTS -------------------
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("top_influencers.csv", top_df.to_csv())
        zf.writestr("community_sizes.csv", comm_df.to_csv())
        zf.writestr("centralities.csv", centrality_df.to_csv(index=False))
        zf.writestr("network_visualization.html", html_content)
    buffer.seek(0)

    st.sidebar.download_button("📦 Download All Results (ZIP)", buffer, "network_analysis_results.zip", "application/zip")
