"""
	Engine for parsing JSON and generating control flow for chatbot webhook. 

	Thoughts
	--------
	- how do we correctly store chat-user responses; do we ask the engine-user
	to define storage elements (e.g. db collections, objects)?
	
	- it makes most sense for message responses (i.e. user response to an
	emitted message from a list) to be stored in a database
		- the exception to this would be binary answers used to handle
		control flow
		- still haven't decided whether or not to store carousel responses 
	
	- we need an overarching unique identifier for a bot-user => used when 
	updating record attributes
	
	- we want keys/fields in JSON to be verbose
	
	- I'm (Sid) aiming to keep the deployed application as thin as possible
	with a minimal reliance on environment variables. Instead we hard-code said
	variables and pass their values as template strings. 


	Example JSON
	------------
	- database configuration
	{
		"collections": [
			"user",
			"transactions"
		]
	}

	- bot flow configuration
	{
		"default": {
			"type": "carousel",
			"buttons": [
				{
					"name": "log_income",
					"target": "income_amt_prompt"
				},
				{
					"name": "log_y",
					"target": <node_uid>
				}, 
				{
					"name": "help",
					"target": "help_message"
				}
			]
		},
		"onboarding": {
			"type": "message_list",
			"messages": [
				{
					"message": "Hello, welcome to ...",
					"expected_input": <input_type>,
					"storage": <collection_name.attribute>
				}, 
				{
					"message": "Please enter your age.",
					"expected_input": int,
					"storage": "user.age"
				},
				{
					"message": "Great, please enter __",
					"expected_input": int,
					"storage": <collection_name.attribute>
				}
			],
			"target": <node_uid>
		},
		"help_message": {
			"type": "message_list",
			"messages": [
				{
					"message": "Generic help message."
				}
			]
		},
		"income_amount_prompt": {
			"type": "message_list",
			"messages": [
				{
					"message": "How much did you earn today?",
					"expected_input": float,
					"storage": "transactions.amount"
				}
			]
		}
	}
"""
import json
import os

from pymongo import MongoClient


class Engine: 
	"""
		Primary engine class for parsing JSON into application logic.
	"""
	def __init__(self, user_id, page_access_token, verify_token, json_string):
		"""
			Constructor. Also handles database configuration and 
			application logic instantiation.

			Parameters
			----------
			user_id : {string}
				alphanumeric identifier for user requiring engine
			
			page_access_token : {string}
				alphanumeric token used to identify user's page; required for 
				application logic
		
			verify_token : {string}
				alphanumeric token for hub verification; required for 
				application logic		
		
			json_string : {JSON}
				data obtained from multiple sources in JSON format.
		"""
		self.json_data = json.loads(json_string)
		self.pat = page_access_token
		self.vt = verify_token

		# database config
		self.client = MongoClient(os.environ["MONGO_IP"], 
								  os.environ["MONGO_PORT"])
		self.db = self.client[user_id]

		# bot application config
		self.application_logic = base_application_logic()


	def database_config(self):
		"""
			Database configuration parser. Currently used to create
			database collections and insert placeholder records.

			Only reason we create collections is for safety during record
			insertions.
		"""
		db_config = self.json_data["database_configuration"]

		db_config.append("state")

		for coll in db_config["collections"]:
			self.db[coll].insert({"record": "placecholder"})


	def base_application_logic(self):
		"""
			Build the base for the bot's application logic. Handles app
			instantiation, verification, and basic message sending.

			For now we try our best to follow PEP8 standards.
		"""
		base_logic = """
		import os
		import json

		import requests
		from pymongo import MongoClient
		from flask import Flask

		from content import *

		app = Flask(__name__)

		# mongo constants
		client = MongoClient({mongo_ip}, {mongo_port})
		db = client[{user_id}]

		# message sending helper
		def send_message(recipient_id, message_data):
			params = {
				"access_token": {page_access_token}
			}

			headers = {
				"Content-Type": "application/json"
			}

			data = json.dumps({
				"recipient": {
					"id": recipient_id
				}, "message": message_data
			})

			r = requests.post("https://graph.facebook.com/v2.6/me/messages",
							  params=params, headers=headers, data=data)

		@app.route("/", methods=["GET"])
		def verify():
			if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
				if not request.args.get("hub.verify_token") == {verify_token}:
					return "Verificiation token mismatch", 403
				return request.args["hub.challenge"], 200

			return "Application Verified!", 200

		@app.route("/", methods=["POST"])
		{webhook_logic}

		if __name__ == "__main__":
			app.run(host="0.0.0.0", port=5000, debug=True)
		"""

		return base_logic


	def webhook_logic(self):
		"""
			Method to string together all components of the webhook logic
			(i.e. message, carousel, and quick reply handling).
		"""

		web_logic = """
		"""

		return web_logic

	def content_creation(self):
		"""
			Primary method for bot content creation (i.e. separate file).
		"""
		return True

	def process(self):
		"""
			Primary method to handle engine process. Calls member function in
			particular order. The end results are application and content files
			deployed and configured for the engine-user's facebook page.
		"""

		self.database_config()

		return True


if __name__ == '__main__':
	# create dict, convert to JSON and then parse

	test_data = {
		"page_access_token": os.environ["PAGE_ACCESS_TOKEN"],
		"database_configuration" : {
			"collections" : ["user", "transactions"]
		}
	}

	json_data = json.dumps(test_data)

	bot_engine = Engine("sunnithan95", json_data["page_access_token"], 
						json_data)

	bot_engine.process()
