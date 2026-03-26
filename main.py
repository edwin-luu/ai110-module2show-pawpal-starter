from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # Create an Owner
    owner = Owner("Jordan", ["morning", "afternoon", "evening"], 90)

    # Create Pet 1: Mochi the dog
    mochi = Pet("Mochi", "dog", "Shiba Inu", 3, special_needs=["grain-free diet"])
    # Intentionally added OUT OF chronological order
    mochi.add_task(Task("Evening feed", 10, 3, "evening", "daily"))
    mochi.add_task(Task("Flea medication", 5, 2, "morning", "weekly"))
    mochi.add_task(Task("Morning walk", 30, 3, "morning", "daily"))
    owner.add_pet(mochi)

    # Create Pet 2: Whiskers the cat
    whiskers = Pet("Whiskers", "cat", "Tabby", 5, special_needs=["indoor only"])
    # Also out of order
    whiskers.add_task(Task("Brush fur", 15, 1, "evening", "weekly"))
    whiskers.add_task(Task("Litter box clean", 10, 3, "morning", "daily"))
    whiskers.add_task(Task("Afternoon play session", 20, 2, "afternoon", "daily"))
    owner.add_pet(whiskers)

    scheduler = Scheduler(owner)

    # --- Recurring task demo ---
    print("=" * 60)
    print("RECURRING TASK DEMO")
    print("=" * 60)

    evening_feed = mochi.tasks[0]  # "Evening feed" (daily)
    print(f"  Before: {evening_feed.describe()}")
    print(f"  Mochi task count: {len(mochi.tasks)}")

    next_task = evening_feed.mark_complete()
    print()
    print(f"  After mark_complete():")
    print(f"    Original: {evening_feed.describe()}")
    print(f"    Next occurrence: {next_task.describe()}")
    print(f"    Mochi task count: {len(mochi.tasks)}")

    flea_med = mochi.tasks[1]  # "Flea medication" (weekly)
    print()
    print(f"  Before: {flea_med.describe()}")
    next_flea = flea_med.mark_complete()
    print(f"  After mark_complete():")
    print(f"    Original: {flea_med.describe()}")
    print(f"    Next occurrence: {next_flea.describe()}")
    print(f"    Mochi task count: {len(mochi.tasks)}")

    # --- Sorting demos ---
    all_tasks = scheduler.get_all_tasks()

    print()
    print("=" * 60)
    print("SORT BY TIME, THEN PRIORITY")
    print("=" * 60)
    for t in scheduler.sort_by_time_then_priority(all_tasks):
        print(f"  {t.describe()}")

    # --- Filtering demos ---
    print()
    print("=" * 60)
    print("FILTER BY STATUS: Pending only")
    print("=" * 60)
    for t in scheduler.filter_by_status(all_tasks, completed=False):
        print(f"  {t.describe()}")

    print()
    print("=" * 60)
    print("FILTER BY STATUS: Completed only")
    print("=" * 60)
    for t in scheduler.filter_by_status(all_tasks, completed=True):
        print(f"  {t.describe()}")

    # --- Conflict detection demo ---
    # Add conflicting tasks: two morning tasks for Mochi that will overload the window
    mochi.add_task(Task("Vet checkup", 25, 3, "morning", "weekly"))
    mochi.add_task(Task("Nail trim", 15, 2, "morning", "weekly"))

    print()
    print("=" * 60)
    print("CONFLICT DETECTION DEMO")
    print("=" * 60)
    pending = scheduler.get_pending_tasks()
    warnings = scheduler.detect_conflicts(pending)
    if warnings:
        for w in warnings:
            print(f"  !! {w}")
    else:
        print("  No conflicts detected.")

    # --- Generate plan (now with conflict warnings) ---
    print()
    print("=" * 60)
    print("GENERATED DAILY PLAN (with conflict warnings)")
    print("=" * 60)
    plan = scheduler.generate_plan()
    print(plan.describe())


if __name__ == "__main__":
    main()
