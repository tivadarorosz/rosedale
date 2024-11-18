import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Acuity Scheduling API credentials
ACUITY_USER_ID = os.getenv("ACUITY_USER_ID")
ACUITY_API_KEY = os.getenv("ACUITY_API_KEY")

# Define the API endpoint for appointment types
API_URL = "https://acuityscheduling.com/api/v1/appointment-types"

# Set up basic authentication
auth = (ACUITY_USER_ID, ACUITY_API_KEY)

try:
	# Make the GET request to the API
	response = requests.get(API_URL, auth=auth)
	response.raise_for_status()  # Raise an error for bad status codes

	# Parse the JSON response
	appointment_types = response.json()

	# Save the JSON data to a file
	with open("acuity_appointment_types.json", "w") as json_file:
		json.dump(appointment_types, json_file, indent=4)

	print("Appointment types have been saved to 'acuity_appointment_types.json'.")

except requests.exceptions.RequestException as e:
	print(f"An error occurred: {e}")