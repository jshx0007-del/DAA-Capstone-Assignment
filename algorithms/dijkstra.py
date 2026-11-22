"""
algorithms/dijkstra.py
Manual implementation of Dijkstra's Shortest Path Algorithm using heapq (Binary Min-Heap).

Finds the shortest driving distance and reconstructs the actual road path from a source
location (e.g. Courier Warehouse) to all other locations in the delivery network.

Complexities:
- Time Complexity: O((V + E) log V) using a binary heap, where V is number of vertices (locations)
  and E is number of edges (roads).
- Space Complexity: O(V + E) to store adjacency list, distances, predecessors, and heap.
"""

import heapq
import time
from typing import Dict, List, Optional, Tuple, Any
from models.delivery_graph import DeliveryGraph


class DijkstraResult:
    """Stores the shortest path search results from a specific source."""

    def __init__(
        self,
        source: str,
        distances: Dict[str, float],
        predecessors: Dict[str, Optional[str]],
        execution_time: float
    ):
        self.source = source
        self.distances = distances
        self.predecessors = predecessors
        self.execution_time = execution_time

    def get_path_to(self, destination: str) -> Optional[List[str]]:
        """
        Reconstructs the node-by-node shortest path from source to destination.
        Returns None if destination is unreachable.
        """
        if self.distances.get(destination, float("inf")) == float("inf"):
            return None

        path = []
        curr: Optional[str] = destination
        while curr is not None:
            path.append(curr)
            curr = self.predecessors.get(curr)

        path.reverse()
        return path

    def get_distance_to(self, destination: str) -> float:
        """Returns the shortest distance to destination, or infinity if unreachable."""
        return self.distances.get(destination, float("inf"))

    def get_route_details(self, destinations: List[str]) -> List[Dict[str, Any]]:
        """
        Generates structured details for a specific list of delivery locations.
        """
        details = []
        for dest in destinations:
            dist = self.get_distance_to(dest)
            path = self.get_path_to(dest)
            details.append({
                "source": self.source,
                "destination": dest,
                "reachable": dist != float("inf"),
                "distance_km": dist if dist != float("inf") else None,
                "path": path,
                "path_str": " -> ".join(path) if path else "Unreachable"
            })
        return details


def dijkstra_shortest_paths(graph: DeliveryGraph, source: str) -> DijkstraResult:
    """
    Computes shortest paths from `source` to all reachable nodes in `graph`
    using a binary min-heap (heapq). NetworkX shortest-path functions are NOT used.

    Args:
        graph: DeliveryGraph instance containing road network adjacency list.
        source: Name of the starting location (e.g. 'Warehouse').

    Returns:
        DijkstraResult containing distance map, predecessor map, and runtime.
    """
    start_time = time.perf_counter()

    all_nodes = graph.get_nodes()
    if source not in all_nodes:
        # If source isn't in graph, return empty result
        elapsed = time.perf_counter() - start_time
        return DijkstraResult(
            source=source,
            distances={n: float("inf") for n in all_nodes},
            predecessors={n: None for n in all_nodes},
            execution_time=elapsed
        )

    # Distances initialized to infinity, predecessor to None
    distances: Dict[str, float] = {node: float("inf") for node in all_nodes}
    predecessors: Dict[str, Optional[str]] = {node: None for node in all_nodes}
    distances[source] = 0.0

    # Priority queue stores tuples of (distance_from_source, node_name)
    pq: List[Tuple[float, str]] = [(0.0, source)]

    visited = set()

    while pq:
        curr_dist, u = heapq.heappop(pq)

        # Skip if we already finalized the shortest path for this node
        if u in visited:
            continue
        visited.add(u)

        # Relax all outgoing edges from u
        for v, weight in graph.get_neighbors(u):
            if v in visited:
                continue

            new_dist = curr_dist + weight
            if new_dist < distances[v]:
                distances[v] = new_dist
                predecessors[v] = u
                heapq.heappush(pq, (new_dist, v))

    elapsed = time.perf_counter() - start_time
    return DijkstraResult(source, distances, predecessors, elapsed)


def compute_all_pairs_shortest_paths(
    graph: DeliveryGraph
) -> Dict[str, DijkstraResult]:
    """
    Computes all-pairs shortest paths by running Dijkstra from each node.
    Used by TSP to calculate shortest travel distances between any pair of stops.
    """
    all_pairs: Dict[str, DijkstraResult] = {}
    for node in graph.get_nodes():
        all_pairs[node] = dijkstra_shortest_paths(graph, node)
    return all_pairs

