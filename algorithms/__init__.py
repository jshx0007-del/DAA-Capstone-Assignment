"""
Algorithms package for Mini-Courier Planner.
Contains manual implementations of:
- Merge Sort (parcels prioritization)
- 0/1 Knapsack DP (vehicle packing optimization)
- Dijkstra's Algorithm (shortest road paths)
- Nearest Neighbor TSP (route tour generation)
- Performance benchmarking suite
"""

from .sorting import merge_sort, sort_parcels_with_metrics, comes_before
from .knapsack import knapsack_01, KnapsackResult
from .dijkstra import dijkstra_shortest_paths, DijkstraResult, compute_all_pairs_shortest_paths
from .tsp import solve_tsp_nearest_neighbor, TSPResult, RouteLeg

__all__ = [
    "merge_sort",
    "sort_parcels_with_metrics",
    "comes_before",
    "knapsack_01",
    "KnapsackResult",
    "dijkstra_shortest_paths",
    "DijkstraResult",
    "compute_all_pairs_shortest_paths",
    "solve_tsp_nearest_neighbor",
    "TSPResult",
    "RouteLeg"
]

