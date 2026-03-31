"""
City mechanics for The Architects' Codex.

The City is the living, visual representation of an Architect's progress.
Bricks are placed in districts; structural cracks accumulate on failure;
compound-mastery bridges and shortcuts unlock as the city matures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .cycles import CycleType, ORDER_DEFINITIONS
from .ranks import Rank, RANK_DEFINITIONS


# ---------------------------------------------------------------------------
# Infrastructure unlocks
# ---------------------------------------------------------------------------

@dataclass
class Infrastructure:
    """A piece of city infrastructure unlocked by hitting a milestone."""

    name: str
    description: str
    unlocked: bool = False
    unlock_condition: str = ""

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "unlocked": self.unlocked,
            "unlock_condition": self.unlock_condition,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Infrastructure":
        return cls(
            name=data["name"],
            description=data["description"],
            unlocked=data["unlocked"],
            unlock_condition=data.get("unlock_condition", ""),
        )


def _default_infrastructure() -> list[Infrastructure]:
    return [
        Infrastructure(
            name="Habit Plumbing",
            description="Underground pipes of routine that feed every district.",
            unlock_condition="Complete 3 Foundations cycles",
        ),
        Infrastructure(
            name="Framework Scaffolding",
            description="Metal skeleton that accelerates construction across the city.",
            unlock_condition="Complete 2 Frameworks cycles",
        ),
        Infrastructure(
            name="Resilience Walls",
            description="Thick outer walls that absorb shock and reduce crack severity.",
            unlock_condition="Complete 1 Towers cycle",
        ),
        Infrastructure(
            name="Energy Canals",
            description="Rivers of vitality flowing between all districts.",
            unlock_condition="Complete 1 Systems cycle",
        ),
        Infrastructure(
            name="Compound Bridge",
            description=(
                "A shortcut bridge: each completed cycle reduces fatigue for "
                "the next-tier cycle."
            ),
            unlock_condition="Complete 1 Towers cycle",
        ),
        Infrastructure(
            name="Defense Towers",
            description="Mental resilience towers that protect against future structural cracks.",
            unlock_condition="Reach rank Ninth Crown",
        ),
        Infrastructure(
            name="Autonomous Grid",
            description="Self-sustaining power grid; the city runs even when you rest.",
            unlock_condition="Reach rank Sovereign Architect",
        ),
    ]


# ---------------------------------------------------------------------------
# Structural crack
# ---------------------------------------------------------------------------

@dataclass
class StructuralCrack:
    """Damage caused by a failed cycle."""

    cycle_type: CycleType
    severity: int        # 1 = hairline, 2 = moderate, 3 = major
    repaired: bool = False
    repair_description: str = ""

    @property
    def severity_label(self) -> str:
        return {1: "hairline", 2: "moderate", 3: "major"}.get(self.severity, "unknown")

    def repair(self, description: str = "") -> None:
        self.repaired = True
        self.repair_description = description or "Repaired through renewed commitment."

    def to_dict(self) -> dict:
        return {
            "cycle_type": self.cycle_type.name,
            "severity": self.severity,
            "repaired": self.repaired,
            "repair_description": self.repair_description,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StructuralCrack":
        return cls(
            cycle_type=CycleType[data["cycle_type"]],
            severity=data["severity"],
            repaired=data["repaired"],
            repair_description=data.get("repair_description", ""),
        )

    @classmethod
    def crack_severity(cls, cycle_type: CycleType) -> int:
        """Higher-order cycles cause more severe cracks when failed."""
        severity_map = {
            CycleType.FOUNDATIONS: 1,
            CycleType.FRAMEWORKS: 1,
            CycleType.TOWERS: 2,
            CycleType.SYSTEMS: 2,
            CycleType.METROPOLIS: 3,
        }
        return severity_map[cycle_type]


# ---------------------------------------------------------------------------
# The City
# ---------------------------------------------------------------------------

@dataclass
class City:
    """
    The living inner city — a data model that grows with the Architect.

    Attributes
    ----------
    total_bricks:
        Cumulative bricks earned from completed cycles.
    cracks:
        List of structural cracks (from failed cycles) and their repair status.
    infrastructure:
        Pieces of city infrastructure that have been unlocked.
    district_counts:
        Number of completed cycles per CycleType, tracking district growth.
    flow_state_active:
        Whether the double-brick 'Flow State' bonus is currently active.
    """

    total_bricks: int = 0
    cracks: list[StructuralCrack] = field(default_factory=list)
    infrastructure: list[Infrastructure] = field(default_factory=_default_infrastructure)
    district_counts: dict[CycleType, int] = field(
        default_factory=lambda: {ct: 0 for ct in CycleType}
    )
    flow_state_active: bool = False

    # Aggregate completion counters per CycleType (needed for unlock checks)
    _completed_counts: dict[CycleType, int] = field(
        default_factory=lambda: {ct: 0 for ct in CycleType}
    )

    @property
    def rank(self) -> Rank:
        return Rank.for_bricks(self.total_bricks)

    @property
    def rank_definition(self):
        return RANK_DEFINITIONS[self.rank]

    @property
    def active_cracks(self) -> list[StructuralCrack]:
        return [c for c in self.cracks if not c.repaired]

    @property
    def stability(self) -> int:
        """
        Stability score 0–100.

        Each unrepaired crack reduces stability proportional to its severity.
        Defense Towers (if unlocked) halve crack impact.
        """
        total_severity = sum(c.severity for c in self.active_cracks)
        if self._is_unlocked("Defense Towers"):
            total_severity = total_severity // 2
        return max(0, 100 - total_severity * 5)

    def _is_unlocked(self, name: str) -> bool:
        for infra in self.infrastructure:
            if infra.name == name and infra.unlocked:
                return True
        return False

    def add_completed_cycle(self, cycle_type: CycleType, bonus_bricks: int = 0) -> int:
        """
        Record a completed cycle.

        Returns the total bricks awarded this cycle (base + bonus + flow state).
        """
        definition = ORDER_DEFINITIONS[cycle_type]
        bricks = definition.brick_value + bonus_bricks

        if self.flow_state_active:
            bricks *= 2
            self.flow_state_active = False   # consumed on use

        self.total_bricks += bricks
        self.district_counts[cycle_type] += 1
        self._completed_counts[cycle_type] += 1

        self._check_infrastructure_unlocks(cycle_type)
        self._check_flow_state_unlock(cycle_type)
        return bricks

    def add_crack(self, cycle_type: CycleType) -> StructuralCrack:
        """Record a structural crack from a failed cycle."""
        crack = StructuralCrack(
            cycle_type=cycle_type,
            severity=StructuralCrack.crack_severity(cycle_type),
        )
        self.cracks.append(crack)
        return crack

    def repair_crack(self, index: int, description: str = "") -> Optional[StructuralCrack]:
        """
        Repair the crack at *index* in the active_cracks list.

        Returns the repaired crack, or None if the index is out of range.
        """
        active = self.active_cracks
        if index < 0 or index >= len(active):
            return None
        active[index].repair(description)
        return active[index]

    # ------------------------------------------------------------------
    # Internal unlock helpers
    # ------------------------------------------------------------------

    def _check_infrastructure_unlocks(self, completed_type: CycleType) -> None:
        foundations_done = self._completed_counts[CycleType.FOUNDATIONS]
        frameworks_done = self._completed_counts[CycleType.FRAMEWORKS]
        towers_done = self._completed_counts[CycleType.TOWERS]
        systems_done = self._completed_counts[CycleType.SYSTEMS]

        if foundations_done >= 3:
            self._unlock("Habit Plumbing")
        if frameworks_done >= 2:
            self._unlock("Framework Scaffolding")
        if towers_done >= 1:
            self._unlock("Resilience Walls")
            self._unlock("Compound Bridge")
        if systems_done >= 1:
            self._unlock("Energy Canals")
        if self.rank >= Rank.NINTH_CROWN:
            self._unlock("Defense Towers")
        if self.rank >= Rank.SOVEREIGN_ARCHITECT:
            self._unlock("Autonomous Grid")

    def _check_flow_state_unlock(self, completed_type: CycleType) -> None:
        if completed_type == CycleType.SYSTEMS:
            self.flow_state_active = True

    def _unlock(self, name: str) -> None:
        for infra in self.infrastructure:
            if infra.name == name and not infra.unlocked:
                infra.unlocked = True

    # ------------------------------------------------------------------
    # Visualization
    # ------------------------------------------------------------------

    def render_map(self) -> str:
        """
        Return an ASCII map of the inner city, showing district density,
        active cracks, and infrastructure.
        """
        lines: list[str] = []
        lines.append("=" * 60)
        lines.append("  THE INNER CITY — ARCHITECT'S MAP")
        lines.append("=" * 60)

        rank_def = self.rank_definition
        lines.append(f"  Rank  : {rank_def.civic_title}")
        lines.append(f"  Bricks: {self.total_bricks}")
        lines.append(f"  Stability: {self.stability} / 100")
        if self.flow_state_active:
            lines.append("  *** FLOW STATE ACTIVE — next cycle earns double bricks ***")
        lines.append("")

        # Build a 5×12 grid representing districts
        grid = self._build_grid()
        lines.append("  Districts (each cell = one completed cycle):")
        lines.append("  " + "-" * 38)
        for row in grid:
            lines.append("  |" + "".join(row) + "|")
        lines.append("  " + "-" * 38)

        # Legend
        lines.append("")
        lines.append("  Legend:")
        for ct in CycleType:
            sym = RANK_DEFINITIONS[Rank.APPRENTICE_LAYER].district_symbol  # default
            count = self.district_counts[ct]
            lines.append(
                f"    [{ct.value:3d}h] {ct.display_name:<12} — {count} district(s) built"
            )

        # Cracks
        if self.active_cracks:
            lines.append("")
            lines.append(f"  ⚠  Structural Cracks ({len(self.active_cracks)} unrepaired):")
            for i, crack in enumerate(self.active_cracks):
                lines.append(
                    f"    [{i}] {crack.cycle_type.display_name} district — "
                    f"{crack.severity_label} crack"
                )

        # Infrastructure
        unlocked = [i for i in self.infrastructure if i.unlocked]
        if unlocked:
            lines.append("")
            lines.append("  ✓  Infrastructure unlocked:")
            for infra in unlocked:
                lines.append(f"    • {infra.name}: {infra.description}")

        locked = [i for i in self.infrastructure if not i.unlocked]
        if locked:
            lines.append("")
            lines.append("  ○  Infrastructure pending:")
            for infra in locked:
                lines.append(f"    · {infra.name} ({infra.unlock_condition})")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    def _build_grid(self) -> list[list[str]]:
        """Build a 5-row × 36-column character grid for the city map."""
        ROWS = 5
        COLS = 36
        grid = [["·"] * COLS for _ in range(ROWS)]

        # Fill columns left-to-right per cycle type, each type occupying
        # a dedicated band of columns proportional to brick value.
        col_bands = {
            CycleType.FOUNDATIONS: (0, 6),
            CycleType.FRAMEWORKS: (7, 13),
            CycleType.TOWERS: (14, 20),
            CycleType.SYSTEMS: (21, 27),
            CycleType.METROPOLIS: (28, 35),
        }
        symbols = {
            CycleType.FOUNDATIONS: "▪",
            CycleType.FRAMEWORKS: "▫",
            CycleType.TOWERS: "T",
            CycleType.SYSTEMS: "~",
            CycleType.METROPOLIS: "★",
        }
        crack_symbols = {
            CycleType.FOUNDATIONS: "/",
            CycleType.FRAMEWORKS: "/",
            CycleType.TOWERS: "X",
            CycleType.SYSTEMS: "X",
            CycleType.METROPOLIS: "✕",
        }

        for ct in CycleType:
            count = self.district_counts[ct]
            c_start, c_end = col_bands[ct]
            band_width = c_end - c_start + 1
            cells_per_completion = max(1, band_width * ROWS // max(count + 1, 1))
            filled = 0
            for r in range(ROWS):
                for c in range(c_start, c_end + 1):
                    if filled < count * max(1, (band_width * ROWS) // max(count, 1)):
                        grid[r][c] = symbols[ct]
                    filled += 1

        # Mark active cracks (overlay on top of filled cells)
        cracked_types = {c.cycle_type for c in self.active_cracks}
        for ct in cracked_types:
            c_start, c_end = col_bands[ct]
            mid_col = (c_start + c_end) // 2
            mid_row = ROWS // 2
            grid[mid_row][mid_col] = crack_symbols.get(ct, "!")

        return grid

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "total_bricks": self.total_bricks,
            "cracks": [c.to_dict() for c in self.cracks],
            "infrastructure": [i.to_dict() for i in self.infrastructure],
            "district_counts": {ct.name: v for ct, v in self.district_counts.items()},
            "_completed_counts": {ct.name: v for ct, v in self._completed_counts.items()},
            "flow_state_active": self.flow_state_active,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "City":
        city = cls()
        city.total_bricks = data.get("total_bricks", 0)
        city.cracks = [StructuralCrack.from_dict(c) for c in data.get("cracks", [])]
        city.infrastructure = [
            Infrastructure.from_dict(i) for i in data.get("infrastructure", [])
        ]
        raw_dc = data.get("district_counts", {})
        city.district_counts = {CycleType[k]: v for k, v in raw_dc.items()}
        raw_cc = data.get("_completed_counts", {})
        city._completed_counts = {CycleType[k]: v for k, v in raw_cc.items()}
        city.flow_state_active = data.get("flow_state_active", False)
        return city
