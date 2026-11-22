"""
tests/test_knapsack.py
Unit tests for manual 0/1 Knapsack Dynamic Programming packing optimization.
"""

import unittest
from models.parcel import Parcel
from algorithms.knapsack import knapsack_01


class TestKnapsack(unittest.TestCase):

    def setUp(self):
        # Classic knapsack test case:
        # Items:
        # A: wt=2, val=3
        # B: wt=3, val=4
        # C: wt=4, val=5
        # D: wt=5, val=6
        # Capacity W=5: optimal subset is {A, B} with wt=5, val=7.
        self.pA = Parcel("PA", "A", "LocA", weight=2, priority=5, delivery_deadline=2, value=3.0)
        self.pB = Parcel("PB", "B", "LocB", weight=3, priority=5, delivery_deadline=2, value=4.0)
        self.pC = Parcel("PC", "C", "LocC", weight=4, priority=5, delivery_deadline=2, value=5.0)
        self.pD = Parcel("PD", "D", "LocD", weight=5, priority=5, delivery_deadline=2, value=6.0)

    def test_empty_input(self):
        """Empty parcels list should return 0 value and full remaining capacity."""
        result = knapsack_01([], capacity=50)
        self.assertEqual(result.total_value, 0.0)
        self.assertEqual(result.total_weight, 0)
        self.assertEqual(result.selected_parcels, [])
        self.assertEqual(result.remaining_capacity, 50)

    def test_zero_capacity(self):
        """Zero capacity should yield 0 selected parcels and 0 value."""
        result = knapsack_01([self.pA, self.pB], capacity=0)
        self.assertEqual(result.total_value, 0.0)
        self.assertEqual(result.total_weight, 0)
        self.assertEqual(result.selected_parcels, [])
        self.assertEqual(result.remaining_capacity, 0)

    def test_negative_capacity(self):
        """Negative capacity handled safely as 0 capacity."""
        result = knapsack_01([self.pA], capacity=-5)
        self.assertEqual(result.total_value, 0.0)
        self.assertEqual(result.selected_parcels, [])

    def test_single_parcel_fits(self):
        """Single parcel within capacity must be selected."""
        result = knapsack_01([self.pA], capacity=5)
        self.assertEqual(result.total_value, 3.0)
        self.assertEqual(result.total_weight, 2)
        self.assertEqual(result.selected_ids, ["PA"])
        self.assertEqual(result.remaining_capacity, 3)

    def test_single_parcel_exceeds_capacity(self):
        """Parcel heavier than capacity must not be selected."""
        heavy = Parcel("PH", "Heavy", "LocH", weight=15, priority=5, delivery_deadline=2, value=500.0)
        result = knapsack_01([heavy], capacity=10)
        self.assertEqual(result.total_value, 0.0)
        self.assertEqual(result.total_weight, 0)
        self.assertEqual(result.selected_parcels, [])
        self.assertEqual(result.remaining_capacity, 10)

    def test_optimal_subset_selection(self):
        """Tests classic DP selection where greedy would fail."""
        # Items: A(wt=2, val=3), B(wt=3, val=4), C(wt=4, val=5), D(wt=5, val=6)
        # Cap = 5: optimal is {A, B} total val=7, weight=5.
        parcels = [self.pA, self.pB, self.pC, self.pD]
        result = knapsack_01(parcels, capacity=5)
        self.assertEqual(result.total_value, 7.0)
        self.assertEqual(result.total_weight, 5)
        self.assertEqual(set(result.selected_ids), {"PA", "PB"})
        self.assertEqual(result.remaining_capacity, 0)

    def test_all_parcels_fit(self):
        """When total parcel weight <= capacity, all parcels should be selected."""
        parcels = [self.pA, self.pB]
        result = knapsack_01(parcels, capacity=100)
        self.assertEqual(result.total_value, 7.0)
        self.assertEqual(result.total_weight, 5)
        self.assertEqual(len(result.selected_parcels), 2)
        self.assertEqual(result.remaining_capacity, 95)

    def test_dp_table_dimensions(self):
        """DP table dimensions must strictly be (n+1) x (W+1)."""
        parcels = [self.pA, self.pB, self.pC]
        W = 10
        result = knapsack_01(parcels, capacity=W)
        self.assertEqual(len(result.dp_table), len(parcels) + 1)
        self.assertEqual(len(result.dp_table[0]), W + 1)
        self.assertEqual(result.dp_table[len(parcels)][W], result.total_value)


if __name__ == "__main__":
    unittest.main()

