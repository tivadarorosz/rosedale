import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Acuity Scheduling API credentials
ACUITY_USER_ID = os.getenv("ACUITY_USER_ID")
ACUITY_API_KEY = os.getenv("ACUITY_API_KEY")

# Define the API endpoint for retrieving orders
API_URL = "https://acuityscheduling.com/api/v1/orders"

# Set up basic authentication
auth = (ACUITY_USER_ID, ACUITY_API_KEY)

try:
	# Make the GET request to the API
	response = requests.get(API_URL, auth=auth)
	response.raise_for_status()  # Raise an error for bad status codes

	# Parse the JSON response
	orders = response.json()

	# Save the JSON data to a file
	with open("acuity_orders.json", "w") as json_file:
		json.dump(orders, json_file, indent=4)

	print("Orders have been saved to 'acuity_orders.json'.")

except requests.exceptions.RequestException as e:
	print(f"An error occurred: {e}")