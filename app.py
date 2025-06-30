import os
import json
import random
import customtkinter as ctk
from tkinter import messagebox, simpledialog

# One file to hold all the problem and solution information
DECISION_FILE = "decisions.json"

# Configs for pretty UI
STYLE = {
    "colors": {
        "base": "#002b36",
        "frame": "#073642",
        "text": "#839496",
        "text_highlight": "#93a1a1",
        "cyan": "#2aa198",
        "orange": "#cb4b16",
        "purple": "#d33682",
    },
    "fonts": {
        "header": ("Segoe UI", 18, "bold"),
        "body": ("Segoe UI", 13),
        "button": ("Segoe UI", 13, "bold"),
    },
    "icons": {
        "problem": "🤔",
        "solution": "💡",
        "action": "✨",
        "choose": "🚀",
        "results": "📋",
        "stats": "📊",
        "list": "📝"
    }
}


class DecisionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.decisions = self.load_json_file(DECISION_FILE)
        self.last_entered_mood = ""

        # Outputs for widgets (which look so much better now)
        self.problem_var = ctk.StringVar()
        self.solution_var = ctk.StringVar()
        self.preference_var = ctk.StringVar(value="default (random)")

        # Update displayed solutions list
        self.problem_var.trace_add("write", self.update_solutions_list)

        # Intial text
        self.stat_solution_count = ctk.StringVar(value="--")
        self.stat_most_chosen = ctk.StringVar(value="--")
        self.stat_least_chosen = ctk.StringVar(value="--")

        # UI setup
        self.title(f"{STYLE['icons']['action']} Decision Engine {STYLE['icons']['action']}")
        self.geometry("950x650")
        self.configure(fg_color=STYLE["colors"]["base"])
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)
        self.create_widgets()
        self.update_solutions_list()
        self.update_stats()

    def create_widgets(self):
        colors, fonts, icons = STYLE["colors"], STYLE["fonts"], STYLE["icons"]

        # Left column
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        left_frame.grid_rowconfigure(2, weight=1)

        # Problem box
        problem_frame = ctk.CTkFrame(left_frame, fg_color=colors["frame"], border_color=colors["purple"],
                                     border_width=2)
        problem_frame.grid(row=0, column=0, sticky="ew")
        problem_frame.grid_columnconfigure(0, weight=1)
        problem_label = ctk.CTkLabel(problem_frame, text=f"{icons['problem']} Problem", font=fonts["header"],
                                     text_color=colors["text_highlight"])
        problem_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        self.problem_combo = ctk.CTkComboBox(problem_frame, variable=self.problem_var,
                                             values=list(self.decisions.keys()), font=fonts["body"],
                                             fg_color=colors["base"], border_color=colors["purple"],
                                             button_color=colors["cyan"],
                                             text_color=colors["text_highlight"], dropdown_fg_color=colors["frame"],
                                             dropdown_hover_color=colors["cyan"],
                                             dropdown_text_color=colors["text_highlight"],
                                             command=self.update_stats)
        self.problem_combo.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        add_problem_button = ctk.CTkButton(problem_frame, text=f"Add {icons['problem']}", font=fonts["button"],
                                           fg_color=colors["cyan"], text_color=colors["base"],
                                           command=lambda: self.add_problem(self.problem_var.get()))
        add_problem_button.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="ew")

        # Add Solution box
        add_solution_frame = ctk.CTkFrame(left_frame, fg_color=colors["frame"], border_color=colors["purple"],
                                          border_width=2)
        add_solution_frame.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        add_solution_frame.grid_columnconfigure(0, weight=1)
        solution_label = ctk.CTkLabel(add_solution_frame, text=f"{icons['solution']} Add Solution",
                                      font=fonts["header"], text_color=colors["text_highlight"])
        solution_label.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        solution_entry = ctk.CTkEntry(add_solution_frame, textvariable=self.solution_var,
                                      placeholder_text="Enter a possible solution...", font=fonts["body"],
                                      fg_color=colors["base"], border_color=colors["purple"],
                                      text_color=colors["text_highlight"])
        solution_entry.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        add_solution_button = ctk.CTkButton(add_solution_frame, text=f"Add {icons['solution']}", font=fonts["button"],
                                            fg_color=colors["cyan"], text_color=colors["base"],
                                            command=lambda: self.add_solution(self.problem_var.get(),
                                                                              self.solution_var.get()))
        add_solution_button.grid(row=2, column=0, padx=15, pady=(5, 15), sticky="ew")

        # Solutions display box
        existing_solutions_frame = ctk.CTkFrame(left_frame, fg_color=colors["frame"], border_color=colors["purple"],
                                                border_width=2)
        existing_solutions_frame.grid(row=2, column=0, sticky="nsew", pady=(20, 0))
        existing_solutions_frame.grid_columnconfigure(0, weight=1)
        existing_solutions_frame.grid_rowconfigure(1, weight=1)
        solutions_list_label = ctk.CTkLabel(existing_solutions_frame, text=f"{icons['list']} Existing Solutions",
                                            font=fonts["header"], text_color=colors["text_highlight"])
        solutions_list_label.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        self.solutions_list_frame = ctk.CTkScrollableFrame(existing_solutions_frame, fg_color=colors["base"])
        self.solutions_list_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))

        # Right column
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        choose_frame = ctk.CTkFrame(right_frame, fg_color=colors["frame"], border_color=colors["purple"],
                                    border_width=2)
        choose_frame.grid(row=0, column=0, sticky="ew")
        choose_frame.grid_columnconfigure(0, weight=1)
        choose_label = ctk.CTkLabel(choose_frame, text=f"{icons['action']} Choose by Preference", font=fonts["header"],
                                    text_color=colors["text_highlight"])
        choose_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")
        preference_dropdown = ctk.CTkComboBox(choose_frame, variable=self.preference_var,
                                              values=["default (random)", "ranking", "mood", "history"],
                                              state="readonly", font=fonts["body"],
                                              fg_color=colors["base"], border_color=colors["purple"],
                                              button_color=colors["orange"],
                                              text_color=colors["text_highlight"], dropdown_fg_color=colors["frame"],
                                              dropdown_hover_color=colors["orange"],
                                              dropdown_text_color=colors["text_highlight"])
        preference_dropdown.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="ew")
        choose_button = ctk.CTkButton(choose_frame, text=f"Choose! {icons['choose']}", font=fonts["button"],
                                      fg_color=colors["orange"], text_color=colors["base"],
                                      command=lambda: self.get_solution(self.problem_var.get()))
        choose_button.grid(row=1, column=1, padx=(0, 15), pady=(5, 15), sticky="e")
        stats_frame = ctk.CTkFrame(right_frame, fg_color=colors["frame"], border_color=colors["purple"], border_width=2)
        stats_frame.grid(row=1, column=0, pady=(20, 0), sticky="ew")
        stats_label = ctk.CTkLabel(stats_frame, text=f"{icons['stats']} Statistics", font=fonts["header"],
                                   text_color=colors["text_highlight"])
        stats_label.pack(padx=15, pady=(15, 10), anchor="w")
        ctk.CTkLabel(stats_frame, text="Solution Count:", font=fonts["body"], text_color=colors["text"]).pack(padx=15,
                                                                                                              anchor="w")
        ctk.CTkLabel(stats_frame, textvariable=self.stat_solution_count, font=fonts["body"],
                     text_color=colors["text_highlight"]).pack(padx=15, anchor="w")
        ctk.CTkLabel(stats_frame, text="Most Chosen:", font=fonts["body"], text_color=colors["text"]).pack(padx=15,
                                                                                                           pady=(10, 0),
                                                                                                           anchor="w")
        ctk.CTkLabel(stats_frame, textvariable=self.stat_most_chosen, font=fonts["body"],
                     text_color=colors["text_highlight"]).pack(padx=15, anchor="w")
        ctk.CTkLabel(stats_frame, text="Least Chosen:", font=fonts["body"], text_color=colors["text"]).pack(padx=15,
                                                                                                            pady=(
                                                                                                            10, 0),
                                                                                                            anchor="w")
        ctk.CTkLabel(stats_frame, textvariable=self.stat_least_chosen, font=fonts["body"],
                     text_color=colors["text_highlight"]).pack(padx=15, pady=(0, 15), anchor="w")

        results_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        results_frame.grid(row=2, column=0, pady=(20, 0), sticky="nsew")
        results_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(1, weight=1)
        results_label = ctk.CTkLabel(results_frame, text=f"{icons['results']} Results", font=fonts["header"],
                                     text_color=colors["text_highlight"])
        results_label.grid(row=0, column=0, sticky="w")
        self.output_text = ctk.CTkTextbox(results_frame, font=fonts["body"], wrap=ctk.WORD, fg_color=colors["frame"],
                                          height=150,
                                          text_color=colors["text"], border_color=colors["purple"], border_width=2)
        self.output_text.grid(row=1, column=0, pady=(5, 0), sticky="nsew")

    def update_solutions_list(self, *args):
        problem = self.problem_var.get()
        for widget in self.solutions_list_frame.winfo_children():
            widget.destroy()
        if problem and problem in self.decisions:
            solutions = [s['solutions'] for s in self.decisions.get(problem, []) if isinstance(s, dict)]
            if solutions:
                for sol_text in solutions:
                    label = ctk.CTkLabel(self.solutions_list_frame, text=f"• {sol_text}", font=STYLE["fonts"]["body"],
                                         wraplength=250, justify="left", text_color=STYLE["colors"]["text_highlight"])
                    label.pack(anchor="w", padx=5, pady=(0, 4))
            else:
                label = ctk.CTkLabel(self.solutions_list_frame, text="No solutions added yet.",
                                     font=STYLE["fonts"]["body"], text_color=STYLE["colors"]["text"])
                label.pack(anchor="w", padx=5)

    def update_stats(self, event=None):
        problem = self.problem_var.get()
        if not problem or problem not in self.decisions:
            # Init
            self.stat_solution_count.set("--")
            self.stat_most_chosen.set("Select a problem")
            self.stat_least_chosen.set("to see stats.")
            return
        solutions = [s for s in self.decisions.get(problem, []) if isinstance(s, dict)]
        self.stat_solution_count.set(str(len(solutions)))
        # For new problems
        if not solutions:
            self.stat_most_chosen.set("No solutions yet.")
            self.stat_least_chosen.set("")
            return
        solutions_with_history = [s for s in solutions if s.get("history", 0) > 0]
        if not solutions_with_history:
            self.stat_most_chosen.set("None chosen yet.")
            self.stat_least_chosen.set("None chosen yet.")
            return
        most_chosen = max(solutions_with_history, key=lambda s: s.get("history", 0))
        least_chosen = min(solutions_with_history, key=lambda s: s.get("history", 0))
        self.stat_most_chosen.set(f"{most_chosen['solutions']} ({most_chosen['history']} times)")
        self.stat_least_chosen.set(f"{least_chosen['solutions']} ({least_chosen['history']} times)")

    # For clean output since the log is now results of a single decision process
    def clear_log_box(self):
        if self.output_text and self.output_text.winfo_exists():
            self.output_text.delete("1.0", ctk.END)

    def load_json_file(self, filepath):
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f: return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            messagebox.showwarning("Warning", f"{filepath} is corrupted or missing. A new file will be created.")
        return {}

    def save_json_file(self, data, filepath):
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except (OSError, PermissionError) as e:
            messagebox.showerror("Error", f"Failed to save to {filepath}: {e}")

    def add_problem(self, problem):
        # User validation
        if not problem: messagebox.showwarning("Missing Input", "Problem cannot be empty.", parent=self); return
        if problem not in self.decisions:
            self.decisions[problem] = []
            self.save_json_file(self.decisions, DECISION_FILE)
            self.problem_combo.configure(values=list(self.decisions.keys()))
            self.problem_combo.set(problem)
            self.output_text.insert("end", f"{STYLE['icons']['problem']} Added new problem: {problem}\n")
            self.update_stats()
            self.update_solutions_list()

    def add_solution(self, problem, solution):
        # User validation
        if not solution: messagebox.showwarning("Missing Input", "Solution cannot be empty.", parent=self); return
        if not problem: messagebox.showerror("Error", "Please select or add a problem first.", parent=self); return
        # No duplicates
        for sol in self.decisions.get(problem, []):
            if (isinstance(sol, dict) and sol.get("solutions") == solution) or (
                    isinstance(sol, str) and sol == solution):
                messagebox.showinfo("Info", "Solution already exists.", parent=self);
                return
        entry = {"solutions": solution, "ranking": None, "mood": [], "history": 0}
        self.decisions[problem].append(entry)
        self.save_json_file(self.decisions, DECISION_FILE)
        self.output_text.insert("end", f"{STYLE['icons']['solution']} Added solution: {solution}\n")
        self.solution_var.set("")
        self.update_stats()
        self.update_solutions_list()

    def get_solution(self, problem):
        # User validation
        if not problem: messagebox.showerror("Error", "No problem selected.", parent=self); return

        pref = self.preference_var.get()
        if pref == "default (random)":
            pref = "default"

        all_solutions_raw = self.decisions.get(problem, [])
        solutions = [s for s in all_solutions_raw if isinstance(s, dict)]
        # Ensures decision can be made
        if not solutions: messagebox.showinfo("Info", "This problem has no valid solutions to choose from.",
                                              parent=self); return
        made_changes = False
        # To ensure all information is filled out for a solution preference pairing
        for sol in solutions:
            if pref == "ranking" and sol.get("ranking") is None:
                rank = simpledialog.askinteger("Input Required", f"Enter rank for solution:\n'{sol['solutions']}'",
                                               parent=self, minvalue=1)
                if rank is not None: sol["ranking"], made_changes = rank, True
            elif pref == "mood" and not sol.get("mood"):
                mood_input = simpledialog.askstring("Input Required",
                                                    f"Enter moods (comma-separated) for:\n'{sol['solutions']}'",
                                                    parent=self)
                if mood_input is not None: sol["mood"], made_changes = [m.strip().lower() for m in mood_input.split(',')
                                                                        if m.strip()], True

        if made_changes: self.save_json_file(self.decisions, DECISION_FILE) # Updates solutions

        selected = None
        if pref == "ranking":
            ranked = [s for s in solutions if isinstance(s.get("ranking"), int)]
            if ranked: min_rank = min(s["ranking"] for s in ranked); selected = random.choice(
                [s for s in ranked if s["ranking"] == min_rank])
        elif pref == "mood":
            all_possible_moods = {m for s in solutions for m in s.get("mood", [])}
            if not all_possible_moods: messagebox.showinfo("Info",
                                                           "No solutions have moods. Please add moods or choose another preference.",
                                                           parent=self); return
            mood_input = simpledialog.askstring("Current Mood", "What is your current mood?", parent=self,
                                                initialvalue=self.last_entered_mood)
            if not mood_input: return
            self.last_entered_mood = mood_input.strip().lower()
            mood_matches = [s for s in solutions if self.last_entered_mood in s.get("mood", [])]
            if not mood_matches: messagebox.showwarning("Invalid Mood",
                                                        f"The mood '{self.last_entered_mood}' is not associated with any solutions.",
                                                        parent=self); return
            selected = random.choice(mood_matches)
        elif pref == "history":
            hist_matches = [s for s in solutions if s.get("history", 0) > 0]
            if hist_matches: min_hist = min(s["history"] for s in hist_matches); selected = random.choice(
                [s for s in hist_matches if s["history"] == min_hist])

        # User validation
        if not selected:
            if not solutions: messagebox.showinfo("Info", "No valid solutions to choose from.", parent=self); return
            selected = random.choice(solutions)

        result = selected["solutions"]
        self.output_text.insert("end",
                                f"\n{STYLE['icons']['choose']} Suggested solution for '{problem}':\n--- {result} ---\n")
        response = messagebox.askquestion("Decision", f"Do you accept this solution?\n\n{result}", parent=self)
        if response == "yes":
            selected["history"] = selected.get("history", 0) + 1 # Update history
            self.save_json_file(self.decisions, DECISION_FILE)
            self.output_text.insert("end", "Decision accepted and history updated.\n")
            self.after(3000, self.clear_log_box)
        else:
            self.output_text.insert("end", "Decision rejected. Feel free to try again.\n")
        self.update_stats()


if __name__ == "__main__":
    app = DecisionApp()
    app.mainloop()