"""
tests/test_integration.py
End-to-end integration tests connecting all modules:
Loading Data -> Merge Sort Prioritization -> Knapsack DP Packing -> Dijkstra Shortest Paths -> TSP Route Planning.
"""

import json
import os
import unittest
from models.parcel import Parcel
from models.delivery_graph import DeliveryGraph
from algorithms.sorting import merge_sort
from algorithms.knapsack import knapsack_01
from algorithms.dijkstra import dijkstra_shortest_paths
from algorithms.tsp import solve_tsp_nearest_neighbor


class TestIntegrationPipeline(unittest.TestCase):

    def setUp(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base_dir, "data", "parcels.json"), "r") as f:
            parcels_data = json.load(f)
            self.parcels = [Parcel.from_dict(p) for p in parcels_data]

        with open(os.path.join(base_dir, "data", "graph.json"), "r") as f:
            graph_data = json.load(f)
            self.graph = DeliveryGraph.from_dict(graph_data)
            self.warehouse = graph_data["warehouse"]

    def test_end_to_end_delivery_pipeline(self):
        # Step 1: Verify data loaded
        self.assertGreaterEqual(len(self.parcels), 10)
        self.assertGreaterEqual(len(self.graph.get_nodes()), 8)
        self.assertTrue(self.graph.has_node(self.warehouse))

        # Step 2: Merge Sort
        sorted_parcels = merge_sort(self.parcels)
        self.assertEqual(len(sorted_parcels), len(self.parcels))
        # Ensure highest priority is first
        self.assertGreaterEqual(sorted_parcels[0].priority, sorted_parcels[-1].priority)

        # Step 3: 0/1 Knapsack Packing (e.g. vehicle capacity = 35 kg)
        capacity = 35
        knapsack_res = knapsack_01(sorted_parcels, capacity=capacity)
        self.assertLessEqual(knapsack_res.total_weight, capacity)
        self.assertGreater(knapsack_res.total_value, 0)
        self.assertGreater(len(knapsack_res.selected_parcels), 0)

        # Step 4: Validate all selected delivery locations exist in graph
        selected_locations = [p.delivery_location for p in knapsack_res.selected_parcels]
        for loc in selected_locations:
            self.assertTrue(self.graph.has_node(loc), f"Location '{loc}' missing from delivery graph!")

        # Step 5: Dijkstra shortest paths from Warehouse to all selected locations
        dijkstra_res = dijkstra_shortest_paths(self.graph, self.warehouse)
        for loc in set(selected_locations):
            dist = dijkstra_res.get_distance_to(loc)
            path = dijkstra_res.get_path_to(loc)
            self.assertNotEqual(dist, float("inf"), f"Location '{loc}' is unreachable from {self.warehouse}")
            self.assertIsNotNone(path)
            self.assertEqual(path[0], self.warehouse)
            self.assertEqual(path[-1], loc)

        # Step 6: TSP Nearest Neighbor Route
        tsp_res = solve_tsp_nearest_neighbor(self.graph, self.warehouse, selected_locations)
        self.assertEqual(tsp_res.warehouse, self.warehouse)
        self.assertEqual(tsp_res.route_sequence[0], self.warehouse)
        self.assertEqual(tsp_res.route_sequence[-1], self.warehouse)
        self.assertGreater(tsp_res.total_distance_km, 0.0)
        self.assertEqual(len(tsp_res.unreachable_stops), 0)

        # Every unique target location must be visited in the route
        for loc in set(selected_locations):
            self.assertIn(loc, tsp_res.route_sequence)


if __name__ == "__main__":
    unittest.main()

