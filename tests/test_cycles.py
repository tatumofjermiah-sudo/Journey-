"""Tests for cycle definitions."""

import pytest
from architects_codex.cycles import (
    Cycle,
    CycleStatus,
    CycleType,
    ORDER_DEFINITIONS,
)


class TestCycleType:
    def test_all_five_orders_defined(self):
        assert set(CycleType) == {
            CycleType.FOUNDATIONS,
            CycleType.FRAMEWORKS,
            CycleType.TOWERS,
            CycleType.SYSTEMS,
            CycleType.METROPOLIS,
        }

    def test_hours_match_values(self):
        assert CycleType.FOUNDATIONS.hours == 12
        assert CycleType.FRAMEWORKS.hours == 24
        assert CycleType.TOWERS.hours == 48
        assert CycleType.SYSTEMS.hours == 72
        assert CycleType.METROPOLIS.hours == 144

    def test_display_name_capitalised(self):
        assert CycleType.FOUNDATIONS.display_name == "Foundations"
        assert CycleType.METROPOLIS.display_name == "Metropolis"


class TestOrderDefinitions:
    def test_all_orders_have_definitions(self):
        for ct in CycleType:
            assert ct in ORDER_DEFINITIONS

    def test_brick_values_increase_with_duration(self):
        bricks = [ORDER_DEFINITIONS[ct].brick_value for ct in CycleType]
        assert bricks == sorted(bricks), "Brick values should increase with cycle duration"

    def test_brick_values(self):
        expected = {
            CycleType.FOUNDATIONS: 1,
            CycleType.FRAMEWORKS: 3,
            CycleType.TOWERS: 6,
            CycleType.SYSTEMS: 12,
            CycleType.METROPOLIS: 30,
        }
        for ct, val in expected.items():
            assert ORDER_DEFINITIONS[ct].brick_value == val


class TestCycle:
    def test_initial_status_is_active(self):
        cycle = Cycle(cycle_type=CycleType.FOUNDATIONS)
        assert cycle.status == CycleStatus.ACTIVE

    def test_complete_sets_status(self):
        cycle = Cycle(cycle_type=CycleType.FOUNDATIONS)
        cycle.complete("done")
        assert cycle.status == CycleStatus.COMPLETED
        assert cycle.completed_at is not None
        assert cycle.notes == "done"

    def test_fail_sets_status(self):
        cycle = Cycle(cycle_type=CycleType.FOUNDATIONS)
        cycle.fail("gave up")
        assert cycle.status == CycleStatus.FAILED
        assert cycle.failed_at is not None
        assert cycle.notes == "gave up"

    def test_bricks_earned_only_on_completion(self):
        completed = Cycle(cycle_type=CycleType.FOUNDATIONS)
        completed.complete()
        assert completed.bricks_earned == 1

        failed = Cycle(cycle_type=CycleType.FOUNDATIONS)
        failed.fail()
        assert failed.bricks_earned == 0

        active = Cycle(cycle_type=CycleType.FOUNDATIONS)
        assert active.bricks_earned == 0

    def test_cannot_complete_twice(self):
        cycle = Cycle(cycle_type=CycleType.FOUNDATIONS)
        cycle.complete()
        with pytest.raises(ValueError):
            cycle.complete()

    def test_cannot_fail_completed_cycle(self):
        cycle = Cycle(cycle_type=CycleType.FOUNDATIONS)
        cycle.complete()
        with pytest.raises(ValueError):
            cycle.fail()

    def test_serialization_round_trip(self):
        cycle = Cycle(cycle_type=CycleType.SYSTEMS)
        cycle.complete("flow achieved")
        restored = Cycle.from_dict(cycle.to_dict())
        assert restored.cycle_type == cycle.cycle_type
        assert restored.status == cycle.status
        assert restored.notes == cycle.notes
        assert restored.completed_at == cycle.completed_at

    def test_failed_serialization_round_trip(self):
        cycle = Cycle(cycle_type=CycleType.TOWERS)
        cycle.fail("walls crumbled")
        restored = Cycle.from_dict(cycle.to_dict())
        assert restored.status == CycleStatus.FAILED
        assert restored.failed_at == cycle.failed_at
