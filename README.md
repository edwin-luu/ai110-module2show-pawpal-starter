# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The Scheduler class includes several algorithmic features beyond basic task listing:

- **Priority-based greedy scheduling**: Tasks are sorted by priority (high first) and packed into the owner's daily time budget. Shorter tasks break ties so more activities fit.
- **Chronological ordering**: The final plan is re-sorted by time window (morning -> afternoon -> evening) with priority as a tiebreaker, so the output reads like an actual day.
- **Sorting and filtering**: Tasks can be sorted by time, priority, or both. They can also be filtered by pet name, completion status, or time window.
- **Recurring tasks**: When a daily or weekly task is marked complete, a new instance is automatically created with the next due date using `timedelta`. The new task is added to the same pet.
- **Conflict detection**: The scheduler warns (without crashing) when a time window is overbooked or when a single pet has multiple tasks competing for the same window.

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The suite includes **13 tests** covering:

- **Basic operations**: Task completion status toggle, pet task list growth
- **Sorting correctness**: Tasks returned in chronological order (morning -> afternoon -> evening); higher priority ranks first within the same window
- **Recurrence logic**: Daily tasks create a next-day occurrence, weekly tasks create a +7 day occurrence, one-off tasks do not recur
- **Conflict detection**: Overbooked time windows are flagged, same-pet overlaps in one window are warned, and balanced schedules produce no false positives
- **Budget enforcement**: Plan duration never exceeds the owner's time budget; high-priority tasks are chosen over low-priority when budget is tight
- **Edge cases**: A pet with zero tasks generates an empty plan without crashing

**Confidence Level: 4/5**

The core scheduling logic, sorting, recurrence, and conflict detection are all verified. One star is held back because the test suite does not yet cover multi-owner scenarios, the Streamlit UI integration, or stress testing with a large number of tasks and pets.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
