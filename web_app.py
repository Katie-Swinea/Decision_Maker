import os
import json
import random
from collections import Counter
import streamlit as st

# --- Constants & Page Configuration ---
DECISION_FILE = "decisions.json"
st.set_page_config(
    page_title="Decision Fox",
    page_icon="🦊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fox-Themed Style Configuration ---
THEME_COLORS = {
    "base": "#FAF9F6",
    "frame": "#E8E8E8",
    "text": "#4A4A4A",
    "text_highlight": "#212121",
    "accent_primary": "#D85C28", # Rusty Orange
    "accent_secondary": "#D85C28"  # Orange for borders
}

# --- Data Handling Functions ---
def load_json_file(filepath):
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        with open(filepath, 'w') as f: json.dump({}, f)
        return {}
    try:
        with open(filepath, 'r') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        st.error(f"Warning: {filepath} is corrupted. A new empty file will be used.")
        return {}

def save_json_file(data, filepath):
    try:
        with open(filepath, 'w') as f: json.dump(data, f, indent=4)
    except (OSError, PermissionError) as e: st.error(f"Error: Failed to save to {filepath}: {e}")

# --- Initialize Session State ---
def init_state():
    if 'decisions' not in st.session_state:
        st.session_state.decisions = load_json_file(DECISION_FILE)
    if 'current_problem' not in st.session_state:
        st.session_state.current_problem = None
    if 'suggested_solution' not in st.session_state:
        st.session_state.suggested_solution = None
    if 'result_message' not in st.session_state:
        st.session_state.result_message = ""
    if 'suggestion_reason' not in st.session_state:
        st.session_state.suggestion_reason = ""
    if 'decision_log' not in st.session_state:
        st.session_state.decision_log = []
    if 'rejected_solutions' not in st.session_state:
        st.session_state.rejected_solutions = {}
    if 'confirming_delete_problem' not in st.session_state:
        st.session_state.confirming_delete_problem = False
    if 'confirming_delete_solution' not in st.session_state:
        st.session_state.confirming_delete_solution = None

init_state()

# --- Dynamic CSS for Theming ---
css = f"""
<style>
    .stApp {{ background-color: {THEME_COLORS["base"]}; }}
    .stApp, .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp li, .stApp label, .st-emotion-cache-16idsys p {{
        color: {THEME_COLORS["text_highlight"]};
    }}
    [data-testid="stMetric"] .st-emotion-cache-16idsys p, .st-emotion-cache-1xarl3l p {{
        color: {THEME_COLORS["text"]} !important;
    }}
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column;"] > [data-testid="stVerticalBlock"] {{ 
        background-color: {THEME_COLORS["frame"]}; 
        border: 1px solid {THEME_COLORS["accent_secondary"]};
        border-radius: 0.5rem;
    }}
    .st-emotion-cache-p5msec {{
        background-color: {THEME_COLORS["frame"]};
    }}
</style>
"""
st.markdown(css, unsafe_allow_html=True)


# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings & Info")
    with st.expander("📖 How It Works", expanded=True):
        st.markdown("""
        - **Default (Random)**: Picks any solution at random.
        - **Ranking**: Picks from solutions with the lowest rank number (1 is best).
        - **Mood**: Suggests a solution matching your entered mood.
        - **Most Chosen**: Picks from solutions with the highest history count.
        - **Least Chosen**: Picks from solutions with the lowest history count.
        - **Trendy**: Picks the solution chosen most often in the last 5 accepted decisions.
        - **Avoid Repeats**: Prevents recently rejected solutions from being suggested.
        """)

# --- MAIN UI ---
st.title("🦊 Decision Fox")
col1, col2 = st.columns([2, 3])

# LEFT COLUMN
with col1:
    st.header("🤔 Problems & Solutions")
    with st.container(border=True):
        problem_list = list(st.session_state.decisions.keys())
        st.session_state.current_problem = st.selectbox("Select a Problem", options=problem_list, index=problem_list.index(st.session_state.current_problem) if st.session_state.current_problem in problem_list else None, placeholder="Choose a problem...")
        if st.session_state.current_problem:
            if st.button("Delete Current Problem", type="secondary", use_container_width=True):
                st.session_state.confirming_delete_problem = True
            if st.session_state.confirming_delete_problem:
                st.warning(f"**Are you sure?** Deleting '{st.session_state.current_problem}' cannot be undone.")
                if st.button("Confirm Deletion", type="primary"):
                    del st.session_state.decisions[st.session_state.current_problem]
                    save_json_file(st.session_state.decisions, DECISION_FILE)
                    st.session_state.current_problem = None
                    st.session_state.confirming_delete_problem = False
                    st.rerun()
        st.markdown("---")
        new_problem_input = st.text_input("Or, add a new problem:")
        if st.button("Add Problem"):
            if new_problem_input and new_problem_input not in st.session_state.decisions:
                st.session_state.decisions[new_problem_input] = []
                save_json_file(st.session_state.decisions, DECISION_FILE)
                st.session_state.current_problem = new_problem_input
                st.toast(f"Added problem: {new_problem_input}")
                st.rerun()
            else: st.warning("Problem name cannot be empty or a duplicate.")

    with st.container(border=True):
        if st.session_state.current_problem:
            st.subheader(f"💡 Solutions for: **{st.session_state.current_problem}**")
            new_solution_input = st.text_input("Add a new solution:")
            if st.button("Add Solution"):
                if new_solution_input:
                    problem_solutions = [s['solutions'] for s in st.session_state.decisions[st.session_state.current_problem]]
                    if new_solution_input not in problem_solutions:
                        st.session_state.decisions[st.session_state.current_problem].append({"solutions": new_solution_input, "ranking": 0, "mood": [], "history": 0})
                        save_json_file(st.session_state.decisions, DECISION_FILE)
                        st.toast("Solution added!"); st.rerun()
                    else: st.warning("This solution already exists.")
                else: st.warning("Solution cannot be empty.")
            st.markdown("---")
            st.subheader("📝 Edit Existing Solutions")
            solutions = st.session_state.decisions[st.session_state.current_problem]
            if solutions:
                for i, sol in enumerate(solutions):
                    sub_col1, sub_col2, sub_col3, sub_col4 = st.columns([4, 1, 3, 1])
                    sub_col1.write(sol['solutions'])
                    st.session_state[f"rank_{i}"] = sub_col2.number_input("Rank", value=sol.get("ranking", 0), key=f"rank_input_{i}", label_visibility="collapsed", help="Rank (1 is best)")
                    st.session_state[f"mood_{i}"] = sub_col3.text_input("Moods", value=", ".join(sol.get("mood", [])), key=f"mood_input_{i}", label_visibility="collapsed", help="Comma-separated moods")
                    if sub_col4.button("🗑️", key=f"del_{i}", help="Delete Solution"):
                        st.session_state.confirming_delete_solution = sol['solutions']
                    if st.session_state.confirming_delete_solution == sol['solutions']:
                        st.warning(f"Delete '{sol['solutions']}'? This cannot be undone.")
                        if st.button("Confirm", key=f"confirm_del_{i}"):
                            st.session_state.decisions[st.session_state.current_problem] = [s for s in solutions if s['solutions'] != sol['solutions']]
                            save_json_file(st.session_state.decisions, DECISION_FILE)
                            st.session_state.confirming_delete_solution = None; st.rerun()
                if st.button("Save All Changes", key="save_all_solutions"):
                    for i, sol in enumerate(solutions):
                        sol['ranking'] = st.session_state[f"rank_{i}"]
                        sol['mood'] = [m.strip().lower() for m in st.session_state[f"mood_{i}"].split(',') if m.strip()]
                    save_json_file(st.session_state.decisions, DECISION_FILE); st.success("All changes saved!")
            else: st.info("No solutions added yet.")
        else: st.info("Select a problem to manage solutions.")

# RIGHT COLUMN
with col2:
    st.header("🚀 Let's Choose!")
    if st.session_state.current_problem and st.session_state.decisions.get(st.session_state.current_problem):
        with st.container(border=True):
            avoid_repeats = st.toggle("Avoid Repeats", help="Don't suggest solutions you have recently rejected.")
            preference = st.radio("Choose by Preference:", ["default (random)", "ranking", "mood", "most chosen", "least chosen", "trendy"], horizontal=True)
            if st.button("Choose For Me!", type="primary", use_container_width=True):
                st.session_state.suggested_solution, st.session_state.result_message, st.session_state.suggestion_reason = None, "", ""
                solutions = st.session_state.decisions[st.session_state.current_problem]
                eligible_solutions = solutions
                if avoid_repeats:
                    rejected = st.session_state.rejected_solutions.get(st.session_state.current_problem, set())
                    eligible_solutions = [s for s in solutions if s['solutions'] not in rejected]
                    if not eligible_solutions:
                        st.toast("All options have been rejected. Resetting 'Avoid Repeats' list.")
                        st.session_state.rejected_solutions[st.session_state.current_problem] = set()
                        eligible_solutions = solutions
                selected, reason = None, ""
                pref_logic = preference.split(" ")[0]
                if pref_logic == "ranking":
                    ranked = [s for s in eligible_solutions if s.get("ranking", 0) > 0]
                    if ranked:
                        min_rank = min(s['ranking'] for s in ranked)
                        best = [s for s in ranked if s['ranking'] == min_rank]
                        selected, reason = random.choice(best), f"Chosen for its top rank of {min_rank}."
                    else: st.warning("No solutions have been ranked yet.")
                elif pref_logic == "mood": st.session_state.result_message = "Please enter your current mood below."
                elif pref_logic == "most chosen":
                    hist_matches = [s for s in eligible_solutions if s.get("history", 0) > 0]
                    if hist_matches:
                        max_hist = max(s["history"] for s in hist_matches)
                        most_chosen = [s for s in hist_matches if s["history"] == max_hist]
                        selected, reason = random.choice(most_chosen), f"Chosen for being the most popular ({max_hist} times)."
                elif pref_logic == "least chosen":
                    min_hist = min(s.get("history", 0) for s in eligible_solutions)
                    least_chosen = [s for s in eligible_solutions if s.get("history", 0) == min_hist]
                    selected, reason = random.choice(least_chosen), f"Chosen for being picked least often ({min_hist} times)."
                elif pref_logic == "trendy":
                    if st.session_state.decision_log:
                        last_5 = st.session_state.decision_log[-5:]
                        if last_5:
                            most_common = Counter(last_5).most_common(1)[0][0]
                            for sol in eligible_solutions:
                                if sol['solutions'] == most_common:
                                    selected, reason = sol, "Chosen for being trendy recently."; break
                if not selected and pref_logic != "mood" and eligible_solutions:
                    selected, reason = random.choice(eligible_solutions), "Chosen at random."
                st.session_state.suggested_solution = selected
                st.session_state.suggestion_reason = reason
            if preference.startswith("mood"):
                current_mood = st.text_input("Enter your current mood:")
                if st.button("Find Solution by Mood"):
                    mood_matches = [s for s in st.session_state.decisions[st.session_state.current_problem] if current_mood.lower() in s.get("mood", [])]
                    if mood_matches:
                        st.session_state.suggested_solution = random.choice(mood_matches)
                        st.session_state.suggestion_reason = f"Chosen for matching the mood '{current_mood}'."; st.session_state.result_message = ""
                    else: st.warning(f"No solutions found for the mood: '{current_mood}'.")

        if st.session_state.suggested_solution:
            with st.container(border=True):
                solution_text = st.session_state.suggested_solution['solutions']
                st.markdown(f"##### {st.session_state.suggestion_reason}")
                st.markdown(f"## **{solution_text}**")
                b_col1, b_col2 = st.columns(2)
                if b_col1.button("✅ Accept", use_container_width=True):
                    for sol in st.session_state.decisions[st.session_state.current_problem]:
                        if sol['solutions'] == solution_text:
                            sol['history'] = sol.get('history', 0) + 1
                            st.session_state.decision_log.append(sol['solutions']); break
                    save_json_file(st.session_state.decisions, DECISION_FILE)
                    st.session_state.result_message, st.session_state.suggested_solution = "Decision accepted!", None; st.rerun()
                if b_col2.button("❌ Reject", use_container_width=True):
                    if st.session_state.current_problem not in st.session_state.rejected_solutions:
                        st.session_state.rejected_solutions[st.session_state.current_problem] = set()
                    st.session_state.rejected_solutions[st.session_state.current_problem].add(solution_text)
                    st.session_state.result_message, st.session_state.suggested_solution = "Decision rejected.", None; st.rerun()
        if st.session_state.result_message: st.success(st.session_state.result_message)
    else: st.info("Select a problem to get started.")
    with st.expander("📊 View Statistics", expanded=True):
        if st.session_state.current_problem:
            stats_solutions = st.session_state.decisions.get(st.session_state.current_problem, [])
            st.metric("Solution Count", len(stats_solutions))
            if stats_solutions:
                solutions_with_history = [s for s in stats_solutions if s.get("history", 0) > 0]
                if solutions_with_history:
                    max_history = max(s['history'] for s in solutions_with_history)
                    most_chosen_list = [s['solutions'] for s in solutions_with_history if s['history'] == max_history]
                    st.write(f"**Most Chosen:** {', '.join(most_chosen_list)} ({max_history} times)")
                else: st.write("**Most Chosen:** None chosen yet.")
                unchosen_solutions = [s['solutions'] for s in stats_solutions if s.get('history', 0) == 0]
                if unchosen_solutions: st.write(f"**Least Chosen:** {', '.join(unchosen_solutions)} (0 times)")
                elif solutions_with_history:
                    min_history = min(s['history'] for s in solutions_with_history)
                    least_chosen_list = [s['solutions'] for s in solutions_with_history if s['history'] == min_history]
                    st.write(f"**Least Chosen:** {', '.join(least_chosen_list)} ({min_history} times)")
            else: st.write("**Most Chosen:** No solutions yet.")
        else: st.info("Select a problem to view stats.")