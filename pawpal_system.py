from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from typing import List


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

    def describe(self) -> str:
        """Return a human-readable summary of this task."""
        status = "Done" if self.completed else "Pending"
        pet_label = self.pet.name if self.pet else "Unassigned"
        priority_labels = {1: "Low", 2: "Medium", 3: "High"}
        return (
            f"[{status}] {self.name} for {pet_label} | "
            f"{self.duration} min, {priority_labels.get(self.priority, '?')} priority, "
            f"{self.time_preference}, {self.frequency}"
        )

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


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
    def __init__(self, date: str, scheduled_tasks: List[Task], reasoning: str):
        self.date = date
        self.scheduled_tasks = scheduled_tasks
        self.reasoning = reasoning

    def total_duration(self) -> int:
        """Calculate the total minutes of all scheduled tasks."""
        return sum(t.duration for t in self.scheduled_tasks)

    def describe(self) -> str:
        """Return a formatted string of the full daily plan with reasoning."""
        task_list = "\n".join(
            f"  {i+1}. {t.describe()}" for i, t in enumerate(self.scheduled_tasks)
        )
        return (
            f"Daily Plan for {self.date}\n"
            f"Tasks ({len(self.scheduled_tasks)}, {self.total_duration()} min total):\n"
            f"{task_list}\n"
            f"Reasoning: {self.reasoning}"
        )


class Scheduler:
    """The 'Brain' — retrieves, organizes, and manages tasks across all pets."""
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

    def filter_by_time_window(self, tasks: List[Task], window: str) -> List[Task]:
        """Return only tasks matching the given time window."""
        return [t for t in tasks if t.time_preference == window]

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

        # Build reasoning string
        reasoning_parts = [
            f"Scheduled {len(scheduled)} of {len(pending)} pending tasks.",
            f"Prioritized by urgency (high > medium > low) within available "
            f"time windows ({', '.join(self.owner.available_time_windows)}).",
            f"Total time used: {sum(t.duration for t in scheduled)} of "
            f"{self.owner.time_budget} min budget.",
        ]
        if skipped:
            reasoning_parts.append(
                f"Skipped {len(skipped)} task(s) that didn't fit the remaining budget."
            )

        plan = DailyPlan(
            date=str(date.today()),
            scheduled_tasks=scheduled,
            reasoning=" ".join(reasoning_parts),
        )

        self.owner.daily_plans.append(plan)
        return plan


# Convenience function that wraps Scheduler for backward compatibility
def generate_plan(owner: Owner) -> DailyPlan:
    """Convenience wrapper that creates a Scheduler and generates a plan."""
    scheduler = Scheduler(owner)
    return scheduler.generate_plan()
