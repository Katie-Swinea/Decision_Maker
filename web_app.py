import os
import json
import random
import streamlit as st

# --- Constants & Page Configuration ---
DECISION_FILE = "decisions.json"
st.set_page_config(page_title="Decision Engine", page_icon="✨", layout="wide")


# --- Data Handling Functions ---
def load_json_file(filepath):
    """Loads data from a JSON file, creating it if it doesn't exist."""
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump({}, f)
        return {}
    try:
        with open(filepath, 'r') as f:
            if os.path.getsize(filepath) == 0:
                return {}
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        st.error(f"Warning: {filepath} is corrupted. A new empty file will be used.")
        return {}


def save_json_file(data, filepath):
    """Saves data to a JSON file."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except (OSError, PermissionError) as e:
        st.error(f"Error: Failed to save to {filepath}: {e}")


# --- Initialize Session State ---
if 'decisions' not in st.session_state:
    st.session_state.decisions = load_json_file(DECISION_FILE)
if 'current_problem' not in st.session_state:
    st.session_state.current_problem = None
if 'suggested_solution' not in st.session_state:
    st.session_state.suggested_solution = None
if 'result_message' not in st.session_state:
    st.session_state.result_message = ""

# --- UI Layout ---
st.title("✨ Decision Engine")
col1, col2 = st.columns([2, 3])

# --- LEFT COLUMN: Inputs and Viewing ---
with col1:
    st.header("🤔 Problems & Solutions")

    # Problem selection
    with st.container(border=True):
        problem_list = list(st.session_state.decisions.keys())
        st.session_state.current_problem = st.selectbox(
            "Select a Problem",
            options=problem_list,
            index=problem_list.index(
                st.session_state.current_problem) if st.session_state.current_problem in problem_list else None,
            placeholder="Choose a problem..."
        )

        new_problem_input = st.text_input("Or, add a new problem:")
        if st.button("Add Problem"):
            if new_problem_input and new_problem_input not in st.session_state.decisions:
                st.session_state.decisions[new_problem_input] = []
                save_json_file(st.session_state.decisions, DECISION_FILE)
                st.session_state.current_problem = new_problem_input
                st.toast(f"Added problem: {new_problem_input}")
                st.rerun()
            else:
                st.warning("Problem name cannot be empty or a duplicate.")

    # Solution management
    with st.container(border=True):
        if st.session_state.current_problem:
            st.subheader(f"💡 Solutions for: **{st.session_state.current_problem}**")
            new_solution_input = st.text_input("Add a new solution:")
            if st.button("Add Solution"):
                if new_solution_input:
                    problem_solutions = [s['solutions'] for s in
                                         st.session_state.decisions[st.session_state.current_problem]]
                    if new_solution_input not in problem_solutions:
                        entry = {"solutions": new_solution_input, "ranking": None, "mood": [], "history": 0}
                        st.session_state.decisions[st.session_state.current_problem].append(entry)
                        save_json_file(st.session_state.decisions, DECISION_FILE)
                        st.toast("Solution added!")
                        st.rerun()
                    else:
                        st.warning("This solution already exists.")
                else:
                    st.warning("Solution cannot be empty.")

            st.markdown("---")
            st.subheader("📝 Edit Existing Solutions")
            solutions = st.session_state.decisions[st.session_state.current_problem]

            if solutions:
                for i, sol in enumerate(solutions):
                    sub_col1, sub_col2, sub_col3 = st.columns([3, 1, 2])
                    with sub_col1:
                        st.write(sol['solutions'])
                    with sub_col2:
                        current_rank = sol.get("ranking") if sol.get("ranking") is not None else 0
                        st.session_state[f"rank_{i}"] = st.number_input("Rank", min_value=0, step=1, value=current_rank,
                                                                        key=f"rank_input_{i}",
                                                                        label_visibility="collapsed")
                    with sub_col3:
                        current_moods = ", ".join(sol.get("mood", []))
                        st.session_state[f"mood_{i}"] = st.text_input("Moods", value=current_moods,
                                                                      key=f"mood_input_{i}",
                                                                      placeholder="happy, sad...",
                                                                      label_visibility="collapsed")

                if st.button("Save Changes", key="save_all_solutions"):
                    for i, sol in enumerate(solutions):
                        sol['ranking'] = st.session_state[f"rank_{i}"]
                        mood_text = st.session_state[f"mood_{i}"]
                        sol['mood'] = [m.strip().lower() for m in mood_text.split(',') if m.strip()]
                    save_json_file(st.session_state.decisions, DECISION_FILE)
                    st.success("All changes saved!")

            else:
                st.info("No solutions added yet for this problem.")
        else:
            st.info("Select a problem to manage solutions.")

# --- RIGHT COLUMN: Actions and Results ---
with col2:
    st.header("🚀 Let's Choose!")

    if st.session_state.current_problem and st.session_state.decisions.get(st.session_state.current_problem):
        with st.container(border=True):
            preference = st.radio(
                "Choose by Preference:",
                ["default (random)", "ranking", "mood", "history"],
                horizontal=True
            )

            if st.button("Choose For Me!", type="primary", use_container_width=True):
                st.session_state.suggested_solution = None
                st.session_state.result_message = ""
                solutions = st.session_state.decisions[st.session_state.current_problem]
                selected = None
                pref_logic = preference.split(" ")[0]

                if pref_logic == "ranking":
                    ranked_solutions = [s for s in solutions if
                                        s.get("ranking") is not None and s.get("ranking", 0) > 0]
                    if ranked_solutions:
                        min_rank = min(s['ranking'] for s in ranked_solutions)
                        best_ranked = [s for s in ranked_solutions if s['ranking'] == min_rank]
                        selected = random.choice(best_ranked)
                    else:
                        st.warning("No solutions have been ranked yet. Please add ranks in the left panel.")

                elif pref_logic == "mood":
                    st.session_state.result_message = "Please enter your current mood below and click 'Find'."

                elif pref_logic == "history":
                    hist_matches = [s for s in solutions if s.get("history", 0) > 0]
                    if hist_matches:
                        # --- CHANGE IS HERE ---
                        # Find the highest history count
                        max_hist = max(s["history"] for s in hist_matches)
                        # Find all solutions with that count
                        most_chosen = [s for s in hist_matches if s["history"] == max_hist]
                        # Randomly select from the most chosen
                        selected = random.choice(most_chosen)

                if not selected and pref_logic != "mood":
                    selected = random.choice(solutions)

                st.session_state.suggested_solution = selected

            # Handle mood input separately
            if preference.startswith("mood"):
                current_mood = st.text_input("Enter your current mood:")
                if st.button("Find Solution by Mood"):
                    mood_matches = [s for s in st.session_state.decisions[st.session_state.current_problem] if
                                    current_mood.lower() in s.get("mood", [])]
                    if mood_matches:
                        st.session_state.suggested_solution = random.choice(mood_matches)
                        st.session_state.result_message = ""
                    else:
                        st.warning(f"No solutions found for the mood: '{current_mood}'.")

        # Display suggested solution and accept/reject buttons
        if st.session_state.suggested_solution:
            with st.container(border=True):
                solution_text = st.session_state.suggested_solution['solutions']
                st.markdown("### Suggested Solution:")
                st.markdown(f"## **{solution_text}**")

                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("✅ Accept", use_container_width=True):
                        for sol in st.session_state.decisions[st.session_state.current_problem]:
                            if sol['solutions'] == solution_text:
                                sol['history'] = sol.get('history', 0) + 1
                                break
                        save_json_file(st.session_state.decisions, DECISION_FILE)
                        st.session_state.result_message = "Decision accepted and history updated!"
                        st.session_state.suggested_solution = None
                        st.rerun()
                with b_col2:
                    if st.button("❌ Reject", use_container_width=True):
                        st.session_state.result_message = "Decision rejected. Feel free to try again!"
                        st.session_state.suggested_solution = None
                        st.rerun()

        # Display result message
        if st.session_state.result_message:
            st.success(st.session_state.result_message)

    else:
        st.info("Select or add a problem to get started.")

    # STATISTICS PANEL
    with st.expander("📊 View Statistics", expanded=True):
        if st.session_state.current_problem:
            stats_solutions = st.session_state.decisions.get(st.session_state.current_problem, [])
            st.metric("Solution Count", len(stats_solutions))

            if stats_solutions:
                # Most Chosen Logic
                solutions_with_history = [s for s in stats_solutions if s.get("history", 0) > 0]
                if solutions_with_history:
                    max_history = max(s['history'] for s in solutions_with_history)
                    most_chosen_list = [s['solutions'] for s in solutions_with_history if s['history'] == max_history]
                    st.write(f"**Most Chosen:** {', '.join(most_chosen_list)} ({max_history} times)")
                else:
                    st.write("**Most Chosen:** None chosen yet.")

                # Least Chosen Logic
                unchosen_solutions = [s['solutions'] for s in stats_solutions if s.get('history', 0) == 0]
                if unchosen_solutions:
                    st.write(f"**Least Chosen:** {', '.join(unchosen_solutions)} (0 times)")
                elif solutions_with_history:
                    min_history = min(s['history'] for s in solutions_with_history)
                    least_chosen_list = [s['solutions'] for s in solutions_with_history if s['history'] == min_history]
                    st.write(f"**Least Chosen:** {', '.join(least_chosen_list)} ({min_history} times)")

            else:
                st.write("**Most Chosen:** No solutions yet.")

        else:
            st.info("Select a problem to view stats.")