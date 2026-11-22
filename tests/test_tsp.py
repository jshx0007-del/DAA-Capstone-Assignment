"""
tests/test_tsp.py
Unit tests for manual Nearest Neighbor TSP Approximation route generation.
"""

import unittest
from models.delivery_graph import DeliveryGraph
from algorithms.tsp import solve_tsp_nearest_neighbor


class TestTSP(unittest.TestCase):

    def setUp(self):
        # Create a triangle graph:
        # Warehouse --(3.0)--> Stop1
        # |                   |
        # (4.0)               (5.0)
        # v                   v
        # Stop2 <---(2.0)------+
        #
        # Warehouse <-> Stop1: 3.0
        # Warehouse <-> Stop2: 4.0
        # Stop1 <-> Stop2: 2.0
        self.graph = DeliveryGraph()
        self.graph.add_edge("Warehouse", "Stop1", 3.0)
        self.graph.add_edge("Warehouse", "Stop2", 4.0)
        self.graph.add_edge("Stop1", "Stop2", 2.0)

    def test_empty_delivery_locations(self):
        """When no stops are provided, route is simply [Warehouse]."""
        result = solve_tsp_nearest_neighbor(self.graph, "Warehouse", [])
        self.assertEqual(result.route_sequence, ["Warehouse"])
        self.assertEqual(result.total_distance_km, 0.0)
        self.assertEqual(result.detailed_legs, [])
        self.assertTrue(result.is_closed_tour)

    def test_single_delivery_location(self):
        """Single stop: Warehouse -> Stop1 -> Warehouse."""
        result = solve_tsp_nearest_neighbor(self.graph, "Warehouse", ["Stop1"])
        self.assertEqual(result.route_sequence, ["Warehouse", "Stop1", "Warehouse"])
        # Leg 1: Warehouse -> Stop1 (3.0 km)
        # Leg 2: Stop1 -> Warehouse (3.0 km)
        self.assertEqual(result.total_distance_km, 6.0)
        self.assertTrue(result.is_closed_tour)

    def test_nearest_neighbor_greedy_choice(self):
        """
        From Warehouse:
        Distance to Stop1 is 3.0
        Distance to Stop2 is 4.0
        Nearest Neighbor chooses Stop1 first!
        From Stop1, unvisited is Stop2 (distance 2.0).
        From Stop2, returns to Warehouse (distance 4.0).
        Total distance = 3.0 + 2.0 + 4.0 = 9.0 km.
        """
        result = solve_tsp_nearest_neighbor(self.graph, "Warehouse", ["Stop2", "Stop1"])
        self.assertEqual(result.route_sequence, ["Warehouse", "Stop1", "Stop2", "Warehouse"])
        self.assertEqual(result.total_distance_km, 9.0)
        self.assertEqual(len(result.detailed_legs), 3)
        self.assertTrue(result.is_closed_tour)

    def test_duplicate_locations_deduplication(self):
        """Multiple parcels going to the same stop should only be visited once."""
        result = solve_tsp_nearest_neighbor(self.graph, "Warehouse", ["Stop1", "Stop1", "Stop2", "Stop2"])
        self.assertEqual(result.route_sequence, ["Warehouse", "Stop1", "Stop2", "Warehouse"])
        self.assertEqual(result.total_distance_km, 9.0)

    def test_disconnected_destination(self):
        """Unreachable stop in disconnected graph is handled without crashing."""
        self.graph.add_node("Remote Island")
        result = solve_tsp_nearest_neighbor(self.graph, "Warehouse", ["Stop1", "Remote Island"])
        self.assertIn("Remote Island", result.unreachable_stops)
        self.assertIn("Stop1", result.route_sequence)


if __name__ == "__main__":
    unittest.main()

