"""Tests for the Flask web application."""

import tempfile
from pathlib import Path

import pytest

import app as app_module
from architects_codex.cycles import CycleType


@pytest.fixture()
def client(tmp_path):
    """Return a Flask test client with an isolated save file."""
    app_module.SAVE_PATH = tmp_path / "state.json"
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


class TestDashboard:
    def test_get_dashboard_ok(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"Architects" in resp.data

    def test_dashboard_shows_stats(self, client):
        resp = client.get("/")
        assert b"Total Bricks" in resp.data
        assert b"Stability" in resp.data
        assert b"Active Cycle" in resp.data


class TestOrders:
    def test_get_orders_ok(self, client):
        resp = client.get("/orders")
        assert resp.status_code == 200
        assert b"Foundations" in resp.data
        assert b"Metropolis" in resp.data

    def test_orders_shows_all_five(self, client):
        resp = client.get("/orders")
        for ct in CycleType:
            assert ct.display_name.encode() in resp.data


class TestHistory:
    def test_get_history_empty(self, client):
        resp = client.get("/history")
        assert resp.status_code == 200
        assert b"No cycles in history" in resp.data

    def test_history_shows_completed_cycle(self, client):
        client.post("/start", data={"order": "FOUNDATIONS"})
        client.post("/complete", data={"notes": "web test done"})
        resp = client.get("/history")
        assert b"Foundations" in resp.data
        assert b"Done" in resp.data


class TestStartCycle:
    def test_start_redirects_to_dashboard(self, client):
        resp = client.post("/start", data={"order": "FOUNDATIONS"})
        assert resp.status_code == 302
        assert resp.headers["Location"] == "/"

    def test_start_shows_active_cycle_on_dashboard(self, client):
        client.post("/start", data={"order": "FRAMEWORKS"})
        resp = client.get("/")
        assert b"Frameworks" in resp.data
        assert b"ACTIVE" in resp.data

    def test_start_unknown_order_redirects_safely(self, client):
        resp = client.post("/start", data={"order": "INVALID"})
        assert resp.status_code == 302

    def test_start_second_cycle_while_active_is_safe(self, client):
        client.post("/start", data={"order": "FOUNDATIONS"})
        resp = client.post("/start", data={"order": "FRAMEWORKS"})
        assert resp.status_code == 302


class TestCompleteCycle:
    def test_complete_redirects(self, client):
        client.post("/start", data={"order": "FOUNDATIONS"})
        resp = client.post("/complete", data={"notes": ""})
        assert resp.status_code == 302

    def test_complete_adds_bricks(self, client):
        client.post("/start", data={"order": "FOUNDATIONS"})
        client.post("/complete", data={"notes": ""})
        resp = client.get("/")
        assert b"1" in resp.data  # at least 1 brick earned

    def test_complete_with_no_active_cycle_is_safe(self, client):
        resp = client.post("/complete", data={"notes": ""})
        assert resp.status_code == 302


class TestFailCycle:
    def test_fail_redirects(self, client):
        client.post("/start", data={"order": "FOUNDATIONS"})
        resp = client.post("/fail", data={"notes": "gave up"})
        assert resp.status_code == 302

    def test_fail_creates_crack_visible_on_dashboard(self, client):
        client.post("/start", data={"order": "TOWERS"})
        client.post("/fail", data={"notes": ""})
        resp = client.get("/")
        assert b"Structural Cracks" in resp.data

    def test_fail_with_no_active_cycle_is_safe(self, client):
        resp = client.post("/fail", data={"notes": ""})
        assert resp.status_code == 302


class TestRepairCrack:
    def test_repair_crack(self, client):
        client.post("/start", data={"order": "FOUNDATIONS"})
        client.post("/fail", data={"notes": ""})
        # Crack exists; repair index 0
        resp = client.post("/repair/0")
        assert resp.status_code == 302
        # Dashboard should no longer show cracks
        resp2 = client.get("/")
        assert b"Structural Cracks" not in resp2.data

    def test_repair_invalid_index_is_safe(self, client):
        resp = client.post("/repair/99")
        assert resp.status_code == 302
