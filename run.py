#!/usr/bin/python3

# remaining features: 
# make it a service instead of on-demand/cron
# add logging
# explore data to see if any other data can be used to evaluate performance
# finish plotting of hourly productivity (+save the pic or find a way to show it)
# weekly + monthly email reports
# add documentation for project + tasks.json 

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
				utils.send_notification("Ooops you've spent %d minutes out of %d minutes limit on %s today." \
					% (time_spent, task['minutes'], task['slice_name']))
		elif task['task_type'] == 'goal':
			if time_spent < task['minutes']:
				utils.send_notification("Work harder! You have %d minutes out of %d minutes goal ahead of you to work on %s" \
					% (task['minutes'] - time_spent, task['minutes'], task['slice_name']))

def process_productivity(config, task):
	today = utils.send_request(config, perspective="interval", resolution_time="day", restrict_kind="efficiency")
	productivity_score = today.at[0, "Efficiency (percent)"]

	today = utils.send_request(config, perspective="interval", resolution_time="day", restrict_kind="productivity")
	very_productive_min = utils.extract_from_cell(today, 'Time', 'Productivity', 2) or 0
	productive_min = utils.extract_from_cell(today, 'Time', 'Productivity', 1) or 0
	time_remaining = task['minutes'] - (very_productive_min + productive_min)
	time_remaining = time_remaining if time_remaining > 0 else 0

	utils.send_notification("You are %d percent productive so far!\n" \
		"You have %d minutes out of %d minutes goal ahead of you."
		% (productivity_score, time_remaining, task['minutes']))

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