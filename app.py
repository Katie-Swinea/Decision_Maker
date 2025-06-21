import os
import json
import random
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# One file to hold all the problem and solution information
DECISION_FILE = "decisions.json"

# Variable to remember the last mood entered this session
last_entered_mood = ""


def load_json_file(filepath):
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        messagebox.showwarning("Warning", "{} is corrupted or missing. A new file will be created.".format(filepath))
    return {}


def save_json_file(data, filepath):
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except (OSError, PermissionError) as e:
        messagebox.showerror("Error", "Failed to save to {}: {}".format(filepath, e))


decisions = load_json_file(DECISION_FILE) # Load information if it exists

# UI setup
root = tk.Tk()
root.title("Decision Helper")
root.geometry("600x400")

main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

output_text = tk.Text(main_frame, wrap=tk.WORD, height=10)
output_text.pack(pady=10, fill=tk.X)

problem_var = tk.StringVar()
solution_var = tk.StringVar()
preference_var = tk.StringVar()

problem_label = tk.Label(main_frame, text="Select or enter a problem:")
problem_label.pack()
problem_combo = ttk.Combobox(main_frame, textvariable=problem_var, values=list(decisions.keys()))
problem_combo.pack(fill=tk.X)

add_problem_button = tk.Button(main_frame, text="Add Problem", command=lambda: add_problem(problem_var.get()))
add_problem_button.pack(pady=5)

solution_label = tk.Label(main_frame, text="Enter a solution:")
solution_label.pack()
solution_entry = tk.Entry(main_frame, textvariable=solution_var)
solution_entry.pack(fill=tk.X)

add_solution_button = tk.Button(main_frame, text="Add Solution",
                                command=lambda: add_solution(problem_var.get(), solution_var.get()))
add_solution_button.pack(pady=5)

choose_frame = tk.Frame(main_frame, pady=10)
choose_frame.pack()

preference_label = tk.Label(choose_frame, text="Choose preference:")
preference_label.grid(row=0, column=0, padx=5)
preference_dropdown = ttk.Combobox(choose_frame, textvariable=preference_var, state="readonly")
preference_dropdown['values'] = ("default", "ranking", "mood", "history")
preference_dropdown.current(0)
preference_dropdown.grid(row=0, column=1, padx=5)

choose_button = tk.Button(choose_frame, text="Choose Solution", command=lambda: get_solution(problem_var.get()))
choose_button.grid(row=0, column=2, padx=5)


def add_problem(problem):
    # Makes sure the user enters a problem
    if not problem:
        messagebox.showwarning("Missing Input", "Problem cannot be empty.", parent=root)
        return
    # Adds problem to file if doesn't exist
    if problem not in decisions:
        decisions[problem] = []
        save_json_file(decisions, DECISION_FILE)
        problem_combo['values'] = list(decisions.keys())
        problem_combo.set(problem)
        output_text.insert(tk.END, "Added new problem: {}\n".format(problem))


def add_solution(problem, solution):
    # Makes sure problem has a solution
    if not solution:
        messagebox.showwarning("Missing Input", "Solution cannot be empty.", parent=root)
        return
    # Makes sure a problem has been selected
    if not problem:
        messagebox.showerror("Error", "Please select or add a problem first.", parent=root)
        return
    # Adds solution so long as it doesn't exist
    for sol in decisions.get(problem, []):
        if isinstance(sol, dict) and sol.get("solutions") == solution:
            messagebox.showinfo("Info", "Solution already exists.", parent=root)
            return
        elif isinstance(sol, str) and sol == solution:
            messagebox.showinfo("Info", "Solution already exists.", parent=root)
            return

    entry = {"solutions": solution, "ranking": None, "mood": [], "history": 0} # Fills out json information
    decisions[problem].append(entry)
    save_json_file(decisions, DECISION_FILE)
    output_text.insert(tk.END, "Added solution: {}\n".format(solution))
    solution_var.set("")


def get_solution(problem):
    # This global statement allows us to modify the last_entered_mood variable
    global last_entered_mood # Used for convience so the same mood can be used when retrying decision

    if not problem:
        messagebox.showerror("Error", "No problem selected.", parent=root)
        return

    all_solutions_raw = decisions.get(problem, [])
    solutions = [s for s in all_solutions_raw if isinstance(s, dict)]

    if not solutions:
        messagebox.showinfo("Info", "This problem has no valid solutions to choose from.", parent=root)
        return

    pref = preference_var.get()
    # Additions to solutions like the rank and mood fields
    made_changes = False
    for sol in solutions:
        if pref == "ranking" and sol.get("ranking") is None:
            rank = simpledialog.askinteger("Input Required", "Enter rank for solution:\n'{}'".format(sol['solutions']),
                                           parent=root, minvalue=1)
            sol["ranking"] = rank
            made_changes = True
        elif pref == "mood" and not sol.get("mood"):
            mood_input = simpledialog.askstring("Input Required",
                                                "Enter moods (comma-separated) for:\n'{}'".format(sol['solutions']),
                                                parent=root)
            if mood_input is not None:
                sol["mood"] = [m.strip().lower() for m in mood_input.split(',') if m.strip()]
                made_changes = True

    if made_changes:
        save_json_file(decisions, DECISION_FILE)

    # Rejected decision and if changes are made logic
    selected = None
    if pref == "ranking":
        ranked = [s for s in solutions if isinstance(s.get("ranking"), int)]
        if ranked:
            min_rank = min(s["ranking"] for s in ranked)
            best = [s for s in ranked if s["ranking"] == min_rank]
            selected = random.choice(best)

    elif pref == "mood":
        all_possible_moods = set()
        for s in solutions:
            all_possible_moods.update(s.get("mood", []))

        if not all_possible_moods:
            messagebox.showinfo("Info",
                                "No solutions have moods. Please add moods via the dialogs or choose another preference.",
                                parent=root)
            return

        # The dialog now uses `initialvalue` to pre-fill the entry
        mood_input = simpledialog.askstring("Current Mood", "What is your current mood?",
                                            initialvalue=last_entered_mood,
                                            parent=root)
        if not mood_input:
            return

        current_mood = mood_input.strip().lower()
        # Remember this mood for the next time
        last_entered_mood = current_mood

        if current_mood not in all_possible_moods:
            messagebox.showwarning("Invalid Mood",
                                   "The mood '{}' is not associated with any solutions for this problem.".format(
                                       current_mood), parent=root)
            return

        mood_matches = [s for s in solutions if current_mood in s.get("mood", [])]
        selected = random.choice(mood_matches)

    elif pref == "history":
        hist_matches = [s for s in solutions if s.get("history", 0) > 0]
        if hist_matches:
            max_hist = max(s["history"] for s in hist_matches)
            selected = random.choice([s for s in hist_matches if s["history"] == max_hist])

    if not selected:
        if not solutions:
            messagebox.showinfo("Info", "No valid solutions to choose from.", parent=root)
            return
        selected = random.choice(solutions)

    result = selected["solutions"]
    output_text.insert(tk.END, "\nSuggested solution for '{}': {}\n".format(problem, result))

    response = messagebox.askquestion("Decision", "Do you accept this solution?\n{}".format(result), parent=root)
    if response == "yes":
        selected["history"] = selected.get("history", 0) + 1
        save_json_file(decisions, DECISION_FILE)
        output_text.insert(tk.END, "Decision accepted and history saved.\n")
    else:
        output_text.insert(tk.END, "Decision rejected. Feel free to try again.\n")


root.mainloop()