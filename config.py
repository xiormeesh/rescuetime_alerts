#!/usr/bin/python3

import json

class Config(object):

	def __init__(self):

		with open('config.json', 'r') as file:
			config = json.loads(file.read())

		self.api_url = config['API_URL']
		self.api_token = config['API_TOKEN']
		self.doExplore = config['EXPLORE']
		self.doPlot = config['PLOT']

		with open('tasks.json', 'r') as file:
			self.tasks = json.loads(file.read())