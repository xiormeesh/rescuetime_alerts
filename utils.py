#!/usr/bin/python3

import json
import requests
import subprocess

import matplotlib.pyplot as plt
import pandas as pd

def send_notification(message):
	"""Sends a desktop notification on linix machines, libnotify-tools has to be installed"""
	# icons' spec: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
	p = subprocess.call(['/usr/bin/notify-send', "RescueTime Alert", message, '--icon=weather-severe-alert'])

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

def send_request(config, **additional_params):
	"""Sends request to rescuetime and preprocesses the respons

	Sends a request to RescueTime API, converts the response to a DataFrame,
	converts seconds to minutes in Time column

	Args:
		config: (Config object)
		params: (dict) params to be passed to RescueTime

	Returns:
		pandas.DataFrame
	"""

	params = {
		'key': config.api_token,
		'format': 'json'
		}

	params.update(additional_params)

	r = requests.get(config.api_url, params=params)
	data = r.json()

	df = pd.DataFrame(data['rows'], columns=data['row_headers'])
	df.rename(columns={'Time Spent (seconds)': 'Time'}, inplace=True)
	df['Time'] = df['Time'].apply(lambda x: int(x/60))
	print(df)

	return df