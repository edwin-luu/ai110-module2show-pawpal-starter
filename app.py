import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A smart pet care planning assistant")

# --- Session State ---
if "owner" not in st.session_state:
    st.session_state.owner = None
if "last_plan" not in st.session_state:
    st.session_state.last_plan = None

PRIORITY_MAP = {1: "Low", 2: "Medium", 3: "High"}

# ============================================================
# OWNER SETUP
# ============================================================
st.subheader("Owner Setup")
owner_name = st.text_input("Owner name", value="Jordan")
time_budget = st.number_input("Daily time budget (minutes)", min_value=10, max_value=480, value=90)
available_windows = st.multiselect(
    "Available time windows",
    ["morning", "afternoon", "evening"],
    default=["morning", "evening"],
)

if st.button("Create / Update Owner"):
    st.session_state.owner = Owner(owner_name, available_windows, int(time_budget))
    st.session_state.last_plan = None
    st.success(f"Owner '{owner_name}' created with {time_budget} min budget.")

owner = st.session_state.owner

if owner:
    st.info(owner.describe())

st.divider()

# ============================================================
# ADD A PET
# ============================================================
st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed", value="Shiba Inu")
age = st.number_input("Age", min_value=0, max_value=30, value=3)

if st.button("Add Pet"):
    if owner is None:
        st.error("Create an owner first!")
    else:
        pet = Pet(pet_name, species, breed, int(age))
        owner.add_pet(pet)
        st.success(f"Added {pet_name} to {owner.name}'s pets.")

if owner and owner.pets:
    with st.expander("Your Pets", expanded=False):
        for p in owner.pets:
            st.markdown(f"- **{p.name}** ({p.species}, {p.breed}, age {p.age})")

st.divider()

# ============================================================
# ADD TASKS
# ============================================================
st.subheader("Add a Task")
st.caption("Select a pet, then add tasks to it.")

if owner and owner.pets:
    pet_names = [p.name for p in owner.pets]
    selected_pet_name = st.selectbox("Select pet", pet_names)
    selected_pet = next(p for p in owner.pets if p.name == selected_pet_name)

    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
        time_pref = st.selectbox("Time preference", ["morning", "afternoon", "evening"])
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", [("Low", 1), ("Medium", 2), ("High", 3)],
                                index=2, format_func=lambda x: x[0])
    frequency = st.selectbox("Frequency", ["daily", "twice daily", "weekly", "once"])

    if st.button("Add Task"):
        task = Task(task_title, int(duration), priority[1], time_pref, frequency)
        selected_pet.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet.name}.")

    # --- Task List: sorted by time then priority using Scheduler ---
    scheduler = Scheduler(owner)
    all_tasks = scheduler.get_all_tasks()

    if all_tasks:
        st.divider()
        st.subheader("All Tasks")

        # Filter controls
        filter_col1, filter_col2 = st.columns(2)
        with filter_col1:
            filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names, key="filter_pet")
        with filter_col2:
            filter_status = st.selectbox("Filter by status", ["All", "Pending", "Completed"],
                                         key="filter_status")

        display_tasks = all_tasks
        if filter_pet != "All":
            display_tasks = scheduler.filter_by_pet(display_tasks, filter_pet)
        if filter_status == "Pending":
            display_tasks = scheduler.filter_by_status(display_tasks, completed=False)
        elif filter_status == "Completed":
            display_tasks = scheduler.filter_by_status(display_tasks, completed=True)

        # Sort chronologically with priority tiebreaker
        display_tasks = scheduler.sort_by_time_then_priority(display_tasks)

        if display_tasks:
            st.table([
                {"Pet": t.pet.name, "Task": t.name,
                 "Duration": f"{t.duration} min",
                 "Priority": PRIORITY_MAP[t.priority],
                 "Time": t.time_preference.capitalize(),
                 "Frequency": t.frequency.capitalize(),
                 "Status": "Done" if t.completed else "Pending",
                 "Due": str(t.due_date)}
                for t in display_tasks
            ])
        else:
            st.info("No tasks match the current filters.")

        # --- Mark tasks complete ---
        st.subheader("Mark Task Complete")
        pending_tasks = scheduler.filter_by_status(all_tasks, completed=False)
        if pending_tasks:
            task_options = {f"{t.pet.name} - {t.name} ({t.time_preference})": t
                           for t in pending_tasks}
            selected_task_label = st.selectbox("Select a task to complete", list(task_options.keys()))

            if st.button("Mark Complete"):
                task_to_complete = task_options[selected_task_label]
                next_task = task_to_complete.mark_complete()
                st.success(f"'{task_to_complete.name}' marked as done!")
                if next_task:
                    st.info(f"Recurring task: next '{next_task.name}' created for {next_task.due_date}.")
        else:
            st.success("All tasks are complete!")
else:
    st.info("Create an owner and add a pet first.")

st.divider()

# ============================================================
# GENERATE SCHEDULE
# ============================================================
st.subheader("Generate Daily Schedule")
st.caption("Build an optimized plan based on priority and your time budget.")

if st.button("Generate Schedule"):
    if owner is None:
        st.error("Create an owner first!")
    elif not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()
        st.session_state.last_plan = plan

# Display the plan (persists across reruns)
plan = st.session_state.last_plan
if plan:
    st.markdown(f"**Plan for {plan.date}**")

    # Show conflict warnings prominently
    if plan.warnings:
        for w in plan.warnings:
            st.warning(f"Conflict: {w}")

    if plan.scheduled_tasks:
        st.table([
            {"#": i + 1,
             "Pet": t.pet.name,
             "Task": t.name,
             "Duration": f"{t.duration} min",
             "Priority": PRIORITY_MAP[t.priority],
             "Window": t.time_preference.capitalize(),
             "Due": str(t.due_date)}
            for i, t in enumerate(plan.scheduled_tasks)
        ])

        st.markdown(f"**Total:** {plan.total_duration()} of {owner.time_budget} min used")
    else:
        st.info("No tasks could be scheduled within the time budget.")

    with st.expander("Scheduling Reasoning"):
        st.markdown(plan.reasoning)
