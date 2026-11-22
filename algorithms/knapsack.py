"""
algorithms/knapsack.py
Manual 0/1 Knapsack Dynamic Programming implementation for vehicle packing optimization.

Given a list of parcels (each with an integer weight and value/profit) and a maximum
vehicle load capacity W, select a subset of parcels to maximize total value without
exceeding W.

Complexities:
- Time Complexity: O(n * W)
- Space Complexity: O(n * W) for the 2D DP table.
"""

import time
from typing import List, Dict, Any, Tuple
from models.parcel import Parcel


class KnapsackResult:
    """Encapsulates the result of the 0/1 Knapsack optimization."""

    def __init__(
        self,
        dp_table: List[List[float]],
        selected_parcels: List[Parcel],
        total_weight: int,
        total_value: float,
        remaining_capacity: int,
        execution_time: float,
        capacity: int,
        input_parcels: List[Parcel]
    ):
        self.dp_table = dp_table
        self.selected_parcels = selected_parcels
        self.total_weight = total_weight
        self.total_value = total_value
        self.remaining_capacity = remaining_capacity
        self.execution_time = execution_time
        self.capacity = capacity
        self.input_parcels = input_parcels

    @property
    def selected_ids(self) -> List[str]:
        return [p.parcel_id for p in self.selected_parcels]

    def summary(self) -> Dict[str, Any]:
        return {
            "capacity": self.capacity,
            "total_weight": self.total_weight,
            "total_value": self.total_value,
            "remaining_capacity": self.remaining_capacity,
            "selected_count": len(self.selected_parcels),
            "selected_ids": self.selected_ids,
            "execution_time_ms": self.execution_time * 1000
        }


def knapsack_01(parcels: List[Parcel], capacity: int) -> KnapsackResult:
    """
    Solves the 0/1 Knapsack problem manually constructing a 2D dynamic programming table.

    Args:
        parcels: List of Parcel objects.
        capacity: Maximum integer capacity (weight) of the delivery vehicle.

    Returns:
        KnapsackResult containing DP table, selected parcels, totals, and execution time.
    """
    start_time = time.perf_counter()

    # Edge cases: zero capacity or empty parcel list or negative capacity
    if capacity <= 0 or not parcels:
        elapsed = time.perf_counter() - start_time
        empty_table = [[0.0] * (max(0, capacity) + 1)] if capacity >= 0 else [[0.0]]
        return KnapsackResult(
            dp_table=empty_table,
            selected_parcels=[],
            total_weight=0,
            total_value=0.0,
            remaining_capacity=max(0, capacity),
            execution_time=elapsed,
            capacity=max(0, capacity),
            input_parcels=parcels
        )

    n = len(parcels)
    W = int(capacity)

    # Step 1: Initialize (n + 1) x (W + 1) table with 0.0
    # dp[i][w] holds the maximum value using a subset of the first i parcels with weight limit w.
    dp = [[0.0 for _ in range(W + 1)] for _ in range(n + 1)]

    # Step 2: Fill DP table row by row
    for i in range(1, n + 1):
        parcel = parcels[i - 1]
        wt = parcel.weight
        val = parcel.value

        for w in range(W + 1):
            if wt <= w:
                # Choice: exclude parcel (dp[i-1][w]) OR include parcel (dp[i-1][w - wt] + val)
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - wt] + val)
            else:
                # Parcel is too heavy for current capacity w
                dp[i][w] = dp[i - 1][w]

    # Step 3: Backtrack to reconstruct the optimal subset of chosen parcels
    selected_parcels: List[Parcel] = []
    w_curr = W

    for i in range(n, 0, -1):
        # If the value came from including item i-1
        if dp[i][w_curr] != dp[i - 1][w_curr]:
            chosen = parcels[i - 1]
            selected_parcels.append(chosen)
            w_curr -= chosen.weight

    # Reverse to maintain original order
    selected_parcels.reverse()

    total_weight = sum(p.weight for p in selected_parcels)
    total_value = dp[n][W]
    remaining_capacity = W - total_weight
    elapsed = time.perf_counter() - start_time

    return KnapsackResult(
        dp_table=dp,
        selected_parcels=selected_parcels,
        total_weight=total_weight,
        total_value=total_value,
        remaining_capacity=remaining_capacity,
        execution_time=elapsed,
        capacity=W,
        input_parcels=parcels
    )

