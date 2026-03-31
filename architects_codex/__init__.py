"""
The Architects' Codex — A symbolic fasting and discipline tracking system.

Every cycle is both a literal trial and a metaphysical brick in the
construction of your inner city. Completing cycles builds districts;
failure creates structural cracks that must be carefully repaired.
"""

from .cycles import Cycle, CycleType, ORDER_DEFINITIONS
from .ranks import Rank, RANK_DEFINITIONS
from .city import City
from .tracker import CycleTracker

__all__ = [
    "Cycle",
    "CycleType",
    "ORDER_DEFINITIONS",
    "Rank",
    "RANK_DEFINITIONS",
    "City",
    "CycleTracker",
]
