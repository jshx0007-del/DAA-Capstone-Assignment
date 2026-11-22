"""
algorithms/sorting.py
Manual Merge Sort implementation for Parcel prioritization.

Sorting Criteria:
1. Higher priority first (descending order of priority).
2. Earlier delivery deadline first (ascending order of deadline).
3. Parcel ID as consistent tie-breaker (alphabetical / ascending order).

Complexities:
- Time Complexity: O(n log n) in all cases (Best, Average, Worst).
- Space Complexity: O(n) auxiliary space for merging.
- Stability: Maintained (equal elements retain relative order if no tie-breaker,
  and deterministic with tie-breaker).
"""

import time
from typing import List, Tuple
from models.parcel import Parcel


def comes_before(a: Parcel, b: Parcel) -> bool:
    """
    Comparator function to check if parcel 'a' should precede parcel 'b'.
    
    Rules:
    1. Higher priority first: a.priority > b.priority
    2. If priorities equal, earlier deadline first: a.delivery_deadline < b.delivery_deadline
    3. If deadlines equal, lexicographical order of parcel_id: a.parcel_id < b.parcel_id
    """
    if a.priority != b.priority:
        return a.priority > b.priority
    if a.delivery_deadline != b.delivery_deadline:
        return a.delivery_deadline < b.delivery_deadline
    return a.parcel_id < b.parcel_id


def merge(left: List[Parcel], right: List[Parcel]) -> List[Parcel]:
    """
    Merges two sorted lists of Parcels into a single sorted list.
    Auxiliary Space: O(len(left) + len(right)).
    """
    merged: List[Parcel] = []
    i = 0
    j = 0

    while i < len(left) and j < len(right):
        if comes_before(left[i], right[j]) or (
            left[i].priority == right[j].priority
            and left[i].delivery_deadline == right[j].delivery_deadline
            and left[i].parcel_id == right[j].parcel_id
        ):
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    # Append remaining elements from left or right
    while i < len(left):
        merged.append(left[i])
        i += 1

    while j < len(right):
        merged.append(right[j])
        j += 1

    return merged


def merge_sort(parcels: List[Parcel]) -> List[Parcel]:
    """
    Recursively divides and sorts a list of parcels using Merge Sort.
    
    Args:
        parcels: List of Parcel objects.
        
    Returns:
        A new sorted list of Parcel objects.
    """
    if len(parcels) <= 1:
        return list(parcels)

    mid = len(parcels) // 2
    left_half = merge_sort(parcels[:mid])
    right_half = merge_sort(parcels[mid:])

    return merge(left_half, right_half)


def sort_parcels_with_metrics(parcels: List[Parcel]) -> Tuple[List[Parcel], float]:
    """
    Executes manual Merge Sort on parcels and measures execution time.
    
    Args:
        parcels: List of Parcel objects.
        
    Returns:
        Tuple of (sorted_parcels, execution_time_seconds).
    """
    start_time = time.perf_counter()
    sorted_list = merge_sort(parcels)
    elapsed_time = time.perf_counter() - start_time
    return sorted_list, elapsed_time

