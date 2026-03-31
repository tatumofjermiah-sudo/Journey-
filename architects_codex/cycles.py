"""
Cycle definitions for The Architects' Codex.

Each cycle represents both a timed trial and a symbolic construction zone
in the Architect's inner city.  Completing a cycle produces a building unit
("brick") that slots into the city's growing structure.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class CycleType(Enum):
    """The five Orders of construction."""

    FOUNDATIONS = 12    # hours
    FRAMEWORKS = 24
    TOWERS = 48
    SYSTEMS = 72
    METROPOLIS = 144

    @property
    def hours(self) -> int:
        return self.value

    @property
    def display_name(self) -> str:
        return self.name.replace("_", " ").title()


class CycleStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class OrderDefinition:
    """Static description of a cycle type (Order)."""

    cycle_type: CycleType
    order_name: str
    construction_metaphor: str
    scaffolding_description: str
    brick_value: int          # bricks awarded on completion
    bonus_description: str    # compound-mastery bonus hint

    @property
    def hours(self) -> int:
        return self.cycle_type.hours


ORDER_DEFINITIONS: dict[CycleType, OrderDefinition] = {
    CycleType.FOUNDATIONS: OrderDefinition(
        cycle_type=CycleType.FOUNDATIONS,
        order_name="First Order — Foundations",
        construction_metaphor=(
            "Beginner streets, cobblestones of habit. You lay the streets and "
            "install the plumbing of discipline."
        ),
        scaffolding_description=(
            "12 hours — Time is your first scaffold. Respect it and the "
            "cobblestones hold firm."
        ),
        brick_value=1,
        bonus_description="Completing Foundations cycles reduces Framework fatigue by 5 %.",
    ),
    CycleType.FRAMEWORKS: OrderDefinition(
        cycle_type=CycleType.FRAMEWORKS,
        order_name="Second Order — Frameworks",
        construction_metaphor=(
            "Skeleton towers, shaping rhythm and control. You erect the "
            "skeletal structure of your inner towers."
        ),
        scaffolding_description=(
            "24 hours — Hunger is your material; scarcity teaches resource "
            "management and structural precision."
        ),
        brick_value=3,
        bonus_description="Each Framework completion grants +1 structural bonus brick to the nearest active Tower.",
    ),
    CycleType.TOWERS: OrderDefinition(
        cycle_type=CycleType.TOWERS,
        order_name="Third Order — Towers",
        construction_metaphor=(
            "Resilient walls, holding against internal chaos. You build the "
            "walls of resilience and floors of endurance."
        ),
        scaffolding_description=(
            "48 hours — Mind is your blueprint; planning without understanding "
            "leads to collapse."
        ),
        brick_value=6,
        bonus_description="Completing a Tower cycle opens a bridge shortcut, reducing the next Systems cycle by 4 h.",
    ),
    CycleType.SYSTEMS: OrderDefinition(
        cycle_type=CycleType.SYSTEMS,
        order_name="Fourth Order — Systems",
        construction_metaphor=(
            "Integrated systems, energy canals connecting all districts. "
            "Body, mind, and energy flow as one."
        ),
        scaffolding_description=(
            "72 hours — Cycles are repetition; structural integrity requires "
            "consistent reinforcement."
        ),
        brick_value=12,
        bonus_description="Systems completion unlocks 'Flow State': next cycle earns double bricks.",
    ),
    CycleType.METROPOLIS: OrderDefinition(
        cycle_type=CycleType.METROPOLIS,
        order_name="Fifth Order — Metropolis",
        construction_metaphor=(
            "Apex metropolis, autonomous, alive, fully realized. You construct "
            "a self-sustaining inner civilization."
        ),
        scaffolding_description=(
            "144 hours — The city breathes on its own; you are its Architect "
            "and its citizen."
        ),
        brick_value=30,
        bonus_description="Metropolis completion crowns a full district and permanently raises baseline resilience.",
    ),
}


@dataclass
class Cycle:
    """A single active, completed, or failed cycle instance."""

    cycle_type: CycleType
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    status: CycleStatus = CycleStatus.ACTIVE
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    notes: str = ""

    # Bonus bricks awarded via compound-mastery mechanics
    bonus_bricks: int = 0

    @property
    def definition(self) -> OrderDefinition:
        return ORDER_DEFINITIONS[self.cycle_type]

    @property
    def bricks_earned(self) -> int:
        """Bricks earned if completed; 0 if failed or still active."""
        if self.status == CycleStatus.COMPLETED:
            return self.definition.brick_value + self.bonus_bricks
        return 0

    @property
    def elapsed_hours(self) -> float:
        end = self.completed_at or self.failed_at or datetime.now(timezone.utc)
        delta = end - self.started_at
        return delta.total_seconds() / 3600

    def complete(self, notes: str = "") -> None:
        """Mark this cycle as successfully completed."""
        if self.status != CycleStatus.ACTIVE:
            raise ValueError(f"Cannot complete a cycle with status '{self.status.value}'.")
        self.status = CycleStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.notes = notes

    def fail(self, notes: str = "") -> None:
        """Mark this cycle as failed (structural crack)."""
        if self.status != CycleStatus.ACTIVE:
            raise ValueError(f"Cannot fail a cycle with status '{self.status.value}'.")
        self.status = CycleStatus.FAILED
        self.failed_at = datetime.now(timezone.utc)
        self.notes = notes

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cycle_type": self.cycle_type.name,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None,
            "bonus_bricks": self.bonus_bricks,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Cycle":
        def _parse_dt(val: Optional[str]) -> Optional[datetime]:
            if val is None:
                return None
            dt = datetime.fromisoformat(val)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt

        return cls(
            id=data["id"],
            cycle_type=CycleType[data["cycle_type"]],
            status=CycleStatus(data["status"]),
            started_at=_parse_dt(data["started_at"]),
            completed_at=_parse_dt(data.get("completed_at")),
            failed_at=_parse_dt(data.get("failed_at")),
            bonus_bricks=data.get("bonus_bricks", 0),
            notes=data.get("notes", ""),
        )
