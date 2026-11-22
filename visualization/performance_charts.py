"""
visualization/performance_charts.py
Generates performance comparison charts and scaling curves using Matplotlib.
Outputs:
1. Runtime comparison bar chart (Small, Medium, Large datasets across algorithms)
2. Input size vs execution time scaling line chart
3. Knapsack capacity impact analysis chart
"""

from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import pandas as pd


def generate_runtime_comparison_bar_chart(
    df_results: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Renders grouped bar chart comparing execution times across dataset sizes.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Pivot table to have Algorithm on x-axis, Dataset Size as bars
    pivot = df_results.pivot(index="Algorithm", columns="Dataset_Size", values="Execution_Time_ms")

    # Order columns by size
    size_order = [col for col in ["Small (10)", "Medium (100)", "Large (500)"] if col in pivot.columns]
    pivot = pivot[size_order]

    colors = ["#3B82F6", "#10B981", "#F59E0B"]
    pivot.plot(kind="bar", ax=ax, color=colors[:len(size_order)], width=0.75, edgecolor="#1E293B", linewidth=1.0)

    ax.set_title("Algorithm Execution Time Comparison (Logarithmic Scale)", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Execution Time (milliseconds) - Log Scale", fontsize=11)
    ax.set_xlabel("Algorithm", fontsize=11)
    ax.set_yscale("log")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    ax.legend(title="Dataset Size", frameon=True)
    plt.xticks(rotation=15, ha="right")
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def generate_scaling_line_chart(
    df_results: pd.DataFrame,
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plots input size (n) vs execution time (ms) curves to visualize empirical growth.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Map dataset labels to numeric sizes
    size_map = {"Small (10)": 10, "Medium (100)": 100, "Large (500)": 500}
    df_plot = df_results.copy()
    df_plot["N"] = df_plot["Dataset_Size"].map(size_map)

    algorithms = df_plot["Algorithm"].unique()
    markers = ["o", "s", "^", "D"]
    colors = ["#2563EB", "#059669", "#D97706", "#DC2626"]

    for idx, algo in enumerate(algorithms):
        sub = df_plot[df_plot["Algorithm"] == algo].sort_values("N")
        ax.plot(
            sub["N"],
            sub["Execution_Time_ms"],
            marker=markers[idx % len(markers)],
            linewidth=2.2,
            markersize=7,
            label=algo,
            color=colors[idx % len(colors)]
        )

    ax.set_title("Input Size (N) vs Execution Time (ms)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Number of Parcels / Elements (N)", fontsize=11)
    ax.set_ylabel("Execution Time (ms)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(title="Algorithms", frameon=True)
    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig


def generate_knapsack_capacity_impact_chart(
    capacity_data: List[Dict[str, Any]],
    save_path: Optional[str] = None
) -> plt.Figure:
    """
    Plots Knapsack vehicle capacity W vs execution time, demonstrating O(n*W) pseudo-polynomial time.
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    df = pd.DataFrame(capacity_data)

    ax.plot(
        df["Capacity_W"],
        df["Execution_Time_ms"],
        marker="o",
        color="#7C3AED",
        linewidth=2.5,
        markersize=6
    )

    ax.set_title("0/1 Knapsack: Impact of Vehicle Capacity (W) on Execution Time", fontsize=12, fontweight="bold", pad=12)
    ax.set_xlabel("Vehicle Capacity W (kg)", fontsize=11)
    ax.set_ylabel("Execution Time (ms)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)

    # Annotate pseudo-polynomial behavior
    if not df.empty:
        max_pt = df.iloc[-1]
        ax.annotate(
            f"O(n · W) Growth\nMax: {max_pt['Execution_Time_ms']:.2f} ms",
            xy=(max_pt["Capacity_W"], max_pt["Execution_Time_ms"]),
            xytext=(max_pt["Capacity_W"] * 0.75, max_pt["Execution_Time_ms"] * 0.85),
            arrowprops=dict(facecolor="#4C1D95", shrink=0.08, width=1, headwidth=6),
            fontsize=9.5,
            bbox=dict(boxstyle="round,pad=0.3", fc="#EDE9FE", ec="#8B5CF6")
        )

    fig.tight_layout()

    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches="tight")

    return fig

