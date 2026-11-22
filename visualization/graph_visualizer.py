"""
visualization/graph_visualizer.py
Visualizes the delivery road network and the TSP delivery tour using Matplotlib and NetworkX.
Note: NetworkX is used strictly for graph layout rendering, NOT for algorithm calculations.
"""

from typing import Optional, List
import matplotlib.pyplot as plt
import networkx as nx
from models.delivery_graph import DeliveryGraph
from algorithms.tsp import TSPResult


def plot_delivery_network(
    graph: DeliveryGraph,
    tsp_result: Optional[TSPResult] = None,
    save_path: Optional[str] = None,
    title: str = "Mini-Courier Planner: Delivery Network & TSP Route"
) -> plt.Figure:
    """
    Renders an informative visualization of the road network and the active delivery route.

    Args:
        graph: The DeliveryGraph instance.
        tsp_result: Optional TSPResult to overlay the delivery van's tour.
        save_path: Optional file path to save the generated figure.
        title: Plot title.

    Returns:
        Matplotlib Figure object.
    """
    fig, ax = plt.subplots(figsize=(11, 8))

    # Build NetworkX graph strictly for visualization
    G = nx.Graph()
    for u in graph.get_nodes():
        G.add_node(u)

    edge_labels = {}
    for u in graph.get_nodes():
        for v, w in graph.get_neighbors(u):
            if not G.has_edge(u, v):
                G.add_edge(u, v, weight=w)
                edge_labels[(u, v)] = f"{w:.1f} km"

    # Use defined coordinates if available, otherwise spring layout
    pos = {}
    has_custom_coords = len(graph.coordinates) == len(graph.get_nodes())
    if has_custom_coords:
        pos = graph.coordinates
    else:
        pos = nx.spring_layout(G, seed=42)

    # 1. Draw base road edges
    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color="#CBD5E1",
        width=2.0,
        style="solid",
        alpha=0.8
    )

    # 2. Draw edge weight labels (distances)
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=edge_labels,
        font_size=8,
        font_color="#475569",
        ax=ax,
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#E2E8F0", alpha=0.9)
    )

    # 3. Categorize nodes: Warehouse, Delivery Stops, Other Network Nodes
    warehouse = tsp_result.warehouse if tsp_result else "Central Warehouse"
    visited_stops = tsp_result.route_sequence if tsp_result else []
    delivery_stops = [n for n in visited_stops if n != warehouse]

    other_nodes = [n for n in G.nodes() if n != warehouse and n not in delivery_stops]

    # Draw regular nodes
    if other_nodes:
        nx.draw_networkx_nodes(
            G, pos, nodelist=other_nodes,
            node_color="#94A3B8", node_size=600,
            ax=ax, alpha=0.7
        )

    # Draw delivery stops
    if delivery_stops:
        nx.draw_networkx_nodes(
            G, pos, nodelist=delivery_stops,
            node_color="#3B82F6", node_size=800,
            ax=ax, edgecolors="#1D4ED8", linewidths=2
        )

    # Draw warehouse
    if warehouse in G:
        nx.draw_networkx_nodes(
            G, pos, nodelist=[warehouse],
            node_color="#10B981", node_size=1000,
            node_shape="s", ax=ax, edgecolors="#047857", linewidths=2.5
        )

    # 4. Node Labels with stop numbers if tour exists
    labels = {}
    for node in G.nodes():
        if node == warehouse:
            labels[node] = f"★ {node}\n(DEPOT)"
        elif node in delivery_stops:
            # Find 1-based order in sequence
            order_indices = [str(i) for i, x in enumerate(visited_stops) if x == node]
            stop_tag = f"Stop #{','.join(order_indices)}"
            labels[node] = f"{node}\n[{stop_tag}]"
        else:
            labels[node] = node

    nx.draw_networkx_labels(
        G, pos, labels=labels,
        font_size=8.5, font_weight="bold",
        font_color="#0F172A", ax=ax
    )

    # 5. Highlight TSP Tour path with directional arrows
    if tsp_result and tsp_result.detailed_legs:
        # Trace through the legs
        for idx, leg in enumerate(tsp_result.detailed_legs):
            leg_path = leg.path
            for i in range(len(leg_path) - 1):
                u_leg, v_leg = leg_path[i], leg_path[i + 1]
                p1, p2 = pos[u_leg], pos[v_leg]
                ax.annotate(
                    "",
                    xy=p2, xycoords="data",
                    xytext=p1, textcoords="data",
                    arrowprops=dict(
                        arrowstyle="-|>",
                        color="#EF4444",
                        lw=3.0,
                        ls="-",
                        shrinkA=15,
                        shrinkB=15,
                        mutation_scale=15
                    )
                )

        total_km = tsp_result.total_distance_km
        ax.text(
            0.02, 0.02,
            f"Active TSP Tour: {' -> '.join(tsp_result.route_sequence)}\n"
            f"Total Driving Distance: {total_km:.2f} km | Stops: {len(delivery_stops)}",
            transform=ax.transAxes,
            fontsize=9.5,
            fontweight="semibold",
            bbox=dict(boxstyle="round,pad=0.5", fc="#FEF2F2", ec="#F87171", lw=1.5)
        )

    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.axis("off")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig

