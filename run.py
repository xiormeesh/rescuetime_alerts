#!/usr/bin/python3

import json
import requests
import subprocess

import matplotlib.pyplot as plt
import pandas as pd

API_URL = "https://www.rescuetime.com/anapi/data"

def send_notification(message):
	"""Sends a desktop notification on linix machines, libnotify-tools has to be installed"""
	# icons' spec: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
	p = subprocess.call(["/usr/bin/notify-send", "RescueTime Alert", message, "--icon=weather-severe-alert"])

def plot_df(data, x, y):

	data.plot.bar(x=x, y=y)
	plt.show()

def extract_from_cell(df, what, where, where_value):
	"""Extracts a single value from a Dataframe

	Extracts a single value from a dataframe, if value cannot be found returns None
	Works similar to SQL's "select WHAT from WHERE where WHERE_VALUE"
	Current assumption is that only 1 cell will be found

	Args:
		df: (pandas.DataFrame)
		what: (str) name of the target column
		where: (str) name of the conditional column
		where_value: (str|int) filter row value 

	Returns: 
		cell's value or None if not found
	"""
	try:
		cell = df.loc[df[where] == where_value, [what]].iat[0,0]
	except IndexError:
		cell = None

	return cell

def send_request(params):
	"""Sends request to rescuetime and preprocesses the respons

	Sends a request to RescueTime API, converts the response to a DataFrame,
	converts seconds to minutes in Time column

	Args:
		params: (dict) params to be passed to RescueTime

	Returns:
		pandas.DataFrame
	"""
	r = requests.get(API_URL, params=params)
	data = r.json()

	df = pd.DataFrame(data['rows'], columns=data['row_headers'])
	df.rename(columns={"Time Spent (seconds)": "Time"}, inplace=True)
	df["Time"] = df["Time"].apply(lambda x: int(x/60))
	print(df)

	return df

def explore_data(token):
	"""Sends an API request and displays + plots the data"""

	# https://www.rescuetime.com/anapi/setup/documentation#analytic-api-reference
	params = {
		"key": token,
		"format": "json",
		"perspective": "interval", # interval|rank (default)
		"resolution_time": "day", # minute|hour|day|week|month (works only for perspective=interval)
		"restrict_kind": "productivity", # overview|category|activity|document|efficiency|productivity
		# if not restrict_time is provided, API returns log for the current day
		#"restrict_begin": "2018-09-20",
		# "restrict_end": "2018-09-29",
		#"restrict_thing": "Uncategorized"
	}

	r = requests.get(API_URL, params=params)
	today = create_dataframe(r.json())

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

	with open('config.json', 'r') as file:
		config = json.loads(file.read())

		token = config['API_TOKEN']
		doExplore = config['EXPLORE']
		doPlot = config['PLOT']

	if doExplore:
		explore_data(token)
		quit()

	with open('tasks.json', 'r') as file:
		tasks = json.loads(file.read())

	for task in tasks:

		params = {
			"key": token,
			"format": "json"
		}

		if task["task_type"] in ["goal", "limit"]:

			params["perspective"] = "rank"
			params["restrict_kind"] = "overview"

			today = send_request(params)

			time_spent = extract_from_cell(today, 'Time', 'Category', task['slice_name'])

			if time_spent:

				if doPlot:
					plot_df(today, 'Category', 'Time')

				# send notification
				if task['task_type'] == 'limit':
					if time_spent > task['minutes']:
						send_notification("Ooops you've spent %d minutes out of %d limit on %s today." \
							% (time_spent, task['minutes'], task['slice_name']))
				elif task['task_type'] == 'goal':
					if time_spent < task['minutes']:
						send_notification("Work harder! You still have %d minutes out of %d goal ahead of you to work on %s" \
							% (task['minutes'] - time_spent, task['minutes'], task['slice_name']))

		elif task['task_type'] == 'productivity':
			params['perspective'] = 'interval'
			params['resolution_time'] = 'day'

			params['restrict_kind'] = 'efficiency'
			today = send_request(params)
			time_logged = today.at[0, "Time"]
			productivity_score = today.at[0, "Efficiency (percent)"]

			params['restrict_kind'] = "productivity"
			today = send_request(params)

			very_productive_min = extract_from_cell(today, 'Time', 'Productivity', 2)
			productive_min = extract_from_cell(today, 'Time', 'Productivity', 1)

			send_notification("You are %d percent productive so far! \n%d minutes logged,\n" \
				"%d minutes very productive,\n%d minutes productive."
				% (productivity_score, time_logged, very_productive_min, productive_min))


	# plot_productivity_today_by_hour(token)

if __name__ == "__main__":
	main()