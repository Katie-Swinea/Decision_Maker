import os
import json
import random
from collections import Counter
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

# --- Constants & Original Theme ---
DECISION_FILE = "decisions.json"
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
        "body": ("Segoe UI", 13)
    }
}


# --- Main Application ---
class DecisionApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Core App Data
        self.decisions = self.load_json_file(DECISION_FILE)
        self.decision_log = []
        self.rejected_solutions = {}

        # Widget String Variables
        self.problem_var = ctk.StringVar()
        self.solution_var = ctk.StringVar()
        self.preference_var = ctk.StringVar(value="default (random)")
        self.avoid_repeats_var = ctk.BooleanVar(value=False)
        self.solution_widgets = []

        # UI setup
        self.title("✨ Decision Engine")
        self.geometry("1100x750")
        self.configure(fg_color=STYLE["colors"]["base"])
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=1)

        self.create_menu()
        self.create_widgets()

        self.problem_var.trace_add("write", self.on_problem_change)
        if list(self.decisions.keys()):
            self.problem_var.set(list(self.decisions.keys())[0])
        else:
            self.on_problem_change()

    def create_menu(self):
        menubar = tk.Menu(self)
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="How It Works", command=self.show_how_it_works)
        menubar.add_cascade(label="Help", menu=help_menu)
        self.config(menu=menubar)

    def create_widgets(self):
        colors, fonts = STYLE["colors"], STYLE["fonts"]

        # Left Column
        left_frame = ctk.CTkFrame(self, fg_color="transparent")
        left_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        left_frame.grid_rowconfigure(2, weight=1)

        problem_frame = ctk.CTkFrame(left_frame, fg_color=colors["frame"], border_color=colors["purple"],
                                     border_width=2)
        problem_frame.grid(row=0, column=0, sticky="ew")
        problem_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(problem_frame, text="🤔 Problem", font=fonts["header"], text_color=colors["text_highlight"]).grid(
            row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        self.problem_combo = ctk.CTkComboBox(problem_frame, variable=self.problem_var,
                                             values=list(self.decisions.keys()), text_color=colors["text_highlight"],
                                             fg_color=colors["base"], border_color=colors["purple"],
                                             button_color=colors["cyan"])
        self.problem_combo.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.delete_problem_btn = ctk.CTkButton(problem_frame, text="Delete Current Problem",
                                                command=self.delete_current_problem)
        self.delete_problem_btn.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        ctk.CTkLabel(problem_frame, text="Or, add a new problem:", text_color=colors["text"]).grid(row=3, column=0,
                                                                                                   padx=15,
                                                                                                   pady=(10, 0),
                                                                                                   sticky="w")
        self.new_problem_entry = ctk.CTkEntry(problem_frame, placeholder_text="Enter new problem name...",
                                              text_color=colors["text_highlight"], fg_color=colors["base"],
                                              border_color=colors["purple"])
        self.new_problem_entry.grid(row=4, column=0, padx=15, pady=5, sticky="ew")
        ctk.CTkButton(problem_frame, text="Add Problem", command=self.add_problem, fg_color=colors["cyan"],
                      text_color=colors["base"]).grid(row=5, column=0, padx=15, pady=(5, 15), sticky="ew")

        # Add Solution Section
        add_solution_frame = ctk.CTkFrame(left_frame, fg_color=colors["frame"], border_color=colors["purple"],
                                          border_width=2)
        add_solution_frame.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        add_solution_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(add_solution_frame, text="💡 Add Solution", font=fonts["header"],
                     text_color=colors["text_highlight"]).grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        self.solution_entry = ctk.CTkEntry(add_solution_frame, textvariable=self.solution_var,
                                           placeholder_text="Enter a possible solution...",
                                           text_color=colors["text_highlight"], fg_color=colors["base"],
                                           border_color=colors["purple"])
        self.solution_entry.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        ctk.CTkButton(add_solution_frame, text="Add Solution", command=self.add_solution, fg_color=colors["cyan"],
                      text_color=colors["base"]).grid(row=2, column=0, padx=15, pady=(5, 15), sticky="ew")

        # Existing Solutions Section
        self.existing_solutions_frame = ctk.CTkFrame(left_frame, fg_color=colors["frame"],
                                                     border_color=colors["purple"], border_width=2)
        self.existing_solutions_frame.grid(row=2, column=0, sticky="nsew", pady=(20, 0))
        self.existing_solutions_frame.grid_columnconfigure(0, weight=1)
        self.existing_solutions_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self.existing_solutions_frame, text="📝 Edit Existing Solutions", font=fonts["header"],
                     text_color=colors["text_highlight"]).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")
        self.solutions_list_frame = ctk.CTkScrollableFrame(self.existing_solutions_frame, fg_color=colors["base"])
        self.solutions_list_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        self.solutions_list_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(self.existing_solutions_frame, text="Save All Changes", command=self.save_all_changes).grid(row=2,
                                                                                                                  column=0,
                                                                                                                  padx=15,
                                                                                                                  pady=(
                                                                                                                  5,
                                                                                                                  15),
                                                                                                                  sticky="ew")

        # --- Right Column ---
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        right_frame.grid_rowconfigure(2, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        choose_frame = ctk.CTkFrame(right_frame, fg_color=colors["frame"], border_color=colors["purple"],
                                    border_width=2)
        choose_frame.grid(row=0, column=0, sticky="ew")
        choose_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(choose_frame, text="🚀 Let's Choose!", font=fonts["header"],
                     text_color=colors["text_highlight"]).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10),
                                                               sticky="w")
        ctk.CTkSwitch(choose_frame, text="Avoid Repeats", variable=self.avoid_repeats_var, onvalue=True, offvalue=False,
                      text_color=colors["text"]).grid(row=1, column=0, padx=15, pady=5, sticky="w")
        ctk.CTkLabel(choose_frame, text="Preference:", text_color=colors["text"]).grid(row=2, column=0, padx=15, pady=5,
                                                                                       sticky="w")
        self.preference_dropdown = ctk.CTkComboBox(choose_frame, variable=self.preference_var,
                                                   values=["default (random)", "ranking", "mood", "most chosen",
                                                           "least chosen", "trendy"],
                                                   text_color=colors["text_highlight"], fg_color=colors["base"],
                                                   border_color=colors["purple"], button_color=colors["orange"])
        self.preference_dropdown.grid(row=2, column=1, padx=15, pady=5, sticky="ew")
        ctk.CTkButton(choose_frame, text="Choose For Me!", fg_color=colors["orange"], text_color=colors["base"],
                      command=self.get_solution).grid(row=3, column=0, columnspan=2, padx=15, pady=(10, 15),
                                                      sticky="ew")

        stats_frame = ctk.CTkFrame(right_frame, fg_color=colors["frame"], border_color=colors["purple"], border_width=2)
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(20, 0))
        ctk.CTkLabel(stats_frame, text="📊 Statistics", font=fonts["header"], text_color=colors["text_highlight"]).pack(
            padx=15, pady=(15, 10), anchor="w")
        self.stats_text = ctk.CTkLabel(stats_frame, text="", justify="left", wraplength=400,
                                       text_color=colors["text_highlight"])
        self.stats_text.pack(padx=15, pady=(0, 15), anchor="w")

        self.results_box = ctk.CTkTextbox(right_frame, wrap="word", fg_color=colors["frame"],
                                          border_color=colors["purple"], border_width=2,
                                          text_color=colors["text_highlight"])
        self.results_box.grid(row=2, column=0, pady=(20, 0), sticky="nsew")

    def on_problem_change(self, *args):
        self.update_solutions_list()
        self.update_stats()

    def update_solutions_list(self):
        for widget in self.solutions_list_frame.winfo_children(): widget.destroy()
        self.solution_widgets = []
        problem = self.problem_var.get()
        if not problem: return

        solutions = self.decisions.get(problem, [])
        for i, sol in enumerate(solutions):
            sol_frame = ctk.CTkFrame(self.solutions_list_frame, fg_color="transparent")
            sol_frame.grid(row=i, column=0, sticky="ew", pady=2)
            sol_frame.grid_columnconfigure(0, weight=3);
            sol_frame.grid_columnconfigure(1, weight=1);
            sol_frame.grid_columnconfigure(2, weight=2)
            ctk.CTkLabel(sol_frame, text=sol['solutions'], text_color=STYLE["colors"]["text_highlight"]).grid(row=0,
                                                                                                              column=0,
                                                                                                              sticky="w")

            rank_var = ctk.StringVar(value=str(sol.get("ranking") or 0))
            mood_var = ctk.StringVar(value=", ".join(sol.get("mood", [])))

            ctk.CTkEntry(sol_frame, textvariable=rank_var, width=50, text_color=STYLE["colors"]["text_highlight"],
                         fg_color=STYLE["colors"]["base"]).grid(row=0, column=1, padx=5)
            ctk.CTkEntry(sol_frame, textvariable=mood_var, text_color=STYLE["colors"]["text_highlight"],
                         fg_color=STYLE["colors"]["base"]).grid(row=0, column=2, padx=5)
            ctk.CTkButton(sol_frame, text="🗑️", width=20, fg_color="transparent", text_color="red",
                          command=lambda s=sol['solutions']: self.delete_solution(s)).grid(row=0, column=3, padx=5)

            self.solution_widgets.append({"solution": sol['solutions'], "rank_var": rank_var, "mood_var": mood_var})

    def save_all_changes(self):
        problem = self.problem_var.get()
        if not problem: return
        for widget_info in self.solution_widgets:
            for sol_data in self.decisions[problem]:
                if sol_data['solutions'] == widget_info['solution']:
                    try:
                        sol_data['ranking'] = int(widget_info['rank_var'].get())
                    except (ValueError, TypeError):
                        sol_data['ranking'] = 0
                    sol_data['mood'] = [m.strip().lower() for m in widget_info['mood_var'].get().split(',') if
                                        m.strip()]
                    break
        self.save_json_file(self.decisions, DECISION_FILE)
        messagebox.showinfo("Success", "All changes have been saved.")
        self.update_stats()

    def update_stats(self):
        problem = self.problem_var.get()
        if not problem:
            self.stats_text.configure(text="Select a problem to view stats.")
            return
        stats_solutions = self.decisions.get(problem, [])
        count_text = f"Solution Count: {len(stats_solutions)}\n"
        most_chosen_text, least_chosen_text = "Most Chosen: None chosen yet.", "Least Chosen: "
        if stats_solutions:
            solutions_with_history = [s for s in stats_solutions if s.get("history", 0) > 0]
            if solutions_with_history:
                max_history = max(s['history'] for s in solutions_with_history)
                most_chosen_list = [s['solutions'] for s in solutions_with_history if s['history'] == max_history]
                most_chosen_text = f"Most Chosen: {', '.join(most_chosen_list)} ({max_history} times)"
            unchosen_solutions = [s['solutions'] for s in stats_solutions if s.get('history', 0) == 0]
            if unchosen_solutions:
                least_chosen_text += f"{', '.join(unchosen_solutions)} (0 times)"
            elif solutions_with_history:
                min_history = min(s['history'] for s in solutions_with_history)
                least_chosen_list = [s['solutions'] for s in solutions_with_history if s['history'] == min_history]
                least_chosen_text += f"{', '.join(least_chosen_list)} ({min_history} times)"
        self.stats_text.configure(text=count_text + most_chosen_text + "\n" + least_chosen_text)

    def get_solution(self):
        problem = self.problem_var.get()
        if not problem: messagebox.showerror("Error", "No problem selected."); return
        solutions = self.decisions.get(problem, [])
        if not solutions: messagebox.showinfo("Info", "This problem has no solutions."); return

        eligible_solutions = solutions
        if self.avoid_repeats_var.get():
            rejected = self.rejected_solutions.get(problem, set())
            eligible_solutions = [s for s in solutions if s['solutions'] not in rejected]
            if not eligible_solutions:
                messagebox.showinfo("Reset", "All options have been suggested. Resetting 'Avoid Repeats' list.")
                self.rejected_solutions[problem] = set()
                eligible_solutions = solutions

        selected, reason = None, ""
        pref_logic = self.preference_var.get().split(" ")[0]

        if pref_logic == "ranking":
            ranked = [s for s in eligible_solutions if s.get("ranking", 0) > 0]
            if ranked:
                min_rank = min(s['ranking'] for s in ranked)
                best = [s for s in ranked if s['ranking'] == min_rank]
                selected, reason = random.choice(best), f"Chosen for its top rank of {min_rank}."
            else:
                messagebox.showwarning("Warning", "No solutions have been ranked yet.")
        elif pref_logic == "mood":
            # Using simpledialog as custom dialog is not available in this context
            mood = simpledialog.askstring("Input", "What is your current mood?", parent=self)
            if mood:
                mood = mood.lower()
                mood_matches = [s for s in eligible_solutions if mood in s.get("mood", [])]
                if mood_matches:
                    selected, reason = random.choice(mood_matches), f"Chosen for matching the mood '{mood}'."
                else:
                    messagebox.showwarning("Warning", f"No solutions found for the mood '{mood}'.")
        elif pref_logic == "most":
            hist = [s for s in eligible_solutions if s.get("history", 0) > 0]
            if hist:
                max_hist = max(s['history'] for s in hist)
                most_chosen = [s for s in hist if s['history'] == max_hist]
                selected, reason = random.choice(most_chosen), f"Chosen for being the most popular ({max_hist} times)."
        elif pref_logic == "least":
            min_hist = min(s.get("history", 0) for s in eligible_solutions)
            least_chosen = [s for s in eligible_solutions if s.get("history", 0) == min_hist]
            selected, reason = random.choice(least_chosen), f"Chosen for being picked least often ({min_hist} times)."
        elif pref_logic == "trendy":
            if self.decision_log:
                last_5 = self.decision_log[-5:]
                most_common = Counter(last_5).most_common(1)[0][0]
                for sol in eligible_solutions:
                    if sol['solutions'] == most_common:
                        selected, reason = sol, "Chosen for being trendy recently.";
                        break

        if not selected and eligible_solutions:
            selected, reason = random.choice(eligible_solutions), "Chosen at random."

        if selected: self.display_result(problem, selected, reason)

    def display_result(self, problem, solution_data, reason):
        solution_text = solution_data["solutions"]
        self.results_box.delete("1.0", "end")
        self.results_box.insert("end", f"For '{problem}', the suggested solution is:\n\n")
        self.results_box.insert("end", f"--- {solution_text} ---\n\n")
        self.results_box.insert("end", f"Reason: {reason}\n\n")

        response = messagebox.askquestion("Accept Solution?", f"Do you accept this solution?\n\n{solution_text}",
                                          parent=self)
        if response == 'yes':
            solution_data['history'] += 1
            self.decision_log.append(solution_text)
            self.save_json_file(self.decisions, DECISION_FILE)
            self.results_box.insert("end", "Decision Accepted!")
            self.update_stats()
        else:
            if self.avoid_repeats_var.get():
                self.rejected_solutions.setdefault(problem, set()).add(solution_text)
            self.results_box.insert("end", "Decision Rejected.")

    def load_json_file(self, filepath):
        if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            with open(filepath, 'w') as f: json.dump({}, f)
            return {}
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            messagebox.showerror("Error", f"{filepath} is corrupted or missing.");
            return {}

    def save_json_file(self, data, filepath):
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except (OSError, PermissionError) as e:
            messagebox.showerror("Error", f"Failed to save to {filepath}: {e}")

    def add_problem(self):
        problem = self.new_problem_entry.get()
        if not problem: messagebox.showwarning("Missing Input", "Problem name cannot be empty."); return
        if problem not in self.decisions:
            self.decisions[problem] = []
            self.save_json_file(self.decisions, DECISION_FILE)
            self.problem_combo.configure(values=list(self.decisions.keys()))
            self.problem_var.set(problem)
            self.new_problem_entry.delete(0, 'end')
        else:
            messagebox.showinfo("Info", "This problem already exists.")

    def add_solution(self):
        problem, solution = self.problem_var.get(), self.solution_var.get()
        if not problem: messagebox.showerror("Error", "Please select a problem first."); return
        if not solution: messagebox.showwarning("Missing Input", "Solution cannot be empty."); return
        if solution not in [s['solutions'] for s in self.decisions[problem]]:
            self.decisions[problem].append({"solutions": solution, "ranking": 0, "mood": [], "history": 0})
            self.save_json_file(self.decisions, DECISION_FILE)
            self.solution_var.set("");
            self.on_problem_change()
        else:
            messagebox.showinfo("Info", "This solution already exists.")

    def delete_current_problem(self):
        problem = self.problem_var.get()
        if not problem: return
        if messagebox.askyesno("Confirm Deletion",
                               f"Are you sure you want to delete '{problem}' and all its solutions? This cannot be undone."):
            del self.decisions[problem]
            self.save_json_file(self.decisions, DECISION_FILE)
            remaining_problems = list(self.decisions.keys())
            self.problem_combo.configure(values=remaining_problems)
            self.problem_var.set(remaining_problems[0] if remaining_problems else "")

    def delete_solution(self, solution_to_delete):
        problem = self.problem_var.get()
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{solution_to_delete}'?"):
            self.decisions[problem] = [s for s in self.decisions[problem] if s['solutions'] != solution_to_delete]
            self.save_json_file(self.decisions, DECISION_FILE)
            self.on_problem_change()

    def show_how_it_works(self):
        message = (
            "- Default (Random): Picks any solution at random.\n"
            "- Ranking: Picks from solutions with the lowest rank number (1 is best).\n"
            "- Mood: Suggests a solution matching your entered mood.\n"
            "- Most Chosen: Picks from solutions with the highest history count.\n"
            "- Least Chosen: Picks from solutions with the lowest history count.\n"
            "- Trendy: Picks the solution chosen most often in the last 5 accepted decisions.\n"
            "- Avoid Repeats: Prevents recently rejected solutions from being suggested."
        )
        messagebox.showinfo("How It Works", message)


if __name__ == "__main__":
    app = DecisionApp()
    app.mainloop()