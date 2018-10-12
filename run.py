#!/usr/bin/python3

import utils

from config import Config

def explore_data(config):
	"""Sends an API request and displays + plots the data"""

	# https://www.rescuetime.com/anapi/setup/documentation#analytic-api-reference
	data = utils.send_request(config, 
		perspective="rank", # interval|rank (default)
		restrict_kind="overview", # overview|category|activity|document|efficiency|productivity
		resolution_time="day" # minute|hour|day|week|month (works only for perspective=interval)
		# if not restrict_time is provided, API returns log for the current day
		#restrict_begin='2018-09-20',
		#restrict_end='2018-09-20',
		#restrict_thing='Uncategorized'
		)

def process_category(config, task):
	today = utils.send_request(config, perspective="rank", restrict_kind="overview")
	time_spent = utils.extract_from_cell(today, 'Time', 'Category', task['slice_name'])

	if time_spent:
		if config.doPlot:
			utils.plot_df(today, 'Category', 'Time')

		# send notification
		if task['task_type'] == 'limit':
			if time_spent > task['minutes']:
				utils.send_notification("Ooops you've spent %d minutes out of %d limit on %s today." \
					% (time_spent, task['minutes'], task['slice_name']))
		elif task['task_type'] == 'goal':
			if time_spent < task['minutes']:
				utils.send_notification("Work harder! You still have %d minutes out of %d goal ahead of you to work on %s" \
					% (task['minutes'] - time_spent, task['minutes'], task['slice_name']))

def process_productivity(config, task):
	today = utils.send_request(config, perspective="interval", resolution_time="day", restrict_kind="efficiency")
	time_logged = today.at[0, "Time"]
	productivity_score = today.at[0, "Efficiency (percent)"]

	today = utils.send_request(config, perspective="interval", resolution_time="day", restrict_kind="productivity")
	very_productive_min = utils.extract_from_cell(today, 'Time', 'Productivity', 2)
	productive_min = utils.extract_from_cell(today, 'Time', 'Productivity', 1)

	# TODO: use productivity goal, should sum(productive, very_productive)
	utils.send_notification("You are %d percent productive so far! \n%d minutes logged,\n" \
		"%d minutes very productive,\n%d minutes productive."
		% (productivity_score, time_logged, very_productive_min, productive_min))

def plot_productivity_today_by_hour(token):
	"""Plots per hour: time logged and productivity score"""

	params = {
		"key": token,
		"format": "json",
		"perspective": "interval",
		"resolution_time": "hour",
		"restrict_kind": "efficiency"
	}

	r = requests.get(API_URL, params=params)
	today = create_dataframe(r.json())

	#plt.bar('Date', 'Efficiency (percent)', data=today)
	#plt.bar('Date', 'Time', data=today)
	#plt.legend(['Efficiency', 'Logged time'], loc='upper left')
	#plt.show()

	fig, ax = plt.subplots()

	efficiency = ax.bar('Date', 'Efficiency (percent)', data=today, label="Efficiency")
	time = ax.bar('Date', 'Time', data=today, label="Time Logged")
	ax.legend()

	plt.show()

	#TODO: pre-process date properly + scale both bars as percentage (or group both graphs)

def main():

	config = Config()

	if config.doExplore:
		explore_data(config)
		quit()

	for task in config.tasks:
		if task["task_type"] in ["goal", "limit"]:
			process_category(config, task)

		elif task['task_type'] == 'productivity':
			process_productivity(config, task)

	if config.doPlot:
		plot_productivity_today_by_hour(config)

if __name__ == "__main__":
	main()