import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Session State: persist the Owner object across Streamlit reruns ---
if "owner" not in st.session_state:
    st.session_state.owner = None

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
    st.success(f"Owner '{owner_name}' created with {time_budget} min budget.")

st.divider()

st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
breed = st.text_input("Breed", value="Shiba Inu")
age = st.number_input("Age", min_value=0, max_value=30, value=3)

if st.button("Add Pet"):
    if st.session_state.owner is None:
        st.error("Create an owner first!")
    else:
        pet = Pet(pet_name, species, breed, int(age))
        st.session_state.owner.add_pet(pet)
        st.success(f"Added {pet_name} to {st.session_state.owner.name}'s pets.")

st.divider()

st.markdown("### Tasks")
st.caption("Select a pet, then add tasks to it.")

owner = st.session_state.owner

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
    frequency = st.selectbox("Frequency", ["daily", "twice daily", "weekly"])

    if st.button("Add Task"):
        task = Task(task_title, int(duration), priority[1], time_pref, frequency)
        selected_pet.add_task(task)
        st.success(f"Added '{task_title}' to {selected_pet.name}.")

    # Show current tasks for all pets
    all_tasks = owner.get_all_tasks()
    if all_tasks:
        st.write("Current tasks:")
        st.table([
            {"Pet": t.pet.name, "Task": t.name, "Duration": f"{t.duration} min",
             "Priority": {1: "Low", 2: "Medium", 3: "High"}[t.priority],
             "Time": t.time_preference, "Frequency": t.frequency}
            for t in all_tasks
        ])
    else:
        st.info("No tasks yet. Add one above.")
else:
    st.info("Create an owner and add a pet first.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily plan using your scheduling logic.")

if st.button("Generate Schedule"):
    if owner is None:
        st.error("Create an owner first!")
    elif not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()

        st.markdown(f"**Plan for {plan.date}**")
        if plan.scheduled_tasks:
            st.table([
                {"#": i + 1, "Pet": t.pet.name, "Task": t.name,
                 "Duration": f"{t.duration} min",
                 "Priority": {1: "Low", 2: "Medium", 3: "High"}[t.priority],
                 "Time": t.time_preference}
                for i, t in enumerate(plan.scheduled_tasks)
            ])
        else:
            st.info("No tasks could be scheduled within the time budget.")
        st.markdown(f"**Reasoning:** {plan.reasoning}")
