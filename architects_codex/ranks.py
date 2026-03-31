"""
Rank definitions for The Architects' Codex.

Ranks map to Districts inside the inner city.  Each rank title is a civic
role in the growing metropolis; attaining it means a district has been fully
constructed and is operational.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Rank(int, Enum):
    """
    Ranks earned through accumulated bricks and completed cycles.

    Each threshold represents a fully realized district in the inner city.
    Integer value equals the brick threshold required to attain the rank,
    which enables natural ordering comparisons (>, >=, <, <=).
    """

    APPRENTICE_LAYER = 0          # starting rank — unpaved ground
    COBBLESTONE_KEEPER = 5        # first district streets laid
    THIRD_GATE = 15               # third gate opened — towers rising
    SIXTH_PATH = 40               # six paths converge — frameworks integrated
    FLOW_KEEPER = 80              # keeper of flow — energy systems activated
    NINTH_CROWN = 140             # ninth crown — full crown district complete
    NINTH_SEAL = 220              # ninth seal — seal of the inner city forged
    SOVEREIGN_ARCHITECT = 350     # apex — autonomous, living metropolis

    @property
    def brick_threshold(self) -> int:
        return self.value

    @classmethod
    def for_bricks(cls, bricks: int) -> "Rank":
        """Return the highest rank the Architect has earned for *bricks*."""
        earned = cls.APPRENTICE_LAYER
        for rank in cls:
            if bricks >= rank.value:
                earned = rank
        return earned

    @classmethod
    def next_rank(cls, current: "Rank") -> Optional["Rank"]:
        """Return the rank immediately above *current*, or None at apex."""
        members = list(cls)
        idx = members.index(current)
        if idx + 1 < len(members):
            return members[idx + 1]
        return None


@dataclass
class RankDefinition:
    """Narrative and structural details for a rank."""

    rank: Rank
    district_name: str
    civic_title: str
    district_description: str
    district_symbol: str   # single ASCII glyph used in the city map


RANK_DEFINITIONS: dict[Rank, RankDefinition] = {
    Rank.APPRENTICE_LAYER: RankDefinition(
        rank=Rank.APPRENTICE_LAYER,
        district_name="Bare Ground",
        civic_title="Apprentice Architect",
        district_description=(
            "Unpaved earth — potential in every grain of soil. "
            "No structures exist yet, but the blueprint is alive in your mind."
        ),
        district_symbol=".",
    ),
    Rank.COBBLESTONE_KEEPER: RankDefinition(
        rank=Rank.COBBLESTONE_KEEPER,
        district_name="Cobblestone Quarter",
        civic_title="Cobblestone Keeper",
        district_description=(
            "The first streets are laid. Cobblestones of habit pave the way; "
            "daily practice creates predictable, stable ground."
        ),
        district_symbol=":",
    ),
    Rank.THIRD_GATE: RankDefinition(
        rank=Rank.THIRD_GATE,
        district_name="Gate District",
        civic_title="Keeper of the Third Gate",
        district_description=(
            "Three gates open — raw potential passes through discipline and "
            "emerges as intentional structure. Towers rise on the horizon."
        ),
        district_symbol="T",
    ),
    Rank.SIXTH_PATH: RankDefinition(
        rank=Rank.SIXTH_PATH,
        district_name="Sixfold Crossing",
        civic_title="Walker of the Sixth Path",
        district_description=(
            "Six roads merge at a single nexus. Frameworks and towers "
            "interlock; the city begins to feel intentional rather than "
            "accidental."
        ),
        district_symbol="X",
    ),
    Rank.FLOW_KEEPER: RankDefinition(
        rank=Rank.FLOW_KEEPER,
        district_name="Flow Canal District",
        civic_title="Keeper of Flow",
        district_description=(
            "Energy rivers run through the city. The 72 h Systems cycles have "
            "cut canals that distribute vitality across every district, "
            "making the city feel alive."
        ),
        district_symbol="~",
    ),
    Rank.NINTH_CROWN: RankDefinition(
        rank=Rank.NINTH_CROWN,
        district_name="Crown District",
        civic_title="Bearer of the Ninth Crown",
        district_description=(
            "The ninth crown district rises above all others — spires visible "
            "across the entire inner city. Mastery wears its crown openly "
            "and without apology."
        ),
        district_symbol="^",
    ),
    Rank.NINTH_SEAL: RankDefinition(
        rank=Rank.NINTH_SEAL,
        district_name="Sealed Citadel",
        civic_title="Holder of the Ninth Seal",
        district_description=(
            "The inner citadel is sealed — no external chaos can breach its "
            "walls. The Architect has proved structural integrity across "
            "every domain."
        ),
        district_symbol="#",
    ),
    Rank.SOVEREIGN_ARCHITECT: RankDefinition(
        rank=Rank.SOVEREIGN_ARCHITECT,
        district_name="The Apex Metropolis",
        civic_title="Sovereign Architect",
        district_description=(
            "Autonomous, alive, fully realized. The inner city breathes on "
            "its own. Every district hums with purpose; every canal flows "
            "with energy. You are its creator and its citizen."
        ),
        district_symbol="@",
    ),
}
