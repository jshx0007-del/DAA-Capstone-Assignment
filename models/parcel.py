"""
models/parcel.py
Data model representing a parcel to be prioritized, packed, and delivered.
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Parcel:
    """
    Represents a parcel in the courier delivery system.

    Attributes:
        parcel_id: Unique identifier for the parcel (e.g., 'P101').
        customer_name: Name of the recipient.
        delivery_location: Node/location in the delivery network.
        weight: Weight of the parcel in kilograms (integer for knapsack DP).
        priority: Priority rank (higher number = higher priority, e.g., 10 > 1).
        delivery_deadline: Deadline in hours (e.g., 2 = within 2 hours; lower = more urgent).
        value: Monetary or service value (profit) earned upon successful delivery.
    """
    parcel_id: str
    customer_name: str
    delivery_location: str
    weight: int
    priority: int
    delivery_deadline: int
    value: float

    def __post_init__(self):
        if self.weight < 0:
            raise ValueError(f"Parcel weight cannot be negative: {self.weight}")
        if self.priority < 0:
            raise ValueError(f"Parcel priority cannot be negative: {self.priority}")
        if self.delivery_deadline < 0:
            raise ValueError(f"Parcel deadline cannot be negative: {self.delivery_deadline}")
        if self.value < 0:
            raise ValueError(f"Parcel value cannot be negative: {self.value}")
        # Ensure weight is integer for exact 0/1 knapsack DP indexing
        self.weight = int(self.weight)

    def to_dict(self) -> Dict[str, Any]:
        """Convert parcel to dictionary representation."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Parcel":
        """Instantiate Parcel from a dictionary."""
        return cls(
            parcel_id=str(data["parcel_id"]),
            customer_name=str(data["customer_name"]),
            delivery_location=str(data["delivery_location"]),
            weight=int(data["weight"]),
            priority=int(data["priority"]),
            delivery_deadline=int(data["delivery_deadline"]),
            value=float(data["value"])
        )

    def __repr__(self) -> str:
        return (
            f"Parcel({self.parcel_id}, {self.customer_name}, loc='{self.delivery_location}', "
            f"wt={self.weight}kg, prio={self.priority}, dline={self.delivery_deadline}h, val=₹{self.value:.0f})"
        )

