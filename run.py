#!/usr/bin/python3

import json
import requests
import subprocess

import matplotlib.pyplot as plt
import pandas as pd

API_URL = "https://www.rescuetime.com/anapi/data"
LIMIT_ENTERTAINMENT_HOURS = 0.5

def get_entertainment_time(data):
	# looking for entertainment in raw response
	for row in data:
		if "Entertainment" in row:
			# converting seconds to hours
			return row[1]/60/60

def send_notification(threshold):
	# testing sending a desktop notification
	# icons' spec: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
	p = subprocess.call(["notify-send", "RescueTime Alert", "Ooops, you've spent more than %d for Entertainment today. Close Netflix and get your lazy ass to surf!" % threshold, "--icon=weather-severe-alert"])

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

def main():

	with open('config.json', 'r') as file:
		config = json.loads(file.read())
		token = config['API_TOKEN']

	params = {
		"key": token,
		"format": "json",
		# "perspective": "interval", # interval|rank
		"resolution_time": "minute", # minute|hour|day|week|month
		"restrict_kind": "overview" # overview|category|activity|productivity
		# if not restrict_time is provided, API returns log for the current day
		# "restrict_begin": "2018-09-29",
		# "restrict_end": "2018-09-29"
	}

	# documentation: https://www.rescuetime.com/anapi/setup/documentation#analytic-api-reference
	r = requests.get(API_URL, params=params)
	today = r.json()

	plot_time_category(today)

	if get_entertainment_time(today["rows"]) > LIMIT_ENTERTAINMENT_HOURS:
		send_notification(LIMIT_ENTERTAINMENT_HOURS)

if __name__ == "__main__":
	main()