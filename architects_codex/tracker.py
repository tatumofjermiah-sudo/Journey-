"""
Cycle tracker for The Architects' Codex.

The tracker orchestrates the lifecycle of cycles, persists state to a JSON
file, applies compound-mastery bonuses, and delegates city updates to the
City model.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .city import City
from .cycles import Cycle, CycleStatus, CycleType


# Default save path (overridable for tests)
DEFAULT_SAVE_PATH = Path.home() / ".architects_codex" / "state.json"


@dataclass
class CompoundBonus:
    """Records a compound-mastery bonus that is queued for the next cycle."""

    source_type: CycleType
    bonus_bricks: int
    description: str
    consumed: bool = False


@dataclass
class CycleTracker:
    """
    Manages the full lifecycle of cycles and city state.

    Attributes
    ----------
    city:
        The living inner city model.
    history:
        All past cycles (completed + failed).
    active_cycle:
        The cycle currently in progress, if any.
    pending_bonuses:
        Compound-mastery bonuses waiting to be applied to the next completion.
    save_path:
        Where to persist state as JSON.
    """

    city: City = field(default_factory=City)
    history: list[Cycle] = field(default_factory=list)
    active_cycle: Optional[Cycle] = None
    pending_bonuses: list[CompoundBonus] = field(default_factory=list)
    save_path: Path = field(default_factory=lambda: DEFAULT_SAVE_PATH)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start_cycle(self, cycle_type: CycleType) -> Cycle:
        """
        Start a new active cycle.

        Raises
        ------
        RuntimeError
            If a cycle is already in progress.
        """
        if self.active_cycle is not None and self.active_cycle.status == CycleStatus.ACTIVE:
            raise RuntimeError(
                f"A {self.active_cycle.cycle_type.display_name} cycle is already active. "
                "Complete or fail it before starting a new one."
            )
        cycle = Cycle(cycle_type=cycle_type)
        self.active_cycle = cycle
        self.save()
        return cycle

    def complete_cycle(self, notes: str = "") -> Cycle:
        """
        Mark the active cycle as completed and update the city.

        Returns the completed cycle.
        """
        self._require_active()
        cycle = self.active_cycle
        cycle.complete(notes)

        # Collect pending bonuses applicable to this cycle type
        bonus_bricks = self._consume_bonuses(cycle.cycle_type)
        cycle.bonus_bricks = bonus_bricks

        # Update city (flow-state doubling happens inside add_completed_cycle)
        self.city.add_completed_cycle(cycle.cycle_type, bonus_bricks)

        # Queue compound bonuses for future cycles
        self._queue_compound_bonus(cycle.cycle_type)

        self.history.append(cycle)
        self.active_cycle = None
        self.save()
        return cycle

    def fail_cycle(self, notes: str = "") -> Cycle:
        """
        Mark the active cycle as failed and record a structural crack.

        Returns the failed cycle.
        """
        self._require_active()
        cycle = self.active_cycle
        cycle.fail(notes)

        crack = self.city.add_crack(cycle.cycle_type)

        self.history.append(cycle)
        self.active_cycle = None
        self.save()
        return cycle

    def repair_crack(self, index: int, description: str = "") -> bool:
        """
        Attempt to repair the crack at *index* in the active crack list.

        Returns True if successful.
        """
        crack = self.city.repair_crack(index, description)
        if crack is not None:
            self.save()
            return True
        return False

    def summary(self) -> dict:
        """Return a plain-dict summary of current progress."""
        rank_def = self.city.rank_definition
        next_rank = self.city.rank.__class__.next_rank(self.city.rank)
        bricks_to_next = (
            next_rank.brick_threshold - self.city.total_bricks
            if next_rank else 0
        )
        return {
            "rank": rank_def.civic_title,
            "district": rank_def.district_name,
            "total_bricks": self.city.total_bricks,
            "stability": self.city.stability,
            "active_cracks": len(self.city.active_cracks),
            "flow_state": self.city.flow_state_active,
            "completed_cycles": sum(
                1 for c in self.history if c.status == CycleStatus.COMPLETED
            ),
            "failed_cycles": sum(
                1 for c in self.history if c.status == CycleStatus.FAILED
            ),
            "next_rank": next_rank.name if next_rank else "MAX",
            "bricks_to_next_rank": bricks_to_next,
            "district_counts": {
                ct.display_name: self.city.district_counts[ct] for ct in CycleType
            },
        }

    # ------------------------------------------------------------------
    # Compound-mastery bonus helpers
    # ------------------------------------------------------------------

    def _queue_compound_bonus(self, completed_type: CycleType) -> None:
        """After a completion, queue bonuses for future higher-tier cycles."""
        # Foundations → Frameworks: small fatigue reduction represented as +1 brick
        if completed_type == CycleType.FOUNDATIONS:
            self.pending_bonuses.append(
                CompoundBonus(
                    source_type=CycleType.FOUNDATIONS,
                    bonus_bricks=1,
                    description="Foundations compound bonus: +1 brick on next Frameworks cycle.",
                )
            )
        # Frameworks → Towers: +1 structural bonus brick
        elif completed_type == CycleType.FRAMEWORKS:
            self.pending_bonuses.append(
                CompoundBonus(
                    source_type=CycleType.FRAMEWORKS,
                    bonus_bricks=2,
                    description="Frameworks compound bonus: +2 bricks on next Towers cycle.",
                )
            )
        # Towers → Systems: bridge shortcut represented as +3 bricks
        elif completed_type == CycleType.TOWERS:
            self.pending_bonuses.append(
                CompoundBonus(
                    source_type=CycleType.TOWERS,
                    bonus_bricks=3,
                    description="Tower bridge bonus: +3 bricks on next Systems cycle.",
                )
            )

    def _consume_bonuses(self, cycle_type: CycleType) -> int:
        """
        Consume all pending bonuses applicable to *cycle_type*.

        Bonuses stack for the next higher tier only (one step up).
        """
        tier_map = {
            CycleType.FRAMEWORKS: CycleType.FOUNDATIONS,
            CycleType.TOWERS: CycleType.FRAMEWORKS,
            CycleType.SYSTEMS: CycleType.TOWERS,
        }
        qualifying_source = tier_map.get(cycle_type)
        total = 0
        for bonus in self.pending_bonuses:
            if not bonus.consumed and bonus.source_type == qualifying_source:
                total += bonus.bonus_bricks
                bonus.consumed = True
        # Remove consumed bonuses
        self.pending_bonuses = [b for b in self.pending_bonuses if not b.consumed]
        return total

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self) -> None:
        """Persist the current state to *save_path* as JSON."""
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "city": self.city.to_dict(),
            "history": [c.to_dict() for c in self.history],
            "active_cycle": self.active_cycle.to_dict() if self.active_cycle else None,
            "pending_bonuses": [
                {
                    "source_type": b.source_type.name,
                    "bonus_bricks": b.bonus_bricks,
                    "description": b.description,
                    "consumed": b.consumed,
                }
                for b in self.pending_bonuses
            ],
        }
        self.save_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, save_path: Path = DEFAULT_SAVE_PATH) -> "CycleTracker":
        """Load state from *save_path*, or return a fresh tracker if missing."""
        if not save_path.exists():
            return cls(save_path=save_path)
        raw = json.loads(save_path.read_text(encoding="utf-8"))
        tracker = cls(save_path=save_path)
        tracker.city = City.from_dict(raw.get("city", {}))
        tracker.history = [Cycle.from_dict(c) for c in raw.get("history", [])]
        active_raw = raw.get("active_cycle")
        tracker.active_cycle = Cycle.from_dict(active_raw) if active_raw else None
        tracker.pending_bonuses = [
            CompoundBonus(
                source_type=CycleType[b["source_type"]],
                bonus_bricks=b["bonus_bricks"],
                description=b["description"],
                consumed=b.get("consumed", False),
            )
            for b in raw.get("pending_bonuses", [])
        ]
        return tracker

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_active(self) -> None:
        if self.active_cycle is None or self.active_cycle.status != CycleStatus.ACTIVE:
            raise RuntimeError("No active cycle. Start one with start_cycle().")

