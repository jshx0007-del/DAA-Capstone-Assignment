"""
algorithms/performance.py
Comprehensive performance evaluation harness for all major algorithms.

Measures actual empirical execution times using time.perf_counter() across:
- Small Dataset: 10 parcels / nodes
- Medium Dataset: 100 parcels / 30 nodes
- Large Dataset: 500 parcels / 100 nodes

Also evaluates 0/1 Knapsack runtime sensitivity against vehicle capacity W
to demonstrate O(n * W) pseudo-polynomial complexity.
"""

import os
import random
import time
from typing import List, Dict, Any, Tuple
import pandas as pd

from models.parcel import Parcel
from models.delivery_graph import DeliveryGraph
from algorithms.sorting import sort_parcels_with_metrics
from algorithms.knapsack import knapsack_01
from algorithms.dijkstra import dijkstra_shortest_paths
from algorithms.tsp import solve_tsp_nearest_neighbor
from visualization.performance_charts import (
    generate_runtime_comparison_bar_chart,
    generate_scaling_line_chart,
    generate_knapsack_capacity_impact_chart
)


def generate_synthetic_parcels(count: int, locations: List[str], seed: int = 42) -> List[Parcel]:
    """Generates synthetic reproducible parcel datasets for empirical benchmarking."""
    rng = random.Random(seed)
    customer_first_names = ["Aarav", "Priya", "Rohan", "Sneha", "Vikram", "Ananya", "Kabir", "Neha", "Aditya", "Pooja"]
    customer_last_names = ["Sharma", "Verma", "Gupta", "Patel", "Malhotra", "Iyer", "Singh", "Reddy", "Nair", "Joshi"]

    parcels: List[Parcel] = []
    for i in range(1, count + 1):
        name = f"{rng.choice(customer_first_names)} {rng.choice(customer_last_names)}"
        loc = rng.choice(locations)
        weight = rng.randint(1, 20)
        priority = rng.randint(1, 10)
        deadline = rng.randint(1, 12)
        value = round(rng.uniform(150.0, 3000.0), 2)
        parcels.append(
            Parcel(
                parcel_id=f"SYN-{i:04d}",
                customer_name=name,
                delivery_location=loc,
                weight=weight,
                priority=priority,
                delivery_deadline=deadline,
                value=value
            )
        )
    return parcels


def generate_synthetic_graph(node_count: int, edge_density: float = 2.5, seed: int = 42) -> Tuple[DeliveryGraph, str]:
    """
    Generates a connected synthetic road graph for scaling experiments.
    Returns (DeliveryGraph, warehouse_node_name).
    """
    rng = random.Random(seed)
    g = DeliveryGraph()
    warehouse = "Hub-0"
    g.add_node(warehouse, (50.0, 50.0))

    # Add other nodes in a grid / planar ring
    for i in range(1, node_count):
        node_name = f"Loc-{i}"
        x = rng.uniform(0.0, 100.0)
        y = rng.uniform(0.0, 100.0)
        g.add_node(node_name, (round(x, 1), round(y, 1)))

    # Ensure connectivity: connect each node i to a previous node
    nodes = g.get_nodes()
    for i in range(1, len(nodes)):
        prev = rng.choice(nodes[:i])
        dist = round(rng.uniform(1.5, 15.0), 2)
        g.add_edge(nodes[i], prev, dist)

    # Add additional edges to reflect road mesh
    extra_edges = int(node_count * edge_density)
    for _ in range(extra_edges):
        u = rng.choice(nodes)
        v = rng.choice(nodes)
        if u != v:
            dist = round(rng.uniform(2.0, 18.0), 2)
            g.add_edge(u, v, dist)

    return g, warehouse


def run_benchmarks(reports_dir: str = "reports") -> Dict[str, Any]:
    """
    Executes actual empirical benchmarks across all algorithms and generates reports and charts.

    Returns:
        Dictionary containing benchmark DataFrames and analysis summaries.
    """
    os.makedirs(reports_dir, exist_ok=True)

    benchmark_configs = [
        {"label": "Small (10)", "parcel_count": 10, "capacity": 50, "nodes": 10, "tsp_stops": 5},
        {"label": "Medium (100)", "parcel_count": 100, "capacity": 200, "nodes": 30, "tsp_stops": 15},
        {"label": "Large (500)", "parcel_count": 500, "capacity": 500, "nodes": 100, "tsp_stops": 30},
    ]

    records: List[Dict[str, Any]] = []

    print("[*] Running algorithmic benchmarks with genuine time.perf_counter() measurements...")

    for cfg in benchmark_configs:
        size_label = cfg["label"]
        p_count = cfg["parcel_count"]
        cap = cfg["capacity"]
        n_count = cfg["nodes"]
        t_stops = cfg["tsp_stops"]

        # Generate graph
        graph, warehouse = generate_synthetic_graph(n_count, seed=100 + n_count)
        all_locs = [n for n in graph.get_nodes() if n != warehouse]

        # Generate parcels
        parcels = generate_synthetic_parcels(p_count, all_locs, seed=200 + p_count)

        # 1. Merge Sort
        # Repeat multiple times for small inputs to get stable average
        repeats = 10 if p_count <= 100 else 3
        sort_times = []
        for _ in range(repeats):
            _, t = sort_parcels_with_metrics(parcels)
            sort_times.append(t)
        avg_sort_time_ms = (sum(sort_times) / repeats) * 1000.0

        records.append({
            "Dataset_Size": size_label,
            "Algorithm": "Merge Sort",
            "Theoretical_Time_Complexity": "O(n log n)",
            "Theoretical_Space_Complexity": "O(n)",
            "Elements_Processed": p_count,
            "Execution_Time_ms": round(avg_sort_time_ms, 4)
        })

        # 2. 0/1 Knapsack DP
        knap_times = []
        for _ in range(repeats):
            res = knapsack_01(parcels, cap)
            knap_times.append(res.execution_time)
        avg_knap_time_ms = (sum(knap_times) / repeats) * 1000.0

        records.append({
            "Dataset_Size": size_label,
            "Algorithm": "0/1 Knapsack DP",
            "Theoretical_Time_Complexity": "O(n · W)",
            "Theoretical_Space_Complexity": "O(n · W)",
            "Elements_Processed": f"n={p_count}, W={cap}",
            "Execution_Time_ms": round(avg_knap_time_ms, 4)
        })

        # 3. Dijkstra's Algorithm
        dijk_times = []
        for _ in range(repeats):
            d_res = dijkstra_shortest_paths(graph, warehouse)
            dijk_times.append(d_res.execution_time)
        avg_dijk_time_ms = (sum(dijk_times) / repeats) * 1000.0

        records.append({
            "Dataset_Size": size_label,
            "Algorithm": "Dijkstra (Heap)",
            "Theoretical_Time_Complexity": "O((V + E) log V)",
            "Theoretical_Space_Complexity": "O(V + E)",
            "Elements_Processed": f"V={len(graph.get_nodes())}, E={sum(len(neighbors) for neighbors in graph.adj.values()) // 2}",
            "Execution_Time_ms": round(avg_dijk_time_ms, 4)
        })

        # 4. Nearest Neighbor TSP
        target_stops = all_locs[:t_stops]
        tsp_times = []
        for _ in range(repeats):
            tsp_res = solve_tsp_nearest_neighbor(graph, warehouse, target_stops)
            tsp_times.append(tsp_res.execution_time)
        avg_tsp_time_ms = (sum(tsp_times) / repeats) * 1000.0

        records.append({
            "Dataset_Size": size_label,
            "Algorithm": "Nearest Neighbor TSP",
            "Theoretical_Time_Complexity": "O(k² + k(V+E)log V)",
            "Theoretical_Space_Complexity": "O(V + E)",
            "Elements_Processed": f"Stops k={t_stops}",
            "Execution_Time_ms": round(avg_tsp_time_ms, 4)
        })

    df_results = pd.DataFrame(records)

    # Save benchmark table to CSV
    csv_path = os.path.join(reports_dir, "performance_results.csv")
    df_results.to_csv(csv_path, index=False)
    print(f"[✓] Benchmark results saved to: {csv_path}")

    # Knapsack Capacity Sensitivity Experiment
    print("[*] Running 0/1 Knapsack capacity scaling analysis (O(n*W) verification)...")
    knap_capacity_records: List[Dict[str, Any]] = []
    fixed_parcels = generate_synthetic_parcels(100, ["NodeA", "NodeB", "NodeC"], seed=999)
    test_capacities = [20, 50, 100, 200, 400, 800, 1500]

    for cap in test_capacities:
        times = []
        for _ in range(5):
            res = knapsack_01(fixed_parcels, cap)
            times.append(res.execution_time)
        avg_ms = (sum(times) / len(times)) * 1000.0
        knap_capacity_records.append({
            "Fixed_Parcels_N": 100,
            "Capacity_W": cap,
            "Execution_Time_ms": round(avg_ms, 4)
        })

    # Generate charts
    bar_chart_path = os.path.join(reports_dir, "performance_runtime_comparison.png")
    line_chart_path = os.path.join(reports_dir, "performance_scaling_curves.png")
    knap_chart_path = os.path.join(reports_dir, "knapsack_capacity_impact.png")

    generate_runtime_comparison_bar_chart(df_results, save_path=bar_chart_path)
    generate_scaling_line_chart(df_results, save_path=line_chart_path)
    generate_knapsack_capacity_impact_chart(knap_capacity_records, save_path=knap_chart_path)

    print(f"[✓] Bar chart generated: {bar_chart_path}")
    print(f"[✓] Scaling line chart generated: {line_chart_path}")
    print(f"[✓] Knapsack impact chart generated: {knap_chart_path}")

    return {
        "results_dataframe": df_results,
        "capacity_dataframe": pd.DataFrame(knap_capacity_records),
        "csv_path": csv_path,
        "bar_chart_path": bar_chart_path,
        "line_chart_path": line_chart_path,
        "knapsack_chart_path": knap_chart_path
    }


if __name__ == "__main__":
    run_benchmarks()

