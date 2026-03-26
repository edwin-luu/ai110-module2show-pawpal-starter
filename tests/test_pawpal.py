from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# --- Existing tests from Phase 2 ---

def test_mark_complete_changes_status():
    """Verify that calling mark_complete() changes the task's completed status."""
    task = Task("Morning walk", 30, 3, "morning", "daily")
    assert task.completed is False

    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    assert len(pet.tasks) == 0

    pet.add_task(Task("Morning walk", 30, 3, "morning", "daily"))
    assert len(pet.tasks) == 1

    pet.add_task(Task("Evening feed", 10, 3, "evening", "daily"))
    assert len(pet.tasks) == 2


# --- Sorting Correctness ---

def test_sort_by_time_returns_chronological_order():
    """Verify tasks are returned in morning -> afternoon -> evening order."""
    owner = Owner("Jordan", ["morning", "afternoon", "evening"], 120)
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    # Add tasks out of order
    pet.add_task(Task("Evening feed", 10, 3, "evening", "daily"))
    pet.add_task(Task("Morning walk", 30, 3, "morning", "daily"))
    pet.add_task(Task("Afternoon play", 20, 2, "afternoon", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time(scheduler.get_all_tasks())

    windows = [t.time_preference for t in sorted_tasks]
    assert windows == ["morning", "afternoon", "evening"]


def test_sort_by_time_then_priority_groups_correctly():
    """Within the same time window, higher priority tasks come first."""
    owner = Owner("Jordan", ["morning"], 120)
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    pet.add_task(Task("Low task", 10, 1, "morning", "daily"))
    pet.add_task(Task("High task", 10, 3, "morning", "daily"))
    pet.add_task(Task("Med task", 10, 2, "morning", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    result = scheduler.sort_by_time_then_priority(scheduler.get_all_tasks())

    priorities = [t.priority for t in result]
    assert priorities == [3, 2, 1]


# --- Recurrence Logic ---

def test_daily_task_recurs_next_day():
    """Completing a daily task creates a new task due tomorrow."""
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    task = Task("Morning walk", 30, 3, "morning", "daily", due_date=date(2026, 3, 25))
    pet.add_task(task)

    next_task = task.mark_complete()

    assert task.completed is True
    assert next_task is not None
    assert next_task.due_date == date(2026, 3, 26)
    assert next_task.completed is False
    assert next_task.name == "Morning walk"
    assert len(pet.tasks) == 2  # original + new occurrence


def test_weekly_task_recurs_seven_days():
    """Completing a weekly task creates a new task due in 7 days."""
    pet = Pet("Whiskers", "cat", "Tabby", 5)
    task = Task("Flea meds", 5, 2, "morning", "weekly", due_date=date(2026, 3, 25))
    pet.add_task(task)

    next_task = task.mark_complete()

    assert next_task.due_date == date(2026, 4, 1)
    assert len(pet.tasks) == 2


def test_one_off_task_does_not_recur():
    """A task with a non-recurring frequency returns None and adds no new task."""
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    task = Task("Vet visit", 60, 3, "morning", "once")
    pet.add_task(task)

    result = task.mark_complete()

    assert result is None
    assert task.completed is True
    assert len(pet.tasks) == 1  # no new task added


# --- Conflict Detection ---

def test_conflict_detected_when_window_overbooked():
    """Scheduler flags a warning when tasks in one window exceed the budget."""
    owner = Owner("Jordan", ["morning"], 30)
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    pet.add_task(Task("Walk", 20, 3, "morning", "daily"))
    pet.add_task(Task("Train", 20, 2, "morning", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts(scheduler.get_all_tasks())

    assert len(warnings) >= 1
    assert any("overbooked" in w.lower() for w in warnings)


def test_conflict_detected_same_pet_same_window():
    """Scheduler warns when one pet has multiple tasks in the same window."""
    owner = Owner("Jordan", ["morning", "evening"], 120)
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    pet.add_task(Task("Walk", 20, 3, "morning", "daily"))
    pet.add_task(Task("Train", 15, 2, "morning", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts(scheduler.get_all_tasks())

    assert any("Mochi" in w and "morning" in w for w in warnings)


def test_no_conflicts_when_tasks_spread_across_windows():
    """No warnings when each window is within budget and no overlaps."""
    owner = Owner("Jordan", ["morning", "afternoon", "evening"], 90)
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    pet.add_task(Task("Walk", 20, 3, "morning", "daily"))
    pet.add_task(Task("Play", 20, 2, "afternoon", "daily"))
    pet.add_task(Task("Feed", 10, 3, "evening", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts(scheduler.get_all_tasks())

    assert warnings == []


# --- Schedule Budget Enforcement ---

def test_schedule_respects_time_budget():
    """Plan total duration never exceeds the owner's time budget."""
    owner = Owner("Jordan", ["morning"], 30)
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    pet.add_task(Task("Walk", 20, 3, "morning", "daily"))
    pet.add_task(Task("Train", 20, 2, "morning", "daily"))
    pet.add_task(Task("Brush", 15, 1, "morning", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan.total_duration() <= 30


def test_schedule_prefers_high_priority():
    """High-priority tasks are chosen over low-priority when budget is tight."""
    owner = Owner("Jordan", ["morning"], 25)
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    pet.add_task(Task("Low task", 20, 1, "morning", "daily"))
    pet.add_task(Task("High task", 20, 3, "morning", "daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert len(plan.scheduled_tasks) == 1
    assert plan.scheduled_tasks[0].name == "High task"


# --- Edge Case: Pet with no tasks ---

def test_empty_pet_generates_empty_plan():
    """An owner with a pet that has no tasks produces an empty plan without crashing."""
    owner = Owner("Jordan", ["morning"], 60)
    pet = Pet("Mochi", "dog", "Shiba Inu", 3)
    owner.add_pet(pet)

    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    assert plan.scheduled_tasks == []
    assert plan.total_duration() == 0
    assert plan.warnings == []
