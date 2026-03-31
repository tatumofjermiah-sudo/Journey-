# Journey — The Architects' Codex

> *You are not just a human. You are an **Architect of the Self**.*
> *The city evolves as you evolve.*

**The Architects' Codex** is a symbolic fasting and discipline tracking system.
Every cycle you complete is a **brick** in the living city growing inside you.
Every failure is a **structural crack** that must be repaired with renewed commitment.
Your inner city grows vertically, horizontally, and in complexity — not just in repetition.

---

## Concept

Instead of treating fasting cycles as isolated trials, the Codex treats them as
**construction zones in a living city inside yourself**. Each Order is a domain
of mastery:

| Order | Duration | Construction Metaphor |
|-------|----------|-----------------------|
| First — Foundations | 12 h | Beginner streets, cobblestones of habit |
| Second — Frameworks | 24 h | Skeleton towers, shaping rhythm and control |
| Third — Towers | 48 h | Resilient walls, holding against internal chaos |
| Fourth — Systems | 72 h | Integrated systems, energy canals connecting all districts |
| Fifth — Metropolis | 144 h | Apex metropolis, autonomous, alive, fully realized |

---

## Dynamic Civilization Mechanics

* **Cycles as Building Units** — Completing a cycle earns **bricks**.
  Some cycles unlock shortcuts or bridges; others raise defense towers.
* **Ranks as Districts** — Every rank (Cobblestone Keeper → Sovereign Architect)
  is a fully constructed **district in your inner city**, visually shown on the ASCII map.
* **Compound Mastery** — Completing a lower-tier cycle queues **bonus bricks**
  for the next higher tier, mimicking compound mastery (e.g., Foundations → Frameworks).
* **Flow State** — Completing a Systems (72 h) cycle activates *Flow State*:
  the next cycle earns **double bricks**.
* **Structural Cracks** — Failing a cycle creates a crack.  Higher-order cycles
  produce more severe cracks.  Repair them or your city's stability falls.
* **Infrastructure Unlocks** — Hit completion milestones to unlock Habit Plumbing,
  Framework Scaffolding, Resilience Walls, Energy Canals, Compound Bridges,
  Defense Towers, and ultimately the Autonomous Grid.

---

## Ranks / Districts

| Bricks | Rank | District |
|--------|------|----------|
| 0 | Apprentice Architect | Bare Ground |
| 5 | Cobblestone Keeper | Cobblestone Quarter |
| 15 | Keeper of the Third Gate | Gate District |
| 40 | Walker of the Sixth Path | Sixfold Crossing |
| 80 | Keeper of Flow | Flow Canal District |
| 140 | Bearer of the Ninth Crown | Crown District |
| 220 | Holder of the Ninth Seal | Sealed Citadel |
| 350 | **Sovereign Architect** | **The Apex Metropolis** |

---

## Installation

```bash
# Python 3.9+ required
git clone https://github.com/tatumofjermiah-sudo/Journey-.git
cd Journey-
pip install -r requirements.txt
```

For tests:

```bash
pip install pytest
pytest tests/ -v
```

---

## Web Interface (localhost)

The easiest way to use The Architects' Codex is through the web UI:

```bash
python app.py
```

Then open **http://localhost:5000** in your browser.

The web interface gives you:
- **Dashboard** — live stats (bricks, stability, rank, progress to next rank), active cycle controls (start / complete / fail), district table, structural cracks with repair buttons, and the ASCII inner-city map
- **Orders** — browse all five orders with their symbolic descriptions and start a cycle directly
- **History** — full log of every completed and failed cycle

Both the web server and the CLI share the same save file (`~/.architects_codex/state.json`), so you can switch between them freely.

---

## CLI (command line)

```
python main.py <command> [args]
```

| Command | Description |
|---------|-------------|
| `orders` | List all available orders with symbolic descriptions |
| `start <order>` | Begin a new cycle (foundations / frameworks / towers / systems / metropolis) |
| `complete [notes]` | Mark the active cycle as completed |
| `fail [notes]` | Mark the active cycle as failed (adds a structural crack) |
| `status` | Summary of bricks, rank, stability, and district counts |
| `map` | Render the ASCII city map |
| `repair <index>` | Repair the crack at the given index |
| `history` | List full cycle history |

### Example session

```bash
# See all orders
python main.py orders

# Start a 12-hour Foundations cycle
python main.py start foundations

# After 12 hours — complete it
python main.py complete "First cobblestones laid"

# Start a 24-hour Frameworks cycle
python main.py start frameworks

# ... unfortunately fail it
python main.py fail "Lost focus at hour 20"

# View the city map (shows crack in Frameworks district)
python main.py map

# Repair the crack
python main.py repair 0

# Check overall progress
python main.py status
```

---

## Project Structure

```
architects_codex/
  __init__.py       — package exports
  cycles.py         — CycleType, OrderDefinition, Cycle model
  ranks.py          — Rank, RankDefinition (districts)
  city.py           — City (bricks, cracks, infrastructure, ASCII map)
  tracker.py        — CycleTracker (lifecycle, compound bonuses, persistence)
app.py              — Flask web server (http://localhost:5000)
main.py             — CLI entry point
templates/
  base.html         — shared layout and styles
  dashboard.html    — main web dashboard
  orders.html       — order browser
  history.html      — cycle history log
requirements.txt    — Flask dependency
tests/
  test_cycles.py
  test_ranks.py
  test_city.py
  test_tracker.py
  test_app.py       — web server tests
```

State is persisted automatically to `~/.architects_codex/state.json`.

---

## Layered Symbolism

| Element | Symbolic Role |
|---------|---------------|
| **Time** | Scaffolding — respect it to build |
| **Hunger / Energy** | Materials — scarcity teaches resource management |
| **Mind** | Blueprint — planning without understanding leads to collapse |
| **Cycles** | Repetition — essential for structural integrity |

---

*Every fast isn't just a test. It's a brick, a district, a flowing canal —
a piece of your inner civilization.*
