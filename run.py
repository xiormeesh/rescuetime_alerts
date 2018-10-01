#!/usr/bin/python3

import json
import requests
import subprocess

import matplotlib.pyplot as plt
import pandas as pd

API_URL = "https://www.rescuetime.com/anapi/data"
LIMIT_ENTERTAINMENT_HOURS = 0
EXPLORE=False

def send_notification(threshold, current_value):
	# testing sending a desktop notification
	# icons' spec: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
	p = subprocess.call(["notify-send", "RescueTime Alert", "Ooops, you've spent %d minutes on Entertainment today. Close Netflix and get your lazy ass to surf!" % current_value, "--icon=weather-severe-alert"])

def plot_time_category(data):
	# testing some visualizations
	df = pd.DataFrame(data['rows'], columns=data['row_headers'])
	cleaned = df.drop(columns=["Rank", "Number of People"])
	cleaned.columns = ["Time", "Category"]
	# converting to minutes for better readability
	cleaned["Time"] = cleaned["Time"].apply(lambda x: int(x/60))
	print(cleaned)
	cleaned.plot.bar(x="Category", y="Time")
	plt.show()

def explore_data(token):
	params = {
		"key": token,
		"format": "json",
		"perspective": "interval", # interval|rank (default)
		"resolution_time": "week", # minute|hour|day|week|month (works only for perspective=interval)
		"restrict_kind": "category", # overview|category|activity|document|efficiency|productivity
		# if not restrict_time is provided, API returns log for the current day
		"restrict_begin": "2018-09-20",
		# "restrict_end": "2018-09-29",
		"restrict_thing": "Uncategorized"
	}

	r = requests.get(API_URL, params=params)
	data = r.json()
	print(data)
	df = pd.DataFrame(data['rows'], columns=data['row_headers'])
	print(df)

def process_entertainment_time_today(token):
	# looking for entertainment in raw response

	params = {
		"key": token,
		"format": "json",
		"perspective": "rank",
		"restrict_kind": "overview"
	}

	r = requests.get(API_URL, params=params)
	today = r.json()

	plot_time_category(today)

	for row in today['rows']:
		if "Entertainment" in row:
			# converting seconds to hours
			current_value_hours = row[1]/60/60
			if current_value_hours > LIMIT_ENTERTAINMENT_HOURS:
				send_notification(LIMIT_ENTERTAINMENT_HOURS, current_value_hours*60)

def main():

	with open('config.json', 'r') as file:
		config = json.loads(file.read())
		token = config['API_TOKEN']

	if EXPLORE:
		explore_data(token)
		quit()

	process_entertainment_time_today(token)

if __name__ == "__main__":
	main()