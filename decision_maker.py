import json
import os
import random

DECISION_FILE = 'decisions.json'

def load_data():
	if os.path.exists(DECISION_FILE):
		with open(DECISION_FILE, 'r') as f:
			list = json.load(f)
			if isinstance(list, dict):
				return list

	return {}

def check_preferences():
	preferences = ""
	while preferences != 'num' and preferences != 'history' and preferences != 'mood' and preferences != 'default' :
		settings = input("Please choose if you want your choice to be made at random, based on a number ranking system, based on the context surrounding the choice or based on the history of your old choices. ")
		if settings.lower() == 'num' or settings.lower() == 'number' or settings.lower() == 'n' or settings.lower() == '#' or preferences.lower() == 'rank' or preferences.lower() == 'ranking' or preferences.lower() == 'system' :
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

def add_solution(inPut):
	if inPut in decisions :
		solution = input("Enter an option for the problem. Enter 'stop' when you are finished. ")
		if preferences == 'default' :
			while solution.lower() != 'stop' :
				if solution not in decisions[inPut]:
					decisions[inPut].append({"solutions": solution, "ranking": [], "mood": [], "history": '0'})
				with open(DECISION_FILE, 'w') as f:
					json.dump(decisions, f)
				solution = input("Enter an option for the problem. Enter 'stop' when you are finished. ")
		if preferences == 'num' :
			while solution.lower() != 'stop' :
				rank = input("Enter a ranking for that option. Remember more than one option can have the same ranking. ")
				if solutions not in decisions[inPut]:
					decisions[inPut].append({"solutions": solution, "ranking": rank, "mood": [], "history": '0'})
				with open(DECISION_FILE, 'w') as f:
					json.dump(decisions, f)
				solution = input("Enter an option for the problem. Enter 'stop' when you are finished. ")
		if preferences == 'mood' :
			while solution.lower() != 'stop' :
				mood = input("Enter a mood corresponding to this option. More than one option can have the same mood. ")
				if solution not in decisions[inPut]:
					decisions[inPut].append({"solutions": solution, "ranking": [], "mood": mood, "history": '0'})
				with open(DECISION_FILE, 'w') as f:
					json.dump(decisions, f)
				solution = input("Enter an option for the problem. Enter 'stop' when you are finished. ")
def get_solution(problem, decisions):
	while problem.lower() != 'exit' :
		if problem not in decisions:
                        add_problem(problem)
                if decisions[problem] == []:
                        add_solution(problem)
                else :
                        while (preferences == 'num' and decisions[problem][1]["ranking"] == []) or (preferences == 'mood' and decisions[problem][0]["mood"] == []):
                                temp_problem = problem
                                problem = input("Enter a problem that matches the preferences you have set for this session. To change your prefernces, enter 'cp' so the preferences match the problem. To add t>
                                if problem.upper() == 'CP' or problem.lower() == 'change' or problem.lower() == 'preferences' or problem.lower() == 'change preferences' :
                                        problem = temp_problem
                                        preferences = input("To do a number ranking, enter 'num', to do a circumstance ranking, enter 'circum', to do a choice based on your history, enter 'history', and to do >
                                        if preferences.lower() == 'circum' or preferences.lower() == 'circ' or preferences.lower() == 'circumstance' or preferences.lower() == 'circumstances':
                                                preferences = 'mood'
                                        if preferences.lower() == 'random' or preferences.lower() == 'rand' or preferences.lower() == 'r' :
                                                preferences = 'default'
                                        while preferences != 'num' and preferences != 'mood' and preferences != 'history' and preferences != 'default' :
                                                preferences = input("To do a number ranking, enter 'num', to do circumstance based ranking, enter 'circum', to do a choice based on your history, enter 'history'>
                                if problem.upper() == 'AP' or problem.lower() == 'add problem' or problem.lower() == 'add to problem' or problem.lower() == 'add' or problem.lower() == 'problem' :
                                        if preferences == 'num' :
                                                problem = temp_problem
                                                for solution in decisions[problem] :
                                                        print(solution["solutions"])
                                                        solution["ranking"] = input("Rank this solution. ")
                                                        with open (DECISION_FILE, 'w') as f:
                                                                json.dump(decisions, f)
                                        if preferences == 'mood' :
                                                problem = temp_problem
                                                for solution in decisions[problem] :
                                                        print(solution["solutions"])
                                                        solution["mood"] = input("Enter the mood that is preferred for this solution. ")
                                                        with open (DECISION_FILE, 'w') as f:
                                                                json.dump(decisions, f)

                        solution = input("Do you want to add options for the decision? ")
                        if solution.upper() == 'Y' or solution.upper() == 'YES' or solution.upper() == 'YEAH' or solution.upper() == 'YE' :
                                add_solution(problem)

                result = get_choice(problem, mood)
                if result == 'nothing' :
                        print("No results were found. Please review your input. Make sure the mood exists if you set your preferences to context. Make sure you did not accidentally create a blank solution.")
                else:
                        print(result["solutions"])
                        loop = input("Do you want to regenerate the solution?")
                        if loop.lower() != 'y' and loop.lower() != 'yes' and loop.lower() != 'ye' and loop.lower() != 'yeah' :
                                problem = "exit"
	return result["solutions"]

def get_choice(input, mood):
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
		solutions = [solution for solution in decisions[input] if solution["mood"] == mood]
		if solutions == []:
			return 'nothing'
		else :
			return random.choice(solutions)

def main():
	global decisions
	global preferences
	preferences = check_preferences()
	if preferences == 'mood' :
		mood = input("Please enter the mood that will be affecting your decision today. ")
	else :
		mood = ""
	decisions = load_data()
	problem = input("Enter the problem you want a decision to be made for. Enter 'exit' to stop running the program. ")
	while problem.lower() != 'exit' :
		solution = get_solution(problem, decisions)
		temp = int(decisions[problem][solution]["history"])
		temp += 1
		decisions[problem][solution]["history"] = str(temp)
		with open (DECISION_FILE, 'w') as f:
			json.dump(decisions, f)
		problem = input("Enter the problem you want a decision to be made for. Enter 'exit' to stop. ")

if __name__ == "__main__":
	main()
