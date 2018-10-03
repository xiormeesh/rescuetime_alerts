#!/usr/bin/python3

import json
import requests
import subprocess

import matplotlib.pyplot as plt
import pandas as pd

API_URL = "https://www.rescuetime.com/anapi/data"
LIMIT_ENTERTAINMENT_MINUTES = 0
EXPLORE=False

def send_notification(current_value, threshold):
	"""Sends a desktop notification on linix machines, libnotify-tools has to be installed"""
	# icons' spec: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
	p = subprocess.call(["notify-send", "RescueTime Alert", "Ooops, you've spent %d minutes on Entertainment today. Close Netflix and get your lazy ass to surf!" % current_value, "--icon=weather-severe-alert"])

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

	plot_df(today, 'Category', 'Time')

	# loc() for finding the cell, iat() for casting DataFrame to numpy.int64
	time_spent_entertainment = today.loc[today['Category'] == 'Entertainment', ['Time']].iat[0,0]

	if time_spent_entertainment > LIMIT_ENTERTAINMENT_MINUTES:
		send_notification(time_spent_entertainment, LIMIT_ENTERTAINMENT_MINUTES)

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