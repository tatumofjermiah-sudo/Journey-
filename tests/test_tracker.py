"""Tests for the cycle tracker."""

import json
import tempfile
from pathlib import Path

import pytest
from architects_codex.cycles import CycleStatus, CycleType
from architects_codex.tracker import CycleTracker


def make_tracker(tmp_path: Path) -> CycleTracker:
    """Return a fresh tracker that persists to a temp file."""
    save = tmp_path / "state.json"
    return CycleTracker(save_path=save)


class TestCycleTrackerBasics:
    def test_start_cycle_creates_active(self, tmp_path):
        tracker = make_tracker(tmp_path)
        cycle = tracker.start_cycle(CycleType.FOUNDATIONS)
        assert cycle.status == CycleStatus.ACTIVE
        assert tracker.active_cycle is cycle

    def test_cannot_start_two_cycles(self, tmp_path):
        tracker = make_tracker(tmp_path)
        tracker.start_cycle(CycleType.FOUNDATIONS)
        with pytest.raises(RuntimeError):
            tracker.start_cycle(CycleType.FRAMEWORKS)

    def test_complete_cycle(self, tmp_path):
        tracker = make_tracker(tmp_path)
        tracker.start_cycle(CycleType.FOUNDATIONS)
        cycle = tracker.complete_cycle("first cobblestones")
        assert cycle.status == CycleStatus.COMPLETED
        assert tracker.active_cycle is None
        assert tracker.city.total_bricks == 1
        assert len(tracker.history) == 1

    def test_fail_cycle_creates_crack(self, tmp_path):
        tracker = make_tracker(tmp_path)
        tracker.start_cycle(CycleType.TOWERS)
        tracker.fail_cycle("walls crumbled")
        assert len(tracker.city.cracks) == 1
        assert tracker.city.cracks[0].cycle_type == CycleType.TOWERS
        assert tracker.active_cycle is None

    def test_fail_requires_active_cycle(self, tmp_path):
        tracker = make_tracker(tmp_path)
        with pytest.raises(RuntimeError):
            tracker.fail_cycle()

    def test_complete_requires_active_cycle(self, tmp_path):
        tracker = make_tracker(tmp_path)
        with pytest.raises(RuntimeError):
            tracker.complete_cycle()

    def test_repair_crack(self, tmp_path):
        tracker = make_tracker(tmp_path)
        tracker.start_cycle(CycleType.FOUNDATIONS)
        tracker.fail_cycle()
        assert len(tracker.city.active_cracks) == 1
        result = tracker.repair_crack(0)
        assert result is True
        assert len(tracker.city.active_cracks) == 0

    def test_repair_nonexistent_crack(self, tmp_path):
        tracker = make_tracker(tmp_path)
        result = tracker.repair_crack(99)
        assert result is False


class TestCompoundBonuses:
    def test_foundations_queues_bonus_for_frameworks(self, tmp_path):
        tracker = make_tracker(tmp_path)
        tracker.start_cycle(CycleType.FOUNDATIONS)
        tracker.complete_cycle()
        assert len(tracker.pending_bonuses) == 1
        assert tracker.pending_bonuses[0].source_type == CycleType.FOUNDATIONS

    def test_bonus_applied_on_next_tier(self, tmp_path):
        tracker = make_tracker(tmp_path)
        # Complete foundations to queue bonus
        tracker.start_cycle(CycleType.FOUNDATIONS)
        tracker.complete_cycle()  # queues +1 bonus for Frameworks

        # Now complete frameworks — should get base 3 + bonus 1 = 4 bricks
        tracker.start_cycle(CycleType.FRAMEWORKS)
        cycle = tracker.complete_cycle()
        # City bricks: 1 (foundations) + 4 (frameworks w/ bonus) = 5
        assert tracker.city.total_bricks == 5
        # No pending bonuses for Foundations→Frameworks should remain
        foundations_bonuses = [
            b for b in tracker.pending_bonuses
            if b.source_type == CycleType.FOUNDATIONS
        ]
        assert not foundations_bonuses

    def test_bonus_not_applied_to_wrong_tier(self, tmp_path):
        tracker = make_tracker(tmp_path)
        # Queue foundations bonus
        tracker.start_cycle(CycleType.FOUNDATIONS)
        tracker.complete_cycle()
        # Complete another foundations — bonus should NOT be consumed
        tracker.start_cycle(CycleType.FOUNDATIONS)
        tracker.complete_cycle()
        # Both foundations completions queue bonuses; neither consumes the other
        foundations_bonuses = [
            b for b in tracker.pending_bonuses
            if b.source_type == CycleType.FOUNDATIONS
        ]
        assert len(foundations_bonuses) == 2  # both still pending


class TestPersistence:
    def test_save_and_reload(self, tmp_path):
        save = tmp_path / "state.json"
        tracker = CycleTracker(save_path=save)
        tracker.start_cycle(CycleType.FOUNDATIONS)
        tracker.complete_cycle("saved")

        # Load fresh
        loaded = CycleTracker.load(save)
        assert loaded.city.total_bricks == 1
        assert len(loaded.history) == 1
        assert loaded.active_cycle is None

    def test_load_missing_file_returns_fresh(self, tmp_path):
        save = tmp_path / "nonexistent.json"
        tracker = CycleTracker.load(save)
        assert tracker.city.total_bricks == 0
        assert not tracker.history

    def test_save_creates_parent_directory(self, tmp_path):
        save = tmp_path / "subdir" / "deep" / "state.json"
        tracker = CycleTracker(save_path=save)
        tracker.start_cycle(CycleType.FOUNDATIONS)
        tracker.complete_cycle()
        assert save.exists()

    def test_active_cycle_persists(self, tmp_path):
        save = tmp_path / "state.json"
        tracker = CycleTracker(save_path=save)
        tracker.start_cycle(CycleType.TOWERS)
        loaded = CycleTracker.load(save)
        assert loaded.active_cycle is not None
        assert loaded.active_cycle.cycle_type == CycleType.TOWERS


class TestSummary:
    def test_summary_keys(self, tmp_path):
        tracker = make_tracker(tmp_path)
        s = tracker.summary()
        for key in (
            "rank", "district", "total_bricks", "stability",
            "active_cracks", "flow_state", "completed_cycles",
            "failed_cycles", "next_rank", "bricks_to_next_rank",
            "district_counts",
        ):
            assert key in s

    def test_summary_counts_reflect_history(self, tmp_path):
        tracker = make_tracker(tmp_path)
        tracker.start_cycle(CycleType.FOUNDATIONS)
        tracker.complete_cycle()
        tracker.start_cycle(CycleType.FOUNDATIONS)
        tracker.fail_cycle()
        s = tracker.summary()
        assert s["completed_cycles"] == 1
        assert s["failed_cycles"] == 1
