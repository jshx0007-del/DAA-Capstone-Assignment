"""
app.py
Mini-Courier Planner — Streamlit Web Application
An interactive, beginner-friendly UI demonstrating algorithmic optimization in courier logistics.
"""

import os
import json
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from models.parcel import Parcel
from models.delivery_graph import DeliveryGraph
from algorithms.sorting import sort_parcels_with_metrics
from algorithms.knapsack import knapsack_01
from algorithms.dijkstra import dijkstra_shortest_paths
from algorithms.tsp import solve_tsp_nearest_neighbor
from visualization.graph_visualizer import plot_delivery_network
from algorithms.performance import run_benchmarks


# Set Page Configuration
st.set_page_config(
    page_title="Mini-Courier Planner | DAA Capstone",
    page_icon="🚚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean academic/professional look
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border-left: 5px solid #2563EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .algo-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #DBEAFE;
        color: #1E40AF;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_base_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(base_dir, "data", "parcels.json"), "r") as f:
        p_data = json.load(f)
    with open(os.path.join(base_dir, "data", "graph.json"), "r") as f:
        g_data = json.load(f)
    return p_data, g_data


p_raw, g_raw = load_base_data()

# Initialize Session State
if "parcels" not in st.session_state:
    st.session_state.parcels = [Parcel.from_dict(p) for p in p_raw]

if "graph" not in st.session_state:
    st.session_state.graph = DeliveryGraph.from_dict(g_raw)
    st.session_state.warehouse = g_raw.get("warehouse", "Central Warehouse")


# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/fluency/96/delivery.png", width=70)
st.sidebar.title("Mini-Courier Planner")
st.sidebar.caption("DAA Capstone Project (ETCCDA302)\nK.R. Mangalam University")

menu_choice = st.sidebar.radio(
    "Navigation Modules",
    [
        "🏠 Dashboard",
        "📦 Parcel Management",
        "⚡ Parcel Prioritization (Merge Sort)",
        "🎒 Packing Optimization (0/1 Knapsack)",
        "🗺️ Delivery Road Graph",
        "📍 Shortest Paths (Dijkstra)",
        "🚚 Route Optimization (TSP)",
        "📊 Performance Analysis",
        "ℹ️ Project Information & Viva Notes"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **Core Principles:**\n"
    "• Merge Sort: O(n log n)\n"
    "• 0/1 Knapsack: O(n·W)\n"
    "• Dijkstra: O((V+E) log V)\n"
    "• Nearest Neighbor: O(k²)"
)

# -------------------------------------------------------------
# 1. DASHBOARD
# -------------------------------------------------------------
if menu_choice == "🏠 Dashboard":
    st.markdown('<div class="main-title">Mini-Courier Planner Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Intelligent Parcel Prioritization, Vehicle Packing Optimization & Delivery Route Planning</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Parcels", len(st.session_state.parcels))
    with col2:
        total_wt = sum(p.weight for p in st.session_state.parcels)
        st.metric("Total Pending Weight", f"{total_wt} kg")
    with col3:
        st.metric("Delivery Locations", len(st.session_state.graph.get_nodes()))
    with col4:
        st.metric("Central Depot", st.session_state.warehouse)

    st.markdown("---")
    st.subheader("System Workflow Pipeline")
    st.markdown("""
    ```mermaid
    flowchart LR
        A[Parcel Intake] --> B[Priority Sorting\nMerge Sort: O n log n]
        B --> C[Vehicle Packing\n0/1 Knapsack DP: O nW]
        C --> D[Shortest Paths\nDijkstra Heap: O V+E log V]
        D --> E[Delivery Tour\nNearest Neighbor TSP: O k²]
        E --> F[Execution & Delivery]
    ```
    """)

    st.subheader("Current Parcel Overview")
    df_parcels = pd.DataFrame([p.to_dict() for p in st.session_state.parcels])
    st.dataframe(df_parcels, use_container_width=True)


# -------------------------------------------------------------
# 2. PARCEL MANAGEMENT
# -------------------------------------------------------------
elif menu_choice == "📦 Parcel Management":
    st.markdown('<div class="main-title">📦 Parcel Management Module</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">View existing parcels, inspect package properties, or insert new consignments.</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📋 View & Filter Parcels", "➕ Add Sample Parcel"])

    with tab1:
        df_p = pd.DataFrame([p.to_dict() for p in st.session_state.parcels])
        loc_filter = st.multiselect("Filter by Destination Location", options=list(df_p["delivery_location"].unique()))
        if loc_filter:
            df_p = df_p[df_p["delivery_location"].isin(loc_filter)]
        st.dataframe(df_p, use_container_width=True)

    with tab2:
        with st.form("add_parcel_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_id = st.text_input("Parcel ID", f"P{len(st.session_state.parcels) + 101}")
                cust_name = st.text_input("Customer Name", "Rajesh Khanna")
                deliv_loc = st.selectbox("Delivery Location", options=st.session_state.graph.get_nodes())
            with c2:
                wt = st.number_input("Weight (kg)", min_value=1, max_value=50, value=5)
                prio = st.slider("Priority Rank (1 = Low, 10 = Urgent)", 1, 10, 8)
                dline = st.number_input("Delivery Deadline (hours)", min_value=1, max_value=24, value=2)
                val = st.number_input("Consignment Value (₹)", min_value=10.0, max_value=10000.0, value=1250.0)

            submitted = st.form_submit_button("Add Parcel to System")
            if submitted:
                new_parcel = Parcel(new_id, cust_name, deliv_loc, int(wt), int(prio), int(dline), float(val))
                st.session_state.parcels.append(new_parcel)
                st.success(f"Parcel {new_id} added successfully!")
                st.rerun()


# -------------------------------------------------------------
# 3. PARCEL PRIORITIZATION (MERGE SORT)
# -------------------------------------------------------------
elif menu_choice == "⚡ Parcel Prioritization (Merge Sort)":
    st.markdown('<div class="main-title">⚡ Parcel Prioritization</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Multi-level sorting using manual Merge Sort with O(n log n) time complexity.</div>', unsafe_allow_html=True)

    st.info("""
    **Sorting Precedence Order:**
    1. **Priority Rank** (Descending): Higher priority consignments serviced first.
    2. **Delivery Deadline** (Ascending): Earlier deadlines take precedence when priorities match.
    3. **Parcel ID** (Ascending): Consistent deterministic tie-breaker.
    """)

    col_btn, col_stats = st.columns([1, 3])
    with col_btn:
        run_sort = st.button("Run Merge Sort", type="primary")

    sorted_list, sort_time = sort_parcels_with_metrics(st.session_state.parcels)

    if run_sort:
        st.success(f"Sorted {len(st.session_state.parcels)} parcels in {sort_time * 1000:.4f} ms!")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Original Unsorted Order")
        st.dataframe(pd.DataFrame([p.to_dict() for p in st.session_state.parcels]), use_container_width=True)
    with c2:
        st.subheader("Prioritized Order (Merge Sort)")
        st.dataframe(pd.DataFrame([p.to_dict() for p in sorted_list]), use_container_width=True)


# -------------------------------------------------------------
# 4. PACKING OPTIMIZATION (0/1 KNAPSACK)
# -------------------------------------------------------------
elif menu_choice == "🎒 Packing Optimization (0/1 Knapsack)":
    st.markdown('<div class="main-title">🎒 Vehicle Packing Optimization</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Manual 0/1 Knapsack Dynamic Programming with 2D DP Table.</div>', unsafe_allow_html=True)

    sorted_parcels, _ = sort_parcels_with_metrics(st.session_state.parcels)

    capacity = st.slider("Select Delivery Vehicle Capacity (kg)", min_value=10, max_value=100, value=35, step=5)

    knap_result = knapsack_01(sorted_parcels, capacity=capacity)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Packed Weight", f"{knap_result.total_weight} / {capacity} kg")
    with m2:
        st.metric("Total Consignment Value", f"₹{knap_result.total_value:.2f}")
    with m3:
        st.metric("Remaining Capacity", f"{knap_result.remaining_capacity} kg")
    with m4:
        st.metric("Computation Time", f"{knap_result.execution_time * 1000:.3f} ms")

    st.subheader(f"Optimally Selected Parcels for Trip ({len(knap_result.selected_parcels)} items)")
    if knap_result.selected_parcels:
        st.dataframe(pd.DataFrame([p.to_dict() for p in knap_result.selected_parcels]), use_container_width=True)
    else:
        st.warning("No parcels fit within the selected vehicle capacity.")

    with st.expander("🔍 View Dynamic Programming Table (First 15 Rows & Columns)"):
        st.caption("Table entry dp[i][w] represents max profit achievable considering first i parcels with weight limit w.")
        slice_rows = min(15, len(knap_result.dp_table))
        slice_cols = min(20, len(knap_result.dp_table[0]))
        dp_subset = [row[:slice_cols] for row in knap_result.dp_table[:slice_rows]]
        df_dp = pd.DataFrame(dp_subset)
        df_dp.index = [f"Item {i} ({sorted_parcels[i-1].parcel_id if i>0 else 'None'})" for i in range(slice_rows)]
        df_dp.columns = [f"{w}kg" for w in range(slice_cols)]
        st.dataframe(df_dp)


# -------------------------------------------------------------
# 5. DELIVERY ROAD GRAPH
# -------------------------------------------------------------
elif menu_choice == "🗺️ Delivery Road Graph":
    st.markdown('<div class="main-title">🗺️ Delivery Road Network Graph</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Adjacency list representation of locations and bidirectional road distances.</div>', unsafe_allow_html=True)

    g = st.session_state.graph
    nodes = g.get_nodes()

    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Network Adjacency List")
        adj_records = []
        for u in nodes:
            neigh_list = [f"{v} ({w} km)" for v, w in g.get_neighbors(u)]
            adj_records.append({
                "Location": u,
                "Degree (Roads)": len(neigh_list),
                "Connected Neighbors": ", ".join(neigh_list)
            })
        st.dataframe(pd.DataFrame(adj_records), use_container_width=True)

    with c2:
        st.subheader("Road Network Map")
        fig = plot_delivery_network(g)
        st.pyplot(fig)


# -------------------------------------------------------------
# 6. SHORTEST PATHS (DIJKSTRA)
# -------------------------------------------------------------
elif menu_choice == "📍 Shortest Paths (Dijkstra)":
    st.markdown('<div class="main-title">📍 Dijkstra Shortest Path Finder</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Manual Dijkstra Algorithm using heapq (Binary Min-Heap) — O((V + E) log V).</div>', unsafe_allow_html=True)

    g = st.session_state.graph
    warehouse = st.session_state.warehouse

    c1, c2 = st.columns(2)
    with c1:
        source_node = st.selectbox("Source Location (Default: Central Depot)", options=g.get_nodes(), index=g.get_nodes().index(warehouse))
    with c2:
        target_node = st.selectbox("Destination Location", options=g.get_nodes(), index=1)

    d_res = dijkstra_shortest_paths(g, source_node)
    dist = d_res.get_distance_to(target_node)
    path = d_res.get_path_to(target_node)

    m1, m2 = st.columns(2)
    with m1:
        st.metric("Shortest Road Distance", f"{dist:.2f} km" if dist != float("inf") else "Unreachable")
    with m2:
        st.metric("Calculation Time", f"{d_res.execution_time * 1000:.4f} ms")

    if path:
        st.success(f"Optimal Turn-by-Turn Path: **{' ➔ '.join(path)}**")
    else:
        st.error(f"No reachable road path exists between {source_node} and {target_node}.")

    st.subheader(f"All Shortest Paths from '{source_node}'")
    all_details = d_res.get_route_details(g.get_nodes())
    st.dataframe(pd.DataFrame(all_details), use_container_width=True)


# -------------------------------------------------------------
# 7. ROUTE OPTIMIZATION (TSP)
# -------------------------------------------------------------
elif menu_choice == "🚚 Route Optimization (TSP)":
    st.markdown('<div class="main-title">🚚 Delivery Route Planning (TSP Nearest Neighbor)</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Heuristic route builder visiting all customer stops and returning to the depot.</div>', unsafe_allow_html=True)

    g = st.session_state.graph
    warehouse = st.session_state.warehouse

    # Auto-pick packed parcels or allow manual selection
    sorted_parcels, _ = sort_parcels_with_metrics(st.session_state.parcels)
    packed = knapsack_01(sorted_parcels, capacity=35).selected_parcels
    default_stops = list(dict.fromkeys(p.delivery_location for p in packed))

    available_stops = [n for n in g.get_nodes() if n != warehouse]
    selected_stops = st.multiselect("Delivery Stops to Service", options=available_stops, default=default_stops)

    if st.button("Generate Optimized Route", type="primary"):
        if not selected_stops:
            st.warning("Please select at least one delivery stop.")
        else:
            tsp_res = solve_tsp_nearest_neighbor(g, warehouse, selected_stops)

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Total Route Distance", f"{tsp_res.total_distance_km:.2f} km")
            with m2:
                st.metric("Stops Serviced", len(selected_stops))
            with m3:
                st.metric("Route Planning Time", f"{tsp_res.execution_time * 1000:.3f} ms")

            st.success(f"**Ordered Tour:** {' ➔ '.join(tsp_res.route_sequence)}")

            c1, c2 = st.columns([1, 1])
            with c1:
                st.subheader("Step-by-Step Delivery Itinerary")
                legs_df = pd.DataFrame([leg.to_dict() for leg in tsp_res.detailed_legs])
                st.dataframe(legs_df, use_container_width=True)
            with c2:
                st.subheader("Interactive Route Map")
                fig = plot_delivery_network(g, tsp_res)
                st.pyplot(fig)


# -------------------------------------------------------------
# 8. PERFORMANCE ANALYSIS
# -------------------------------------------------------------
elif menu_choice == "📊 Performance Analysis":
    st.markdown('<div class="main-title">📊 Empirical Performance Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Execution time benchmarking across Small (10), Medium (100), and Large (500) inputs.</div>', unsafe_allow_html=True)

    reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
    csv_file = os.path.join(reports_dir, "performance_results.csv")

    if st.button("Re-run Empirical Benchmarks"):
        with st.spinner("Executing benchmark suite with time.perf_counter()..."):
            run_benchmarks(reports_dir)
            st.success("Benchmarks completed and charts updated!")

    if os.path.exists(csv_file):
        df_bench = pd.read_csv(csv_file)
        st.subheader("Algorithmic Runtime Comparison Table")
        st.dataframe(df_bench, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Runtime Comparison Bar Chart (Log Scale)")
            bar_img = os.path.join(reports_dir, "performance_runtime_comparison.png")
            if os.path.exists(bar_img):
                st.image(bar_img, use_container_width=True)
        with c2:
            st.subheader("Scaling Curves (Input Size vs Runtime)")
            line_img = os.path.join(reports_dir, "performance_scaling_curves.png")
            if os.path.exists(line_img):
                st.image(line_img, use_container_width=True)

        st.subheader("0/1 Knapsack Capacity Sensitivity (Pseudo-Polynomial O(n·W))")
        knap_img = os.path.join(reports_dir, "knapsack_capacity_impact.png")
        if os.path.exists(knap_img):
            st.image(knap_img, use_container_width=True)
    else:
        st.info("Performance results CSV not found. Click the button above to run benchmarks.")


# -------------------------------------------------------------
# 9. PROJECT INFORMATION & VIVA NOTES
# -------------------------------------------------------------
elif menu_choice == "ℹ️ Project Information & Viva Notes":
    st.markdown('<div class="main-title">ℹ️ Project Information & Viva Guide</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">K.R. Mangalam University — ETCCDA302 Capstone Documentation</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 🎯 System Architecture Overview
    The Mini-Courier Planner orchestrates four classic foundational computer science algorithms into a cohesive logistics pipeline:
    1. **Merge Sort (Divide-and-Conquer)**: Prioritizes parcels based on urgency and deadline with deterministic $O(n \log n)$ guarantee and stability.
    2. **0/1 Knapsack (Dynamic Programming)**: Optimizes vehicle cargo filling within a payload weight constraint to maximize revenue in $O(n \cdot W)$ pseudo-polynomial time.
    3. **Dijkstra's Algorithm (Greedy with Priority Queue)**: Computes true shortest road path between warehouse and destinations in $O((V+E)\log V)$ time.
    4. **Nearest Neighbor TSP (Heuristic)**: Assembles delivery stops into a closed-loop route starting and ending at the warehouse in $O(k^2)$ time.

    ### ⏱️ Time & Space Complexity Matrix
    | Algorithm | Technique | Time Complexity | Auxiliary Space | Key Invariant |
    | :--- | :--- | :--- | :--- | :--- |
    | **Merge Sort** | Divide & Conquer | $O(n \log n)$ (All Cases) | $O(n)$ | Stable sorting & recursive subproblem division |
    | **0/1 Knapsack** | Dynamic Programming | $O(n \cdot W)$ | $O(n \cdot W)$ | Optimal substructure & overlapping subproblems |
    | **Dijkstra** | Greedy (Min-Heap) | $O((V + E) \log V)$ | $O(V + E)$ | Non-negative edge weights & triangular relaxation |
    | **Nearest Neighbor TSP** | Greedy Heuristic | $O(k^2 + k(V+E)\log V)$| $O(V + E)$ | Locally nearest unvisited node chosen at each step |

    ### 🎓 Viva Quick Prep Notes
    - **Why Merge Sort instead of Quick Sort?** Merge Sort guarantees $O(n \log n)$ in the worst case (unlike Quick Sort's $O(n^2)$ with poor pivots) and is naturally stable, preserving original sequence for identical parcels.
    - **Why is 0/1 Knapsack pseudo-polynomial?** Its runtime depends on the numeric magnitude of vehicle capacity $W$. In terms of input bits $b = \log_2 W$, the runtime is $O(n \cdot 2^b)$, which is exponential in input size.
    - **Does Nearest Neighbor guarantee the optimal TSP tour?** No. It is a greedy heuristic that can make locally optimal choices leading to expensive return legs. It provides a practical polynomial-time approximation.
    """)

