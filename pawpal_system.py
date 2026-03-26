from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional


@dataclass
class Task:
    """Represents a single pet care activity."""
    name: str
    duration: int          # in minutes
    priority: int          # 1 = low, 2 = medium, 3 = high
    time_preference: str   # "morning", "afternoon", or "evening"
    frequency: str         # e.g., "daily", "twice daily", "weekly"
    completed: bool = False
    pet: Pet = None        # back-reference set when task is added to a pet
    due_date: Optional[date] = None  # when this task is next due

    # How many days until the next occurrence, by frequency
    RECURRENCE_DAYS = {"daily": 1, "twice daily": 1, "weekly": 7}

    def __post_init__(self):
        """Set due_date to today if not provided."""
        if self.due_date is None:
            self.due_date = date.today()

    def describe(self) -> str:
        """Return a human-readable summary of this task."""
        status = "Done" if self.completed else "Pending"
        pet_label = self.pet.name if self.pet else "Unassigned"
        priority_labels = {1: "Low", 2: "Medium", 3: "High"}
        return (
            f"[{status}] {self.name} for {pet_label} | "
            f"{self.duration} min, {priority_labels.get(self.priority, '?')} priority, "
            f"{self.time_preference}, {self.frequency}, due {self.due_date}"
        )

    def mark_complete(self) -> Optional[Task]:
        """Mark this task as completed. If recurring, create and return the next occurrence."""
        self.completed = True

        days_ahead = self.RECURRENCE_DAYS.get(self.frequency)
        if days_ahead is None:
            return None  # one-off task, no recurrence

        # Create the next occurrence with a future due date
        next_task = Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            time_preference=self.time_preference,
            frequency=self.frequency,
            due_date=self.due_date + timedelta(days=days_ahead),
        )

        # Automatically add to the same pet if one is assigned
        if self.pet:
            self.pet.add_task(next_task)

        return next_task


@dataclass
class Pet:
    """Stores pet details and a list of tasks."""
    name: str
    species: str
    breed: str
    age: int
    special_needs: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and set the task's pet back-reference."""
        task.pet = self
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[Task]:
        """Return only tasks that have not been completed."""
        return [t for t in self.tasks if not t.completed]

    def describe(self) -> str:
        """Return a human-readable summary of this pet."""
        needs = ", ".join(self.special_needs) if self.special_needs else "None"
        return (
            f"{self.name} ({self.species}, {self.breed}, age {self.age}) | "
            f"Special needs: {needs} | Tasks: {len(self.tasks)}"
        )


class Owner:
    """Manages multiple pets and provides access to all their tasks."""
    def __init__(self, name: str, available_time_windows: List[str], time_budget: int):
        self.name = name
        self.available_time_windows = available_time_windows  # e.g., ["morning", "evening"]
        self.time_budget = time_budget  # total minutes available today
        self.pets: List[Pet] = []
        self.daily_plans: List[DailyPlan] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet under this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Collect and return all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_all_pending_tasks(self) -> List[Task]:
        """Return incomplete tasks across all pets."""
        return [t for t in self.get_all_tasks() if not t.completed]

    def describe(self) -> str:
        """Return a human-readable summary of this owner and their pets."""
        pet_names = ", ".join(p.name for p in self.pets) if self.pets else "None"
        windows = ", ".join(self.available_time_windows)
        return (
            f"Owner: {self.name} | Pets: {pet_names} | "
            f"Available: {windows} | Budget: {self.time_budget} min"
        )


class DailyPlan:
    """A generated daily schedule with reasoning."""
    def __init__(self, date: str, scheduled_tasks: List[Task], reasoning: str,
                 warnings: List[str] = None):
        self.date = date
        self.scheduled_tasks = scheduled_tasks
        self.reasoning = reasoning
        self.warnings = warnings or []

    def total_duration(self) -> int:
        """Calculate the total minutes of all scheduled tasks."""
        return sum(t.duration for t in self.scheduled_tasks)

    def describe(self) -> str:
        """Return a formatted string of the full daily plan with reasoning."""
        task_list = "\n".join(
            f"  {i+1}. {t.describe()}" for i, t in enumerate(self.scheduled_tasks)
        )
        parts = [
            f"Daily Plan for {self.date}",
            f"Tasks ({len(self.scheduled_tasks)}, {self.total_duration()} min total):",
            task_list,
            f"Reasoning: {self.reasoning}",
        ]
        if self.warnings:
            parts.append("Warnings:")
            for w in self.warnings:
                parts.append(f"  !! {w}")
        return "\n".join(parts)


class Scheduler:
    """The 'Brain' — retrieves, organizes, and manages tasks across all pets."""

    # Maps time-preference strings to sort order so morning < afternoon < evening
    TIME_ORDER = {"morning": 0, "afternoon": 1, "evening": 2}

    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Retrieve every task from the owner's pets."""
        return self.owner.get_all_tasks()

    def get_pending_tasks(self) -> List[Task]:
        """Retrieve only incomplete tasks from the owner's pets."""
        return self.owner.get_all_pending_tasks()

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted from highest to lowest priority."""
        return sorted(tasks, key=lambda t: t.priority, reverse=True)

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted chronologically by time window (morning -> afternoon -> evening)."""
        return sorted(
            tasks,
            key=lambda t: self.TIME_ORDER.get(t.time_preference, 99),
        )

    def sort_by_time_then_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort by time window first, then by priority (high first) within each window."""
        return sorted(
            tasks,
            key=lambda t: (self.TIME_ORDER.get(t.time_preference, 99), -t.priority),
        )

    def filter_by_time_window(self, tasks: List[Task], window: str) -> List[Task]:
        """Return only tasks matching the given time window."""
        return [t for t in tasks if t.time_preference == window]

    def filter_by_pet(self, tasks: List[Task], pet_name: str) -> List[Task]:
        """Return only tasks belonging to the named pet."""
        return [t for t in tasks if t.pet and t.pet.name == pet_name]

    def filter_by_status(self, tasks: List[Task], completed: bool) -> List[Task]:
        """Return tasks filtered by completion status."""
        return [t for t in tasks if t.completed == completed]

    def detect_conflicts(self, tasks: List[Task], budget_per_window: int = None) -> List[str]:
        """Check for scheduling conflicts and return a list of warning strings."""
        warnings = []

        # Default: split total budget evenly across available windows
        if budget_per_window is None:
            num_windows = len(self.owner.available_time_windows) or 1
            budget_per_window = self.owner.time_budget // num_windows

        # Group tasks by time window
        by_window: dict[str, List[Task]] = {}
        for t in tasks:
            by_window.setdefault(t.time_preference, []).append(t)

        for window, window_tasks in by_window.items():
            total = sum(t.duration for t in window_tasks)

            # Check if the window is overbooked
            if total > budget_per_window:
                warnings.append(
                    f"{window.capitalize()} is overbooked: "
                    f"{total} min of tasks vs {budget_per_window} min budget."
                )

            # Check for same-pet overlaps within the same window
            pet_tasks: dict[str, List[Task]] = {}
            for t in window_tasks:
                pet_name = t.pet.name if t.pet else "Unassigned"
                pet_tasks.setdefault(pet_name, []).append(t)

            for pet_name, pt in pet_tasks.items():
                if len(pt) > 1:
                    task_names = ", ".join(f"'{t.name}'" for t in pt)
                    warnings.append(
                        f"{pet_name} has {len(pt)} tasks in the same "
                        f"{window} window: {task_names}."
                    )

        return warnings

    def generate_plan(self) -> DailyPlan:
        """Build an optimized daily plan based on priority and time budget."""
        pending = self.get_pending_tasks()

        # Filter to tasks that fit the owner's available time windows
        available = [
            t for t in pending
            if t.time_preference in self.owner.available_time_windows
        ]

        # Sort by priority (high first), then by duration (shorter first as tiebreaker)
        available = sorted(available, key=lambda t: (-t.priority, t.duration))

        # Greedily select tasks that fit within the owner's time budget
        scheduled = []
        remaining_budget = self.owner.time_budget
        skipped = []

        for task in available:
            if task.duration <= remaining_budget:
                scheduled.append(task)
                remaining_budget -= task.duration
            else:
                skipped.append(task)

        # Re-order the final schedule chronologically for a readable day plan
        scheduled = self.sort_by_time_then_priority(scheduled)

        # Build reasoning string
        reasoning_parts = [
            f"Scheduled {len(scheduled)} of {len(pending)} pending tasks.",
            f"Prioritized by urgency (high > medium > low) within available "
            f"time windows ({', '.join(self.owner.available_time_windows)}).",
            f"Final order: chronological (morning -> evening) with priority tiebreaker.",
            f"Total time used: {sum(t.duration for t in scheduled)} of "
            f"{self.owner.time_budget} min budget.",
        ]
        if skipped:
            reasoning_parts.append(
                f"Skipped {len(skipped)} task(s) that didn't fit the remaining budget."
            )

        # Detect conflicts in the scheduled tasks
        warnings = self.detect_conflicts(scheduled)

        plan = DailyPlan(
            date=str(date.today()),
            scheduled_tasks=scheduled,
            reasoning=" ".join(reasoning_parts),
            warnings=warnings,
        )

        self.owner.daily_plans.append(plan)
        return plan


# Convenience function that wraps Scheduler for backward compatibility
def generate_plan(owner: Owner) -> DailyPlan:
    """Convenience wrapper that creates a Scheduler and generates a plan."""
    scheduler = Scheduler(owner)
    return scheduler.generate_plan()
