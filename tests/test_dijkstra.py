"""
tests/test_dijkstra.py
Unit tests for manual Dijkstra's Shortest Path Algorithm using binary min-heap.
"""

import unittest
from models.delivery_graph import DeliveryGraph
from algorithms.dijkstra import dijkstra_shortest_paths


class TestDijkstra(unittest.TestCase):

    def setUp(self):
        # Build standard test graph:
        # A --(4)--> B --(2)--> C
        # |          ^          |
        # (1)        (1)        (3)
        # v          |          v
        # D -------- E -------- F
        #      (5)        (1)
        self.graph = DeliveryGraph()
        self.graph.add_edge("A", "B", 4.0)
        self.graph.add_edge("A", "D", 1.0)
        self.graph.add_edge("D", "E", 5.0)
        self.graph.add_edge("E", "B", 1.0)
        self.graph.add_edge("B", "C", 2.0)
        self.graph.add_edge("E", "F", 1.0)
        self.graph.add_edge("C", "F", 3.0)

    def test_source_to_itself(self):
        """Distance from source to itself must be 0."""
        res = dijkstra_shortest_paths(self.graph, "A")
        self.assertEqual(res.get_distance_to("A"), 0.0)
        self.assertEqual(res.get_path_to("A"), ["A"])

    def test_direct_vs_indirect_shortest_path(self):
        """Direct road A-B is 4.0, but A-D-E-B is 1+5+1 = 7.0, so A->B is shortest at 4.0."""
        res = dijkstra_shortest_paths(self.graph, "A")
        self.assertEqual(res.get_distance_to("B"), 4.0)
        self.assertEqual(res.get_path_to("B"), ["A", "B"])

    def test_multi_hop_shortest_path(self):
        """Shortest path from A to F:
        Option 1: A -> B -> C -> F = 4 + 2 + 3 = 9.0
        Option 2: A -> D -> E -> F = 1 + 5 + 1 = 7.0
        Option 3: A -> B -> E -> F = 4 + 1 + 1 = 6.0 (Global Shortest!)
        """
        res = dijkstra_shortest_paths(self.graph, "A")
        self.assertEqual(res.get_distance_to("F"), 6.0)
        self.assertEqual(res.get_path_to("F"), ["A", "B", "E", "F"])

    def test_disconnected_node(self):
        """Unreachable node in disconnected component must return infinity and None path."""
        self.graph.add_node("Isolated Island")
        res = dijkstra_shortest_paths(self.graph, "A")
        self.assertEqual(res.get_distance_to("Isolated Island"), float("inf"))
        self.assertIsNone(res.get_path_to("Isolated Island"))

    def test_nonexistent_source(self):
        """Searching from a source not in graph should safely report infinity."""
        res = dijkstra_shortest_paths(self.graph, "Ghost Town")
        self.assertEqual(res.get_distance_to("A"), float("inf"))
        self.assertIsNone(res.get_path_to("A"))

    def test_single_node_graph(self):
        """Graph with only one node."""
        g = DeliveryGraph()
        g.add_node("Solo")
        res = dijkstra_shortest_paths(g, "Solo")
        self.assertEqual(res.get_distance_to("Solo"), 0.0)
        self.assertEqual(res.get_path_to("Solo"), ["Solo"])


if __name__ == "__main__":
    unittest.main()
