"""Tests for city building mechanics."""

import pytest
from architects_codex.city import City, StructuralCrack
from architects_codex.cycles import CycleType
from architects_codex.ranks import Rank


class TestCity:
    def setup_method(self):
        self.city = City()

    def test_initial_state(self):
        assert self.city.total_bricks == 0
        assert self.city.rank == Rank.APPRENTICE_LAYER
        assert self.city.stability == 100
        assert not self.city.active_cracks
        assert not self.city.flow_state_active

    def test_add_completed_cycle_adds_bricks(self):
        earned = self.city.add_completed_cycle(CycleType.FOUNDATIONS)
        assert earned == 1
        assert self.city.total_bricks == 1

    def test_add_completed_cycle_increments_district_count(self):
        self.city.add_completed_cycle(CycleType.FOUNDATIONS)
        assert self.city.district_counts[CycleType.FOUNDATIONS] == 1

    def test_rank_advances_with_bricks(self):
        # Add enough bricks for COBBLESTONE_KEEPER (threshold = 5)
        for _ in range(5):
            self.city.add_completed_cycle(CycleType.FOUNDATIONS)  # +1 brick each
        assert self.city.total_bricks == 5
        assert self.city.rank == Rank.COBBLESTONE_KEEPER

    def test_rank_third_gate(self):
        # Need 15 bricks — use FRAMEWORKS (3 bricks each) × 5
        for _ in range(5):
            self.city.add_completed_cycle(CycleType.FRAMEWORKS)
        assert self.city.total_bricks == 15
        assert self.city.rank == Rank.THIRD_GATE

    def test_crack_reduces_stability(self):
        self.city.add_crack(CycleType.FOUNDATIONS)  # severity 1
        assert self.city.stability < 100

    def test_multiple_cracks_reduce_stability_further(self):
        self.city.add_crack(CycleType.FOUNDATIONS)
        s1 = self.city.stability
        self.city.add_crack(CycleType.FOUNDATIONS)
        s2 = self.city.stability
        assert s2 < s1

    def test_repairing_crack_restores_stability(self):
        self.city.add_crack(CycleType.FOUNDATIONS)
        damaged_stability = self.city.stability
        self.city.repair_crack(0)
        assert self.city.stability > damaged_stability

    def test_repair_nonexistent_crack_returns_none(self):
        result = self.city.repair_crack(99)
        assert result is None

    def test_flow_state_activates_after_systems_completion(self):
        assert not self.city.flow_state_active
        self.city.add_completed_cycle(CycleType.SYSTEMS)
        assert self.city.flow_state_active

    def test_flow_state_doubles_bricks_and_resets(self):
        self.city.add_completed_cycle(CycleType.SYSTEMS)  # activates flow state
        assert self.city.flow_state_active
        initial_bricks = self.city.total_bricks
        # Next completion should earn double bricks
        bricks = self.city.add_completed_cycle(CycleType.FRAMEWORKS)  # base=3, doubled=6
        assert bricks == 6
        assert not self.city.flow_state_active  # consumed

    def test_infrastructure_unlocked_after_three_foundations(self):
        for _ in range(3):
            self.city.add_completed_cycle(CycleType.FOUNDATIONS)
        assert self.city._is_unlocked("Habit Plumbing")

    def test_infrastructure_not_unlocked_before_threshold(self):
        for _ in range(2):
            self.city.add_completed_cycle(CycleType.FOUNDATIONS)
        assert not self.city._is_unlocked("Habit Plumbing")

    def test_resilience_walls_unlocked_after_one_tower(self):
        self.city.add_completed_cycle(CycleType.TOWERS)
        assert self.city._is_unlocked("Resilience Walls")

    def test_energy_canals_unlocked_after_one_systems(self):
        self.city.add_completed_cycle(CycleType.SYSTEMS)
        assert self.city._is_unlocked("Energy Canals")

    def test_crack_severity_by_cycle_type(self):
        assert StructuralCrack.crack_severity(CycleType.FOUNDATIONS) == 1
        assert StructuralCrack.crack_severity(CycleType.FRAMEWORKS) == 1
        assert StructuralCrack.crack_severity(CycleType.TOWERS) == 2
        assert StructuralCrack.crack_severity(CycleType.SYSTEMS) == 2
        assert StructuralCrack.crack_severity(CycleType.METROPOLIS) == 3

    def test_serialization_round_trip(self):
        self.city.add_completed_cycle(CycleType.FOUNDATIONS)
        self.city.add_crack(CycleType.TOWERS)
        restored = City.from_dict(self.city.to_dict())
        assert restored.total_bricks == self.city.total_bricks
        assert len(restored.cracks) == len(self.city.cracks)
        assert restored.rank == self.city.rank

    def test_render_map_returns_string(self):
        output = self.city.render_map()
        assert isinstance(output, str)
        assert "INNER CITY" in output


class TestStructuralCrack:
    def test_crack_labels(self):
        crack = StructuralCrack(cycle_type=CycleType.FOUNDATIONS, severity=1)
        assert crack.severity_label == "hairline"
        crack.severity = 2
        assert crack.severity_label == "moderate"
        crack.severity = 3
        assert crack.severity_label == "major"

    def test_repair_crack(self):
        crack = StructuralCrack(cycle_type=CycleType.TOWERS, severity=2)
        assert not crack.repaired
        crack.repair("rebuilt with intention")
        assert crack.repaired
        assert crack.repair_description == "rebuilt with intention"

    def test_serialization_round_trip(self):
        crack = StructuralCrack(cycle_type=CycleType.METROPOLIS, severity=3)
        crack.repair("renewed")
        restored = StructuralCrack.from_dict(crack.to_dict())
        assert restored.cycle_type == crack.cycle_type
        assert restored.severity == crack.severity
        assert restored.repaired == crack.repaired
        assert restored.repair_description == crack.repair_description
