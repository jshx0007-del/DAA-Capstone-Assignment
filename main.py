"""
main.py
Mini-Courier Planner — Intelligent Parcel Prioritization, Packing Optimization
and Delivery Route Planning System.

Main application entry point providing:
1. Interactive Command Line Interface (CLI)
2. Automated Demonstration Mode (--demo)
3. Benchmark Execution Mode (--benchmark)
"""

import argparse
import json
import os
import sys
from typing import List

from models.parcel import Parcel
from models.delivery_graph import DeliveryGraph
from algorithms.sorting import sort_parcels_with_metrics
from algorithms.knapsack import knapsack_01
from algorithms.dijkstra import dijkstra_shortest_paths
from algorithms.tsp import solve_tsp_nearest_neighbor
from algorithms.performance import run_benchmarks
from visualization.graph_visualizer import plot_delivery_network


def load_sample_data(base_dir: str):
    """Loads parcel and graph data from JSON files."""
    parcels_path = os.path.join(base_dir, "data", "parcels.json")
    graph_path = os.path.join(base_dir, "data", "graph.json")

    with open(parcels_path, "r", encoding="utf-8") as f:
        raw_parcels = json.load(f)
        parcels = [Parcel.from_dict(p) for p in raw_parcels]

    with open(graph_path, "r", encoding="utf-8") as f:
        raw_graph = json.load(f)
        graph = DeliveryGraph.from_dict(raw_graph)
        warehouse = raw_graph.get("warehouse", "Central Warehouse")

    return parcels, graph, warehouse


def print_banner():
    print("=" * 80)
    print(" MINI-COURIER PLANNER: ALGORITHMIC OPTIMIZATION ENGINE")
    print(" K.R. Mangalam University — Design & Analysis of Algorithms (ETCCDA302)")
    print("=" * 80)


def display_parcels(parcels: List[Parcel], title: str = "Parcels List"):
    print(f"\n--- {title} (Total: {len(parcels)}) ---")
    header = f"{'ID':<6} {'Customer':<18} {'Location':<20} {'Weight':<8} {'Priority':<9} {'Deadline':<9} {'Value':<10}"
    print(header)
    print("-" * len(header))
    for p in parcels:
        print(f"{p.parcel_id:<6} {p.customer_name:<18} {p.delivery_location:<20} {p.weight:<8} {p.priority:<9} {p.delivery_deadline:<9} ₹{p.value:<9.0f}")


def run_demo(base_dir: str):
    """Executes a complete automated end-to-end demonstration of all algorithms."""
    print_banner()
    print("[+] Loading initial sample dataset...")
    parcels, graph, warehouse = load_sample_data(base_dir)

    print(f"\nLoaded {len(parcels)} parcels and {len(graph.get_nodes())} delivery locations.")
    print(f"Designated Logistics Depot: {warehouse}")

    # 1. Parcel Prioritization (Merge Sort)
    print("\n" + "=" * 60)
    print(" STEP 1: PARCEL PRIORITIZATION (MANUAL MERGE SORT)")
    print("=" * 60)
    print("Sorting criteria: 1) Priority (desc) -> 2) Deadline (asc) -> 3) Parcel ID (asc)")
    sorted_parcels, sort_time = sort_parcels_with_metrics(parcels)
    display_parcels(sorted_parcels[:8], "Top Prioritized Parcels (First 8 shown)")
    print(f"[✓] Merge Sort Execution Time: {sort_time * 1000:.4f} ms")

    # 2. Vehicle Packing (0/1 Knapsack DP)
    vehicle_capacity = 35
    print("\n" + "=" * 60)
    print(" STEP 2: PACKING OPTIMIZATION (0/1 KNAPSACK DYNAMIC PROGRAMMING)")
    print("=" * 60)
    print(f"Vehicle Capacity Limit: {vehicle_capacity} kg")
    knap_res = knapsack_01(sorted_parcels, capacity=vehicle_capacity)
    display_parcels(knap_res.selected_parcels, "Optimally Selected Parcels for Trip")
    print(f"Total Selected Weight: {knap_res.total_weight} / {vehicle_capacity} kg")
    print(f"Total Monetary Value : ₹{knap_res.total_value:.2f}")
    print(f"Remaining Capacity   : {knap_res.remaining_capacity} kg")
    print(f"[✓] 0/1 Knapsack DP Execution Time: {knap_res.execution_time * 1000:.4f} ms")

    # 3. Dijkstra Shortest Paths
    print("\n" + "=" * 60)
    print(" STEP 3: SHORTEST PATHS FROM WAREHOUSE (MANUAL DIJKSTRA HEAP)")
    print("=" * 60)
    selected_locations = list(dict.fromkeys(p.delivery_location for p in knap_res.selected_parcels))
    print(f"Delivery destinations to service: {selected_locations}")
    dijkstra_res = dijkstra_shortest_paths(graph, warehouse)
    print(f"\n{'Destination':<22} {'Distance (km)':<15} {'Shortest Road Path'}")
    print("-" * 75)
    for loc in selected_locations:
        dist = dijkstra_res.get_distance_to(loc)
        path = dijkstra_res.get_path_to(loc)
        path_str = " -> ".join(path) if path else "Unreachable"
        print(f"{loc:<22} {dist:<15.2f} {path_str}")
    print(f"[✓] Dijkstra Execution Time: {dijkstra_res.execution_time * 1000:.4f} ms")

    # 4. TSP Route Planning
    print("\n" + "=" * 60)
    print(" STEP 4: DELIVERY TOUR PLANNING (NEAREST NEIGHBOR TSP APPROXIMATION)")
    print("=" * 60)
    tsp_res = solve_tsp_nearest_neighbor(graph, warehouse, selected_locations)
    print(f"Depot / Warehouse : {tsp_res.warehouse}")
    print(f"Total Driving Dist : {tsp_res.total_distance_km:.2f} km")
    print(f"Closed Loop Tour   : {'Yes (returns to depot)' if tsp_res.is_closed_tour else 'No'}")
    print("\nDetailed Tour Legs:")
    for idx, leg in enumerate(tsp_res.detailed_legs, start=1):
        print(f"  Leg {idx}: {leg.from_node} ➔ {leg.to_node} ({leg.distance_km:.2f} km) via [{leg.to_dict()['path_str']}]")
    print(f"\nFinal Ordered Delivery Sequence: {' ➔ '.join(tsp_res.route_sequence)}")
    print(f"[✓] TSP Nearest Neighbor Execution Time: {tsp_res.execution_time * 1000:.4f} ms")

    # 5. Generate Network Visualization
    reports_dir = os.path.join(base_dir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    viz_path = os.path.join(reports_dir, "delivery_route_visualization.png")
    plot_delivery_network(graph, tsp_res, save_path=viz_path)
    print(f"\n[✓] Generated delivery network route visualization at: {viz_path}")
    print("=" * 80)
    print(" DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)


def interactive_cli(base_dir: str):
    """Interactive text menu for user exploration."""
    parcels, graph, warehouse = load_sample_data(base_dir)
    sorted_parcels = None
    knap_res = None
    tsp_res = None

    while True:
        print_banner()
        print("1. View Current Parcels")
        print("2. Add a New Parcel")
        print("3. Prioritize Parcels (Merge Sort)")
        print("4. Pack Delivery Vehicle (0/1 Knapsack DP)")
        print("5. View Delivery Road Graph")
        print("6. Calculate Shortest Road Paths (Dijkstra)")
        print("7. Plan Delivery Route (Nearest Neighbor TSP)")
        print("8. Run Full Empirical Performance Benchmarks")
        print("9. Run Automated End-to-End Demo")
        print("0. Exit")
        print("-" * 80)
        choice = input("Enter your choice (0-9): ").strip()

        if choice == "1":
            display_parcels(parcels, "Current Parcel Pool")
        elif choice == "2":
            try:
                pid = input("Enter Parcel ID (e.g., P999): ").strip()
                name = input("Enter Customer Name: ").strip()
                print(f"Available locations: {graph.get_nodes()}")
                loc = input("Enter Delivery Location: ").strip()
                if not graph.has_node(loc):
                    print(f"[!] Warning: Location '{loc}' not in graph. Adding node automatically.")
                    graph.add_node(loc)
                wt = int(input("Enter Weight (kg, integer): ").strip())
                prio = int(input("Enter Priority (1-10): ").strip())
                dline = int(input("Enter Delivery Deadline (hours): ").strip())
                val = float(input("Enter Monetary Value (₹): ").strip())
                new_p = Parcel(pid, name, loc, wt, prio, dline, val)
                parcels.append(new_p)
                print(f"[✓] Parcel {pid} successfully added!")
            except Exception as e:
                print(f"[!] Error adding parcel: {e}")
        elif choice == "3":
            sorted_parcels, t = sort_parcels_with_metrics(parcels)
            display_parcels(sorted_parcels, "Prioritized Parcels (Merge Sort Result)")
            print(f"[✓] Sorted {len(parcels)} parcels in {t * 1000:.4f} ms (O(n log n)).")
        elif choice == "4":
            pool = sorted_parcels if sorted_parcels else parcels
            try:
                cap_input = input("Enter vehicle maximum capacity in kg [default: 35]: ").strip()
                cap = int(cap_input) if cap_input else 35
                knap_res = knapsack_01(pool, cap)
                display_parcels(knap_res.selected_parcels, f"Optimally Packed Parcels (Vehicle Cap: {cap} kg)")
                print(f"Total Selected Weight: {knap_res.total_weight} / {cap} kg")
                print(f"Total Selected Value : ₹{knap_res.total_value:.2f}")
                print(f"Remaining Capacity   : {knap_res.remaining_capacity} kg")
                print(f"[✓] Computed via manual DP table in {knap_res.execution_time * 1000:.4f} ms.")
            except Exception as e:
                print(f"[!] Error in Knapsack packing: {e}")
        elif choice == "5":
            print(f"\n--- Delivery Network Graph (Depot: {warehouse}) ---")
            for u in graph.get_nodes():
                neighbors = graph.get_neighbors(u)
                neigh_str = ", ".join([f"{v} ({w} km)" for v, w in neighbors])
                print(f"• {u:<22} ➔ [{neigh_str}]")
        elif choice == "6":
            print(f"Calculating shortest paths from {warehouse}...")
            d_res = dijkstra_shortest_paths(graph, warehouse)
            for node in graph.get_nodes():
                dist = d_res.get_distance_to(node)
                path = d_res.get_path_to(node)
                path_str = " -> ".join(path) if path else "Unreachable"
                print(f"  {node:<22} : {dist:.2f} km | Path: {path_str}")
        elif choice == "7":
            if knap_res and knap_res.selected_parcels:
                destinations = [p.delivery_location for p in knap_res.selected_parcels]
                print(f"Planning route for {len(destinations)} parcel destinations...")
            else:
                destinations = [n for n in graph.get_nodes() if n != warehouse][:5]
                print(f"Using default sample locations: {destinations}")
            tsp_res = solve_tsp_nearest_neighbor(graph, warehouse, destinations)
            print(f"\nDelivery Tour Route: {' ➔ '.join(tsp_res.route_sequence)}")
            print(f"Total Driving Distance: {tsp_res.total_distance_km:.2f} km")
            for idx, leg in enumerate(tsp_res.detailed_legs, 1):
                print(f"  Stop {idx}: {leg.from_node} ➔ {leg.to_node} ({leg.distance_km:.2f} km)")
        elif choice == "8":
            reports_dir = os.path.join(base_dir, "reports")
            run_benchmarks(reports_dir)
        elif choice == "9":
            run_demo(base_dir)
        elif choice == "0":
            print("Exiting Mini-Courier Planner. Goodbye!")
            sys.exit(0)
        else:
            print("[!] Invalid option. Please enter 0-9.")

        input("\nPress [Enter] to return to main menu...")


def main():
    parser = argparse.ArgumentParser(description="Mini-Courier Planner")
    parser.add_argument("--demo", action="store_true", help="Run automated end-to-end demonstration")
    parser.add_argument("--benchmark", action="store_true", help="Run empirical performance benchmarking suite")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))

    if args.demo:
        run_demo(base_dir)
    elif args.benchmark:
        reports_dir = os.path.join(base_dir, "reports")
        run_benchmarks(reports_dir)
    else:
        interactive_cli(base_dir)


if __name__ == "__main__":
    main()

