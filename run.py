#!/usr/bin/python3

import json
import requests
import subprocess

import matplotlib.pyplot as plt
import pandas as pd

API_URL = "https://www.rescuetime.com/anapi/data"
LIMIT_ENTERTAINMENT_MINUTES = 0
GOAL_DEVELOPMENT_MINUTES = 180
GOAL_PRODUCTIVE_MINUTES = 300
EXPLORE=False

def send_notification(message):
	"""Sends a desktop notification on linix machines, libnotify-tools has to be installed"""
	# icons' spec: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
	p = subprocess.call(["/usr/bin/notify-send", "RescueTime Alert", message, "--icon=weather-severe-alert"])

def plot_df(data, x, y):

	data.plot.bar(x=x, y=y)
	plt.show()

def create_dataframe(data):
	"""Creates pandas.DataFrame from the response from Rescuetime API

	Creates a DataFrame and converts Time from seconds to minutes

	Args:
		data: (dict) response from RescueTime API in json

	Returns:
		pandas.DataFrame
	"""

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

def process_entertainment_time_today(token):
	"""Compares time spent on Entertainment with the limit

	Fetches data for today, finds time spent on Entertainment and displays a Desktop notification

	Args:
		token: (str) RescueTime API token

	"""

	params = {
		"key": token,
		"format": "json",
		"perspective": "rank",
		"restrict_kind": "overview"
	}

	r = requests.get(API_URL, params=params)

	today = create_dataframe(r.json())

	#plot_df(today, 'Category', 'Time')

	# loc() for finding the cell, iat() for casting DataFrame to numpy.int64
	time_spent_entertainment = today.loc[today['Category'] == 'Entertainment', ['Time']].iat[0,0]

	if time_spent_entertainment > LIMIT_ENTERTAINMENT_MINUTES:
		send_notification("Ooops, you've spent %d out of %d minutes on Entertainment today. " \
			"Close Netflix and get your lazy ass to surf!"
			% (time_spent_entertainment, LIMIT_ENTERTAINMENT_MINUTES))

def process_development_time_today(token):
	# intentionally copying pre-processing response for now to figure out the patterns
	# to improve in the future, latest version of this logic will be in process_entertainment_time_today()

	params = {
		"key": token,
		"format": "json",
		"perspective": "rank",
		"restrict_kind": "overview"
	}

	r = requests.get(API_URL, params=params)

	today = create_dataframe(r.json())

	#plot_df(today, 'Category', 'Time')

	# loc() for finding the cell, iat() for casting DataFrame to numpy.int64
	time_spent_development = today.loc[today['Category'] == 'Software Development', ['Time']].iat[0,0]

	if time_spent_development < GOAL_DEVELOPMENT_MINUTES:
		send_notification("You worked hard for %d minutes so far, your current goal is %d minutes. %d more to go!"
			% (time_spent_development, GOAL_DEVELOPMENT_MINUTES, GOAL_DEVELOPMENT_MINUTES-time_spent_development))

def process_productivity_score_today(token):
	"""Retrives time logged and productivity score"""

	params = {
		"key": token,
		"format": "json",
		"perspective": "interval",
		"resolution_time": "day",
		"restrict_kind": "efficiency"
	}

	r = requests.get(API_URL, params=params)
	today = create_dataframe(r.json())

	time_logged = today.at[0, "Time"]
	productivity_score = today.at[0, "Efficiency (percent)"]

	params['restrict_kind'] = "productivity"
	r = requests.get(API_URL, params=params)
	today = create_dataframe(r.json())

	very_productive_min = today.loc[today['Productivity'] == 2, ['Time']].iat[0,0]
	productive_min = today.loc[today['Productivity'] == 1, ['Time']].iat[0,0]

	send_notification("You are %d percent productive so far! \n%d minutes logged,\n" \
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

	with open('config.json', 'r') as file:
		config = json.loads(file.read())
		token = config['API_TOKEN']

	if EXPLORE:
		explore_data(token)
		quit()

	process_entertainment_time_today(token)
	process_development_time_today(token)
	process_productivity_score_today(token)
	#plot_productivity_today_by_hour(token)

if __name__ == "__main__":
	main()