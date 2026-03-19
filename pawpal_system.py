from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    special_needs: List[str] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def describe(self) -> str:
        pass


@dataclass
class Task:
    name: str
    duration: int          # in minutes
    priority: int          # 1 = low, 2 = medium, 3 = high
    time_preference: str   # "morning", "afternoon", or "evening"
    frequency: str         # e.g., "daily", "twice daily", "weekly"
    pet: Pet = None        # the pet this task belongs to

    def describe(self) -> str:
        pass


class Owner:
    def __init__(self, name: str, available_time_windows: List[str], time_budget: int):
        self.name = name
        self.available_time_windows = available_time_windows  # e.g., ["morning", "evening"]
        self.time_budget = time_budget  # total minutes available today
        self.pets: List[Pet] = []
        self.daily_plans: List[DailyPlan] = []

    def describe(self) -> str:
        pass


class DailyPlan:
    def __init__(self, date: str, scheduled_tasks: List[Task], reasoning: str):
        self.date = date
        self.scheduled_tasks = scheduled_tasks
        self.reasoning = reasoning

    def describe(self) -> str:
        pass


# Generates a daily plan across all of the owner's pets and their tasks
def generate_plan(owner: Owner) -> DailyPlan:
    pass
