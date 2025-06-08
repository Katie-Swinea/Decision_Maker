import os
import json
import random
import textwrap
import tkinter as tk
from tkinter import messagebox, simpledialog

# Constants
DECISION_FILE = "decisions.json"
PREFERENCE_FILE = "preferences.json"
HISTORY_FILE = "history.json"

# Load or initialize JSON data safely
def load_json_file(filepath):
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        messagebox.showwarning("Warning", f"{filepath} is corrupted or missing. Resetting file.")
    return {}

def save_json_file(data, filepath):
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
    except (OSError, PermissionError) as e:
        messagebox.showerror("Error", f"Failed to save to {filepath}: {e}")

# Load data files
decisions = load_json_file(DECISION_FILE)
preferences = load_json_file(PREFERENCE_FILE)
history = load_json_file(HISTORY_FILE)

# GUI setup
root = tk.Tk()
root.title("Decision Helper")
root.geometry("600x400")

output_text = tk.Text(root, wrap=tk.WORD, height=15)
output_text.pack(pady=10)

# Functions

def ask_preferences():
    options = ["default", "ranking", "mood", "history"]
    choice = simpledialog.askstring("Preferences", f"Choose preference: {', '.join(options)}")
    if choice in options:
        preferences["mode"] = choice
        if choice == "mood":
            moods = simpledialog.askstring("Moods", "Enter a list of moods separated by commas:")
            preferences["moods"] = [m.strip() for m in moods.split(',')] if moods else []
        save_json_file(preferences, PREFERENCE_FILE)
    else:
        messagebox.showerror("Invalid", "Invalid preference selected.")
        ask_preferences()

def choose_solution(problem):
    pref = preferences.get("mode", "default")
    solutions = decisions.get(problem, [])

    if not solutions:
        messagebox.showinfo("No Solutions", "No solutions found for this problem.")
        return None

    if pref == "ranking":
        try:
            ranked = [s for s in solutions if isinstance(s.get("ranking"), int)]
            if not ranked:
                raise ValueError("No ranked solutions")
            min_rank = min(s["ranking"] for s in ranked)
            best = [s for s in ranked if s["ranking"] == min_rank]
            return random.choice(best)
        except Exception as e:
            messagebox.showwarning("Ranking Error", f"{e}")

    elif pref == "mood":
        mood = simpledialog.askstring("Mood", "What is your current mood?")
        if mood:
            mood_solutions = [s for s in solutions if mood in s.get("mood", [])]
            if mood_solutions:
                return random.choice(mood_solutions)

    elif pref == "history":
        hist_matches = [s for s in solutions if s.get("history", 0) > 0]
        if hist_matches:
            max_score = max(s["history"] for s in hist_matches)
            return random.choice([s for s in hist_matches if s["history"] == max_score])
        else:
            messagebox.showinfo("History", "Not enough history data yet.")

    return random.choice(solutions)

def submit_problem():
    problem = simpledialog.askstring("Problem", "Enter a problem:")
    if not problem:
        return
    if problem not in decisions:
        decisions[problem] = []
        save_json_file(decisions, DECISION_FILE)

    pref = preferences.get("mode")
    if not pref:
        ask_preferences()

    while True:
        solution = simpledialog.askstring("Solution", "Enter a solution (or type 'stop' to finish):")
        if not solution or solution.lower() == 'stop':
            break

        exists = any(sol["solutions"] == solution for sol in decisions[problem])
        if not exists:
            entry = {
                "solutions": solution,
                "ranking": None,
                "mood": [],
                "history": 0
            }
            if pref == "ranking":
                try:
                    entry["ranking"] = int(simpledialog.askstring("Rank", "Enter a ranking (lower is better):"))
                except ValueError:
                    entry["ranking"] = None
            elif pref == "mood":
                entry["mood"] = [m.strip() for m in simpledialog.askstring("Moods", "Tag moods (comma-separated):").split(',')]
            decisions[problem].append(entry)
            save_json_file(decisions, DECISION_FILE)

    chosen = choose_solution(problem)
    if chosen:
        output_text.insert(tk.END, f"\nSuggested solution for '{problem}': {chosen['solutions']}\n")
        action = messagebox.askquestion("Confirm", "Do you accept this solution?")
        if action == 'yes':
            if preferences.get("mode") == "history":
                chosen["history"] += 1
                save_json_file(decisions, DECISION_FILE)
        else:
            retry = messagebox.askyesno("Retry", "Would you like to change preferences and try again?")
            if retry:
                ask_preferences()
                submit_problem()

# Buttons
tk.Button(root, text="Add Problem & Get Solution", command=submit_problem).pack()
tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

root.mainloop()
