from pawpal_system import Task, Pet


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
