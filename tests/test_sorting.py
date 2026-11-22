"""
tests/test_sorting.py
Unit tests for manual Merge Sort parcel prioritization.
"""

import unittest
from models.parcel import Parcel
from algorithms.sorting import merge_sort, comes_before, sort_parcels_with_metrics


class TestMergeSort(unittest.TestCase):

    def setUp(self):
        self.p1 = Parcel("P01", "Alice", "LocA", weight=5, priority=10, delivery_deadline=2, value=100.0)
        self.p2 = Parcel("P02", "Bob", "LocB", weight=3, priority=8, delivery_deadline=1, value=200.0)
        self.p3 = Parcel("P03", "Charlie", "LocC", weight=4, priority=8, delivery_deadline=3, value=150.0)
        self.p4 = Parcel("P04", "David", "LocD", weight=2, priority=8, delivery_deadline=1, value=80.0)

    def test_empty_list(self):
        """Test sorting an empty parcel list."""
        sorted_list = merge_sort([])
        self.assertEqual(sorted_list, [])

    def test_single_parcel(self):
        """Test sorting a list with a single parcel."""
        sorted_list = merge_sort([self.p1])
        self.assertEqual(len(sorted_list), 1)
        self.assertEqual(sorted_list[0].parcel_id, "P01")

    def test_multiple_parcels_priority_order(self):
        """Higher priority must precede lower priority."""
        parcels = [self.p2, self.p1]  # P02 (prio 8), P01 (prio 10)
        sorted_list = merge_sort(parcels)
        self.assertEqual([p.parcel_id for p in sorted_list], ["P01", "P02"])

    def test_equal_priority_different_deadlines(self):
        """When priorities are equal, earlier deadline (smaller value) comes first."""
        # P02: prio 8, deadline 1; P03: prio 8, deadline 3
        parcels = [self.p3, self.p2]
        sorted_list = merge_sort(parcels)
        self.assertEqual([p.parcel_id for p in sorted_list], ["P02", "P03"])

    def test_equal_priority_and_deadline_tiebreaker(self):
        """When priority and deadline are identical, parcel_id is the tie-breaker."""
        # P02: prio 8, dline 1, id 'P02'; P04: prio 8, dline 1, id 'P04'
        parcels = [self.p4, self.p2]
        sorted_list = merge_sort(parcels)
        self.assertEqual([p.parcel_id for p in sorted_list], ["P02", "P04"])

    def test_reverse_sorted_and_already_sorted(self):
        """Verify consistency on reverse sorted and sorted lists."""
        all_parcels = [self.p1, self.p2, self.p4, self.p3]  # already in correct order: 10, 8(d1,id2), 8(d1,id4), 8(d3)
        rev = list(reversed(all_parcels))
        sorted_rev = merge_sort(rev)
        self.assertEqual([p.parcel_id for p in sorted_rev], ["P01", "P02", "P04", "P03"])

    def test_metrics_function(self):
        """Verify sorting with metrics returns non-negative time."""
        sorted_list, elapsed = sort_parcels_with_metrics([self.p3, self.p1])
        self.assertEqual(len(sorted_list), 2)
        self.assertGreaterEqual(elapsed, 0.0)

    def test_large_dataset(self):
        """Test with 1000 parcels to ensure O(n log n) stability."""
        large_parcels = [
            Parcel(f"P{i:04d}", f"Cust {i}", "Loc", weight=5, priority=i % 10, delivery_deadline=(i % 5) + 1, value=100.0)
            for i in range(1000)
        ]
        sorted_list = merge_sort(large_parcels)
        self.assertEqual(len(sorted_list), 1000)
        # Verify monotonically non-increasing priority, or if equal, non-decreasing deadline
        for k in range(len(sorted_list) - 1):
            a, b = sorted_list[k], sorted_list[k + 1]
            self.assertTrue(
                (a.priority > b.priority) or
                (a.priority == b.priority and a.delivery_deadline < b.delivery_deadline) or
                (a.priority == b.priority and a.delivery_deadline == b.delivery_deadline and a.parcel_id <= b.parcel_id)
            )


if __name__ == "__main__":
    unittest.main()

