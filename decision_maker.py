import json
import os
import random
import textwrap
from flask import Flask, request, render_template

DECISION_FILE = 'decisions.json'

app = Flask(__name__)

@app.route('/')
def home_page():
	return render_template('index.html')

@app.route('/run-script', methods=['POST'])
def run_decision_maker():
	decision = main()
	return f"{decision}"

def load_data():
	if os.path.exists(DECISION_FILE):
		with open(DECISION_FILE, 'r') as f:
			list = json.load(f)
			if isinstance(list, dict):
				return list

	return {}

def check_preferences(preferences):
	while preferences != 'num' and preferences != 'history' and preferences != 'mood' and preferences != 'default' :
		msg = textwrap.fill("Please choose if you want your choice to be made at random, based on a number ranking system, based on the context surrounding the choice, or based on the history of your old choices. ", width=100)
		settings = input("\n"+msg+" ")
		if settings.lower() == 'num' or settings.lower() == 'number' or settings.lower() == 'n' or settings.lower() == '#' or settings.lower() == 'rank' or settings.lower() == 'ranking' or settings.lower() == 'system' :
			preferences = 'num'
		if settings.lower() == 'mood' or settings.lower() == 'scene' or settings.lower() == 'scenario' or settings.lower() == 'circumstance' or settings.lower() == 's' or settings.lower() == 'context' :
			preferences = 'mood'
		if settings.lower() == 'previous' or settings.lower() == 'previous choice' or settings.lower() == 'previous choices' or settings.lower() == 'choice' or settings.lower() == 'choices' or settings.lower() == 'history' or settings.lower() == 'p' or settings.lower() == 'pc'  or settings.lower() == 'old':
			preferences = 'history'
		if settings.lower() == 'random' or settings.lower() == 'default' or settings.lower() == 'r' or settings.lower() == 'rand' :
			preferences = 'default'
	return preferences

def add_problem(input):
	if input not in decisions:
		decisions[input] = []
		with open(DECISION_FILE, 'w') as f:
			json.dump(decisions, f)

def add_solution(inPut, preferences):
	if inPut in decisions :
		msg = textwrap.fill("Enter an option for the problem. Enter 'stop' when you are finished.", width=100)
		solution = input("\n"+msg+" ")
		if preferences == 'default' :
			while solution.lower() != 'stop' :
				if solution not in decisions[inPut]:
					decisions[inPut].append({"solutions": solution, "ranking": [], "mood": [], "history": 0})
				with open(DECISION_FILE, 'w') as f:
					json.dump(decisions, f)
				msg = textwrap.fill("Enter an option for the problem. Enter 'stop' when you are finished.", width=100)
				solution = input("\n"+msg+" ")
		if preferences == 'num' :
			while solution.lower() != 'stop' :
				msg = textwrap.fill("Enter a ranking for that option. Remember more than one option can have the same ranking.", width=100)
				rank = input("\n"+msg+" ")
				if solution not in decisions[inPut]:
					decisions[inPut].append({"solutions": solution, "ranking": rank, "mood": [], "history": 0})
				with open(DECISION_FILE, 'w') as f:
					json.dump(decisions, f)
				msg = textwrap.fill("Enter an option for the problem. Enter 'stop' when you are finished.", width=100)
				solution = input("\n"+msg+" ")
		if preferences == 'mood' :
			while solution.lower() != 'stop' :
				msg = textwrap.fill("Enter a mood corresponding to this option. More than one option can have the same mood.", width=100)
				mood = input("\n"+msg+" ")
				if solution not in decisions[inPut]:
					decisions[inPut].append({"solutions": solution, "ranking": [], "mood": mood, "history": 0})
				with open(DECISION_FILE, 'w') as f:
					json.dump(decisions, f)
				msg = textwrap.fill("Enter an option for the problem. Enter 'stop' when you are finished.", width=100)
				solution = input("\n"+msg+" ")

def get_solutions(problem, decisions, preferences, mood):
	if problem not in decisions :
		add_problem(problem)
	while problem.lower() != 'exit' :
		while decisions[problem] == [] and preferences != 'mood' and preferences != 'default' and preferences != 'num':
			msg = textwrap.fill("You cannot use history with a new or empty problem because it has no previous data to use.", width=100)
			print("\n"+msg)
			msg = textwrap.fill("Please choose a different preference.", width=100)
			preferences = input("\n"+msg+" ")
			if preferences.lower() == 'num' or preferences.lower() == 'number' or preferences.lower() == 'n' or preferences.lower() == '#' or preferences.lower() == 'rank' or preferences.lower() == 'ranking' :
				preferences = 'num'
			if preferences.lower() == 'mood' or preferences.lower() == 'scene' or preferences.lower() == 'scenario' or preferences.lower() == 'circumstance' or preferences.lower() == 's' or preferences.lower() == 'context' :
				preferences = 'mood'
				msg = textwrap.fill("Please enter the mood that will be affecting your decision today.", width=100)
				mood = input("\n"+msg+" ")
			if preferences.lower() == 'default' or preferences.lower() == 'r' or preferences.lower() == 'rand' or preferences.lower() == 'random' :
				preferences = 'default'
		if decisions[problem] == [] :
			add_solution(problem, preferences)
		else:
			while (preferences == 'num' and decisions[problem][0]["ranking"] == []) or (preferences == 'mood' and decisions[problem][0]["mood"] == []):
				temp_problem = problem
				msg = textwrap.fill("Enter a problem that matches the preferences you have set for this sission. To change your preferences, enter 'cp' so the preferences match the problem. To add options to your problem, enter 'ap'.", width=100)
				problem = input("\n"+msg+" ")
				if problem.upper() == 'CP' or problem.lower() == 'change' or problem.lower() == 'preferences' or problem.lower() == 'change preferences' :
					problem = temp_problem
					msg = textwrap.fill("To do a number ranking, enter 'num', to do a cicrumstance ranking, enter 'circum', to do a choice based on your history, enter 'history', to have a random choice made, enter 'random'.", width=100)
					preferences = input("\n"+msg+" ")
					if preferences.lower() == 'circum' or preferences.lower() == 'circ' or preferences.lower() == 'circumstance' or preferences.lower() == 'circumstances' :
						preferences = 'mood'
						msg = textwrap.fill("Please enter the mood that will be affecting your decision today.", width=100)
						mood = input("\n"+msg+" ")
					if preferences.lower() == 'random' or preferences.lower() == 'rand' or preferences.lower() == 'r' :
						preferences = 'default'
					while preferences != 'num' and preferences != 'mood' and preferences != 'history' and preferences != 'default' :
						msg = textwrap.fill("To do a number ranking, enter 'num', to do a circumstance based ranking, enter 'circum', to do a choice based on your history, enter 'history', to make a random choice, enter 'random'.", width=100)
						print("\n"+msg)
				if problem.upper() == 'AP' or problem.lower() == 'add problem' or problem.lower() == 'add to problem' or problem.lower() == 'add' or problem.lower() == 'problme' :
					if preferences == 'num' :
						problem = temp_problem
						for solution in decisions[problem] :
							print(solution["solutions"])
							solution["ranking"] = input("\nRank this solution. ")
							with open (DECISION_FILE, 'w') as f:
								json.dump(decisions, f)
					if preferences == 'mood' :
						problem = temp_problem
						for solution in decisions[problem] :
							print("\n"+solution["solutions"])
							solution["mood"] = input("\nEnter the mood that is preferred for this solution. ")
							with open (DECISION_FILE, 'w') as f:
								json.dump(decisions, f)
			solution = input("\nDo you want to add an option for the decision? ")
			if solution.upper() == 'Y' or solution.upper() == 'YES' or solution.upper() == 'YEAH' or solution.upper() == 'YE' :
				add_solution(problem, preferences)
		result = get_choice(problem, mood, preferences)
		if result == 'nothing' :
			msg = textwrap.fill("No results were found. Please review your input. Make sure the mood exits if you set your preferences to context. Make sure you did not accidentally create a problem with no solutions.", width=100)
			print("\n"+msg)
		elif result == 'inconlusive' :
			print("\nNo single solution has been favored over the others.")
		else:
			print(result["solutions"])
			loop = input("\nDo you want to regenerate the solution? ")
			if loop.lower() != 'y' and loop.lower() != 'yes' and loop.lower() != 'ye' and loop.lower() != 'yeah' :
				problem = "exit"
	return result["solutions"]

def get_choice(input, mood, preferences):
	if preferences == 'default':
		if decisions[input] == []:
			return 'nothing'
		else:
			return random.choice(decisions[input])
	if preferences == 'num':
		solutions = [solution for solution in decisions[input] if solution["ranking"] == '1']
		if solutions == []:
			return 'nothing'
		else:
			return random.choice(solutions)
	if preferences == 'mood':
		solutions = [solution for solution in decisions[input] if solution["mood"].lower() == mood.lower()]
		if solutions == []:
			return 'nothing'
		else :
			return random.choice(solutions)
	if preferences == 'history':
		total = 0
		length = 0
		result = []
		for solution in decisions[input]:
			total = total + solution["history"]
			length += 1
		if total == 0 or length == 0 :
			return 'nothing'
		for solution in decisions[input]:
			percent = solution["history"]/total
			if percent >= 1/length:
				result.append(solution)
		if result == []:
			return 'inconclusive'
		else :
			return random.choice(result)

def main():
	global decisions
	preferences = ""
	preferences = check_preferences(preferences)
	decisions = load_data()
	msg = textwrap.fill("Enter the problem you want a decision to be made for. Enter 'exit' to stop running the program.", width=100)
	problem = input("\n"+msg+" ")
	while problem.lower() != 'exit':
		if preferences == 'mood' :
			msg = textwrap.fill("Please enter the mood that will be affecting your decision today.", width=100)
			mood = input("\n"+msg+" ")
		else :
			mood = ""
		solution = get_solutions(problem, decisions, preferences, mood.lower())
		for index in decisions[problem] :
			if index["solutions"] == solution :
				index["history"] += 1
				with open(DECISION_FILE, 'w') as f:
					json.dump(decisions, f)
		msg = textwrap.fill("Do you want to change your preferences before you enter a new problem.", width=100)
		temp_preferences = input("\n"+msg+" ")
		if temp_preferences.lower() == 'y' or temp_preferences.lower() == 'yes' or temp_preferences.lower == 'ye' or temp_preferences.lower() == 'yeah' :
			preferences = input("\nEnter your new preferences. ")
			while preferences != 'num' and preferences != 'mood' and preferences != 'history' and preferences != 'default' :
				if preferences.lower() == 'num' or preferences.lower() == 'number' or preferences.lower() == '#' or preferences.lower() == 'rank' or preferences.lower() == 'ranking':
					preferences = 'num'
				if preferences.lower() == 'mood' or preferences.lower() == 'scenario' or preferences.lower() == 'context' or preferences.lower == 'circumstance' :
					preferences = 'mood'
				if preferences.lower() == 'history' or preferences.lower() == 'previous' or preferences.lower() == 'old' :
					preferences = 'history'
				if preferences.lower() == 'default' or preferences.lower() == 'random' or preferences.lower() == 'rand' :
					preferences = 'default'
		msg = textwrap.fill("Enter the problem you want a decision to be made for. Enter 'exit' to stop running the program.", width=100)
		problem = input("\n"+msg+" ")

if __name__ == "__main__":
	app.run(debug=True)
