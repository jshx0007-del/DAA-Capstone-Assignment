"""
models/delivery_graph.py
Adjacency-list based weighted undirected graph representing the delivery network.
"""

from typing import Dict, List, Tuple, Optional, Any


class DeliveryGraph:
    """
    Weighted undirected graph representing road connections between delivery locations.
    Uses an adjacency list representation.
    """

    def __init__(self):
        # Map node -> List of (neighbor, distance_in_km)
        self.adj: Dict[str, List[Tuple[str, float]]] = {}
        # Optional 2D coordinates for visualization: node -> (x, y)
        self.coordinates: Dict[str, Tuple[float, float]] = {}

    def add_node(self, node: str, coords: Optional[Tuple[float, float]] = None) -> None:
        """Add a location node to the graph."""
        if node not in self.adj:
            self.adj[node] = []
        if coords is not None:
            self.coordinates[node] = coords

    def add_edge(self, u: str, v: str, weight: float, bidirectional: bool = True) -> None:
        """
        Add a weighted edge between location u and location v.
        Road networks are typically bidirectional.
        """
        if weight < 0:
            raise ValueError(f"Edge weight cannot be negative: {weight}")

        self.add_node(u)
        self.add_node(v)

        # Update or add u -> v
        self._insert_or_update_edge(u, v, float(weight))
        if bidirectional:
            self._insert_or_update_edge(v, u, float(weight))

    def _insert_or_update_edge(self, u: str, v: str, weight: float) -> None:
        for idx, (neighbor, _) in enumerate(self.adj[u]):
            if neighbor == v:
                self.adj[u][idx] = (v, weight)
                return
        self.adj[u].append((v, weight))

    def get_nodes(self) -> List[str]:
        """Return list of all location names."""
        return list(self.adj.keys())

    def get_neighbors(self, node: str) -> List[Tuple[str, float]]:
        """Return list of (neighbor, distance) for a given location."""
        return self.adj.get(node, [])

    def get_edge_weight(self, u: str, v: str) -> Optional[float]:
        """Return the direct edge weight between u and v, or None if no direct road exists."""
        for neighbor, weight in self.adj.get(u, []):
            if neighbor == v:
                return weight
        return None

    def has_node(self, node: str) -> bool:
        """Check if location exists in graph."""
        return node in self.adj

    def to_dict(self) -> Dict[str, Any]:
        """Serialize graph to dictionary for JSON persistence."""
        edges = []
        seen = set()
        for u, neighbors in self.adj.items():
            for v, w in neighbors:
                edge_key = tuple(sorted([u, v]))
                if edge_key not in seen:
                    seen.add(edge_key)
                    edges.append({"from": u, "to": v, "distance": w})

        return {
            "nodes": [
                {
                    "name": node,
                    "x": self.coordinates.get(node, (0.0, 0.0))[0],
                    "y": self.coordinates.get(node, (0.0, 0.0))[1]
                }
                for node in self.adj
            ],
            "edges": edges
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeliveryGraph":
        """Reconstruct graph from dictionary."""
        g = cls()
        for node_info in data.get("nodes", []):
            name = node_info["name"]
            coords = (float(node_info.get("x", 0.0)), float(node_info.get("y", 0.0)))
            g.add_node(name, coords)

        for edge in data.get("edges", []):
            g.add_edge(edge["from"], edge["to"], float(edge["distance"]))

        return g

