from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # Create an Owner
    owner = Owner("Jordan", ["morning", "afternoon", "evening"], 90)

    # Create Pet 1: Mochi the dog
    mochi = Pet("Mochi", "dog", "Shiba Inu", 3, special_needs=["grain-free diet"])
    mochi.add_task(Task("Morning walk", 30, 3, "morning", "daily"))
    mochi.add_task(Task("Evening feed", 10, 3, "evening", "daily"))
    mochi.add_task(Task("Flea medication", 5, 2, "morning", "weekly"))
    owner.add_pet(mochi)

    # Create Pet 2: Whiskers the cat
    whiskers = Pet("Whiskers", "cat", "Tabby", 5, special_needs=["indoor only"])
    whiskers.add_task(Task("Litter box clean", 10, 3, "morning", "daily"))
    whiskers.add_task(Task("Afternoon play session", 20, 2, "afternoon", "daily"))
    whiskers.add_task(Task("Brush fur", 15, 1, "evening", "weekly"))
    owner.add_pet(whiskers)

    # Print owner and pet info
    print("=" * 60)
    print("PawPal+ Demo")
    print("=" * 60)
    print(owner.describe())
    print()
    for pet in owner.pets:
        print(pet.describe())
    print()

    # Generate and print the daily schedule
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan()

    print("-" * 60)
    print(plan.describe())
    print("-" * 60)


if __name__ == "__main__":
    main()
