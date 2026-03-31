"""Tests for rank / district system."""

import pytest
from architects_codex.ranks import Rank, RANK_DEFINITIONS


class TestRank:
    def test_all_ranks_have_definitions(self):
        for rank in Rank:
            assert rank in RANK_DEFINITIONS

    def test_for_bricks_starts_at_apprentice(self):
        assert Rank.for_bricks(0) == Rank.APPRENTICE_LAYER
        assert Rank.for_bricks(4) == Rank.APPRENTICE_LAYER

    def test_for_bricks_cobblestone_keeper(self):
        assert Rank.for_bricks(5) == Rank.COBBLESTONE_KEEPER
        assert Rank.for_bricks(14) == Rank.COBBLESTONE_KEEPER

    def test_for_bricks_third_gate(self):
        assert Rank.for_bricks(15) == Rank.THIRD_GATE

    def test_for_bricks_sovereign_architect(self):
        assert Rank.for_bricks(350) == Rank.SOVEREIGN_ARCHITECT
        assert Rank.for_bricks(10000) == Rank.SOVEREIGN_ARCHITECT

    def test_rank_progression_is_monotone(self):
        thresholds = [r.brick_threshold for r in Rank]
        assert thresholds == sorted(thresholds), "Rank thresholds must increase monotonically"

    def test_next_rank_returns_higher_rank(self):
        nxt = Rank.next_rank(Rank.APPRENTICE_LAYER)
        assert nxt == Rank.COBBLESTONE_KEEPER

    def test_next_rank_at_apex_returns_none(self):
        assert Rank.next_rank(Rank.SOVEREIGN_ARCHITECT) is None

    def test_district_symbol_defined(self):
        for rank in Rank:
            defn = RANK_DEFINITIONS[rank]
            assert len(defn.district_symbol) >= 1


class TestRankDefinition:
    def test_civic_titles_are_unique(self):
        titles = [RANK_DEFINITIONS[r].civic_title for r in Rank]
        assert len(titles) == len(set(titles))

    def test_district_names_are_unique(self):
        names = [RANK_DEFINITIONS[r].district_name for r in Rank]
        assert len(names) == len(set(names))
