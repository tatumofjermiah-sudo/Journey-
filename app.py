"""
Web server for The Architects' Codex.

Run with:
    python app.py

Then open http://localhost:5000 in your browser.
"""

from __future__ import annotations

from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

from architects_codex.cycles import CycleType, ORDER_DEFINITIONS
from architects_codex.ranks import RANK_DEFINITIONS
from architects_codex.tracker import CycleTracker, DEFAULT_SAVE_PATH

app = Flask(__name__)

# Custom Jinja2 filter: enumerate a list so templates can access (index, item)
app.jinja_env.filters["enumerate"] = enumerate

# Use the same default save path as the CLI so progress is shared
SAVE_PATH: Path = DEFAULT_SAVE_PATH


def _tracker() -> CycleTracker:
    return CycleTracker.load(SAVE_PATH)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    """Main dashboard — city map, status, active cycle."""
    tracker = _tracker()
    summary = tracker.summary()
    city_map = tracker.city.render_map()
    active = tracker.active_cycle
    rank_def = tracker.city.rank_definition

    next_rank = tracker.city.rank.__class__.next_rank(tracker.city.rank)
    bricks_to_next = (
        next_rank.brick_threshold - tracker.city.total_bricks if next_rank else 0
    )
    progress_pct = 0
    if next_rank:
        span = next_rank.brick_threshold - tracker.city.rank.brick_threshold
        earned = tracker.city.total_bricks - tracker.city.rank.brick_threshold
        progress_pct = int(min(100, earned * 100 // span)) if span else 100

    return render_template(
        "dashboard.html",
        summary=summary,
        city_map=city_map,
        active_cycle=active,
        rank_def=rank_def,
        city=tracker.city,
        cycle_types=list(CycleType),
        next_rank=next_rank,
        bricks_to_next=bricks_to_next,
        progress_pct=progress_pct,
    )


@app.route("/orders")
def orders():
    """List all available orders."""
    return render_template(
        "orders.html",
        order_definitions=ORDER_DEFINITIONS,
        cycle_types=list(CycleType),
    )


@app.route("/history")
def history():
    """Full cycle history."""
    tracker = _tracker()
    return render_template("history.html", cycles=tracker.history)


@app.route("/start", methods=["POST"])
def start():
    """Start a new cycle."""
    order = request.form.get("order", "").upper()
    try:
        ct = CycleType[order]
    except KeyError:
        return redirect(url_for("dashboard"))
    tracker = _tracker()
    try:
        tracker.start_cycle(ct)
    except RuntimeError:
        pass  # already has active cycle — silently redirect
    return redirect(url_for("dashboard"))


@app.route("/complete", methods=["POST"])
def complete():
    """Complete the active cycle."""
    notes = request.form.get("notes", "")
    tracker = _tracker()
    try:
        tracker.complete_cycle(notes)
    except RuntimeError:
        pass
    return redirect(url_for("dashboard"))


@app.route("/fail", methods=["POST"])
def fail():
    """Fail the active cycle."""
    notes = request.form.get("notes", "")
    tracker = _tracker()
    try:
        tracker.fail_cycle(notes)
    except RuntimeError:
        pass
    return redirect(url_for("dashboard"))


@app.route("/repair/<int:index>", methods=["POST"])
def repair(index: int):
    """Repair a structural crack by index."""
    tracker = _tracker()
    tracker.repair_crack(index)
    return redirect(url_for("dashboard"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug, port=5000)
