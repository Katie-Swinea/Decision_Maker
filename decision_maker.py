import json
import os
import random

DECISION_FILE = 'decisions.json'
PREFERENCES_FILE = 'preferences.json'

def load_data(file):
	if os.path.exists(file):
		with open(file, 'r') as f:
			data = json.load(f)
			if isinstance(list, dict):
				return list

	return {}

def check_preferences():
	preferences = load_data(PREFERENCES_FILE)
	if preferences == [] or 'default' :
		settings = input("Would you like to input your preferences by choosing a ranking system for the options you enter? ")
		if settings == 'y' or settings == 'Y' or settings == 'yes' or settings == 'Yes' or settings == 'yeah' or settings == 'Yeah' or settings == 'ye' or settings == 'Ye' :
			while preferences != 'num' and preferences != 'mood' and preferences != 'history' :
				rank = input("Choose your rank based on numbers, scenario, or previous choices? ")
				if rank == 'num' or rank == 'number' or rank == 'n' or rank == '#' :
					preferences == 'num'
				if rank == 'mood' or rank == 'scene' or rank == 'scenario' or rank == 'circumstance' or rank == 's' :
					preferences == 'mood'
				if rank == 'previous' or rank == 'previous choice' or rank == 'previous choices' or rank == 'choice' or rank == 'choices' or rank == 'history' or rank == 'p' or rank == 'pc' :
					preferences == 'history'
			if preferences == 'mood' :
				moods = []
				mood = input("Enter the different scenarios that will affect the decision. Enter 'done' when finished. ")
				while mood != 'done' :
					moods.append(mood)
					mood = input("Enter the different scenarios that will affect the decision. Enter 'done' when finished. ")
		else :
			preferences = 'default'
	with open (PREFERENCES_FILE, 'w') as f:
		json.dump(preferences, f)

def add_problem(input):
	if input not in decisions:
		decisions[input] = []
		with open(DECISION_FILE, 'w') as f:
			json.dump(decisions, f)

def add_solution(inPut):
	if inPut in decisions :
		solution = input("Enter an option for the problem. Enter 'stop' when you are finished. ")
		if preferences == 'default' or preferences == [] :
			while solution != 'stop' :
				if solution not in decisions[inPut]:
					decisions[inPut].append(solution)
				with open(DECISION_FILE, 'w') as f:
					json.dump(decisions, f)
				solution = input("Enter an option for the problem. Enter 'stop' when you are finished. ")
		if preferences == 'num' :
			rank = input("Enter a ranking for that option. Remember more than one option can have the same ranking. ")
			while solution != 'stop' :
				if solution not in decisions[input]:
					decisions[inPut].append({"solutions": solution, "ranking": rank})
				with open(DECISION_FILE, 'w') as f:
					json.dump(decisions, f)
				solution = input("Enter an option for the problem. Enter 'stop' when you are finished. ")

def get_choice(input):
	return random.choice(decisions[input])

def main():
	global decisions
	global preferences
	decisions = load_data(DECISION_FILE)
	check_preferences()
	problem = input("Enter the problem you want a decision to be made for. Enter 'exit' to stop running the program. ")
	while problem != 'exit' :
		if problem not in decisions:
			add_problem(problem)
		if decisions[problem] == []:
			add_solution(problem)
		else :
			solution = input("Do you want to add options for the decision? ")
			if solution == 'y' or solution == 'Y' or solution == 'yes' or solution == 'Yes' or solution == 'yeah' or solution == 'Yeah' or solution == 'ye' or solution == 'Ye' :
				add_solution(problem)
		result = get_choice(problem)
		print(result)
		problem = input("Enter the problem you want a decision to be made for. Enter 'exit to stop. ")

if __name__ == "__main__":
	main()
