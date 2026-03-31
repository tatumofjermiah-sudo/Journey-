"""
CLI for The Architects' Codex.

Usage
-----
    python main.py start <order>        # begin a new cycle
    python main.py complete [notes]     # complete the active cycle
    python main.py fail    [notes]      # fail the active cycle
    python main.py status               # show current city state
    python main.py map                  # render the ASCII city map
    python main.py repair <index>       # repair an unrepaired crack
    python main.py history              # list cycle history
    python main.py orders               # list all available orders

Available orders (case-insensitive):
    foundations   12 h
    frameworks    24 h
    towers        48 h
    systems       72 h
    metropolis   144 h
"""

from __future__ import annotations

import sys
from pathlib import Path

from architects_codex.cycles import CycleType, ORDER_DEFINITIONS
from architects_codex.ranks import RANK_DEFINITIONS
from architects_codex.tracker import CycleTracker, DEFAULT_SAVE_PATH


def _tracker(save_path: Path = DEFAULT_SAVE_PATH) -> CycleTracker:
    return CycleTracker.load(save_path)


def _parse_cycle_type(name: str) -> CycleType:
    try:
        return CycleType[name.upper()]
    except KeyError:
        valid = ", ".join(ct.name.lower() for ct in CycleType)
        print(f"Unknown order '{name}'. Valid orders: {valid}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_orders() -> None:
    """List all available orders with their descriptions."""
    print()
    print("THE ARCHITECTS' CODEX — Available Orders")
    print("=" * 60)
    for ct in CycleType:
        defn = ORDER_DEFINITIONS[ct]
        print()
        print(f"  {defn.order_name}")
        print(f"  Duration   : {ct.hours} hours")
        print(f"  Bricks     : {defn.brick_value} per completion")
        print(f"  Metaphor   : {defn.construction_metaphor}")
        print(f"  Scaffolding: {defn.scaffolding_description}")
        print(f"  Bonus      : {defn.bonus_description}")
    print()


def cmd_start(order_name: str) -> None:
    """Start a new cycle of the given order."""
    ct = _parse_cycle_type(order_name)
    tracker = _tracker()
    try:
        cycle = tracker.start_cycle(ct)
    except RuntimeError as exc:
        print(f"✗  {exc}")
        sys.exit(1)
    defn = ORDER_DEFINITIONS[ct]
    print()
    print(f"  ▶  Cycle started: {defn.order_name}")
    print(f"     {defn.construction_metaphor}")
    print(f"     Target duration: {ct.hours} hours")
    print(f"     Started at: {cycle.started_at.strftime('%Y-%m-%d %H:%M UTC')}")
    print()


def cmd_complete(notes: str = "") -> None:
    """Mark the active cycle as completed."""
    tracker = _tracker()
    try:
        cycle = tracker.complete_cycle(notes)
    except RuntimeError as exc:
        print(f"✗  {exc}")
        sys.exit(1)
    bricks = cycle.bricks_earned
    rank_def = tracker.city.rank_definition
    print()
    print(f"  ✓  Cycle completed: {cycle.cycle_type.display_name} ({cycle.cycle_type.hours}h)")
    print(f"     Bricks earned  : {bricks}")
    print(f"     Total bricks   : {tracker.city.total_bricks}")
    print(f"     Current rank   : {rank_def.civic_title}")
    print(f"     Stability      : {tracker.city.stability} / 100")
    if cycle.bonus_bricks:
        print(f"     (includes compound-mastery bonus)")
    if tracker.city.flow_state_active:
        print("     *** FLOW STATE now active — next cycle earns double bricks ***")
    print()


def cmd_fail(notes: str = "") -> None:
    """Mark the active cycle as failed."""
    tracker = _tracker()
    try:
        cycle = tracker.fail_cycle(notes)
    except RuntimeError as exc:
        print(f"✗  {exc}")
        sys.exit(1)
    crack = tracker.city.cracks[-1] if tracker.city.cracks else None
    print()
    print(f"  ✗  Cycle failed: {cycle.cycle_type.display_name} ({cycle.cycle_type.hours}h)")
    if crack:
        print(f"     Structural crack: {crack.severity_label} crack in "
              f"{crack.cycle_type.display_name} district")
    print(f"     Stability: {tracker.city.stability} / 100")
    print(f"     Repair cracks with: python main.py repair <index>")
    print()


def cmd_status() -> None:
    """Show a summary of the Architect's current progress."""
    tracker = _tracker()
    s = tracker.summary()
    next_rank_label = s["next_rank"].replace("_", " ").title() if s["next_rank"] != "MAX" else "—"
    print()
    print("THE ARCHITECTS' CODEX — Status")
    print("=" * 60)
    print(f"  Rank           : {s['rank']}")
    print(f"  District       : {s['district']}")
    print(f"  Total Bricks   : {s['total_bricks']}")
    print(f"  Stability      : {s['stability']} / 100")
    if s["active_cracks"]:
        print(f"  Active Cracks  : {s['active_cracks']} unrepaired")
    if s["flow_state"]:
        print("  *** FLOW STATE active — next cycle earns double bricks ***")
    print(f"  Completed      : {s['completed_cycles']} cycles")
    print(f"  Failed         : {s['failed_cycles']} cycles")
    if s["next_rank"] != "MAX":
        print(f"  Next rank      : {next_rank_label} (need {s['bricks_to_next_rank']} more bricks)")
    print()
    print("  Districts built:")
    for name, count in s["district_counts"].items():
        print(f"    {name:<14} {count}")
    if tracker.active_cycle:
        ac = tracker.active_cycle
        print()
        print(f"  Active cycle   : {ac.cycle_type.display_name} ({ac.cycle_type.hours}h)")
        print(f"  Elapsed        : {ac.elapsed_hours:.1f} h / {ac.cycle_type.hours} h")
    print()


def cmd_map() -> None:
    """Render the ASCII city map."""
    tracker = _tracker()
    print(tracker.city.render_map())


def cmd_repair(index: int) -> None:
    """Repair the crack at the given index."""
    tracker = _tracker()
    active_cracks = tracker.city.active_cracks
    if not active_cracks:
        print("  No active cracks to repair.")
        return
    print()
    print("  Active cracks:")
    for i, crack in enumerate(active_cracks):
        print(f"    [{i}] {crack.cycle_type.display_name} — {crack.severity_label} crack")
    print()
    success = tracker.repair_crack(index, "Repaired through renewed commitment.")
    if success:
        print(f"  ✓  Crack [{index}] repaired.")
        print(f"     Stability: {tracker.city.stability} / 100")
    else:
        print(f"  ✗  No crack at index {index}.")
    print()


def cmd_history() -> None:
    """List the full cycle history."""
    tracker = _tracker()
    if not tracker.history:
        print("  No cycles in history yet.")
        return
    print()
    print("THE ARCHITECTS' CODEX — Cycle History")
    print("=" * 60)
    for cycle in tracker.history:
        status_icon = "✓" if cycle.status.value == "completed" else "✗"
        ts = cycle.started_at.strftime("%Y-%m-%d %H:%M")
        bricks = f"+{cycle.bricks_earned}" if cycle.bricks_earned else ""
        notes = f"  [{cycle.notes}]" if cycle.notes else ""
        print(
            f"  {status_icon} {ts}  {cycle.cycle_type.display_name:<12} "
            f"({cycle.cycle_type.hours:3d}h)  {bricks:>5}{notes}"
        )
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

COMMANDS = {
    "orders": cmd_orders,
    "start": cmd_start,
    "complete": cmd_complete,
    "fail": cmd_fail,
    "status": cmd_status,
    "map": cmd_map,
    "repair": cmd_repair,
    "history": cmd_history,
}


def main(argv: list[str] | None = None) -> None:
    args = argv if argv is not None else sys.argv[1:]

    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return

    cmd = args[0].lower()
    rest = args[1:]

    if cmd == "start":
        if not rest:
            print("Usage: python main.py start <order>")
            sys.exit(1)
        cmd_start(rest[0])

    elif cmd == "complete":
        cmd_complete(" ".join(rest))

    elif cmd == "fail":
        cmd_fail(" ".join(rest))

    elif cmd == "repair":
        if not rest:
            print("Usage: python main.py repair <index>")
            sys.exit(1)
        try:
            idx = int(rest[0])
        except ValueError:
            print("Index must be an integer.")
            sys.exit(1)
        cmd_repair(idx)

    elif cmd == "status":
        cmd_status()

    elif cmd == "map":
        cmd_map()

    elif cmd == "history":
        cmd_history()

    elif cmd == "orders":
        cmd_orders()

    else:
        print(f"Unknown command '{cmd}'. Run 'python main.py --help' for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
