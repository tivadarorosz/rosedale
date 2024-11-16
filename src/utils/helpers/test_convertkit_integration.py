import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

CONVERTKIT_API_KEY = os.getenv("CONVERTKIT_API_KEY")
CHARLOTTE_FORM_ID = os.getenv("CONVERTKIT_CHARLOTTE_FORM_ID")

def test_convertkit_integration():
	try:
		# ConvertKit API endpoint for adding a subscriber to a form
		url = f"https://api.convertkit.com/v3/forms/{CHARLOTTE_FORM_ID}/subscribe"

		# Hard-coded test data
		first_name = "Will"
		last_name = "Moss"
		email = "william.jake.moss@gmail.com"

		# Create subscriber data
		data = {
			"api_key": CONVERTKIT_API_KEY,
			"email": email,
			"first_name": first_name,
			"fields": {
				"last_name": last_name
			}
		}

		# Send POST request to add subscriber to the form
		headers = {
			"Content-Type": "application/json"
		}
		response = requests.post(url, json=data, headers=headers)

		# Check the response status
		if response.status_code == 200:
			print(f"Successfully added {email} to ConvertKit form: {CHARLOTTE_FORM_ID}")
		else:
			print(f"Failed to add {email} to ConvertKit form: {CHARLOTTE_FORM_ID}. Status Code: {response.status_code}")
			print(f"Response Content: {response.text}")
			print(f"Request URL: {response.request.url}")
			print(f"Request Headers: {response.request.headers}")
			print(f"Request Body: {response.request.body}")

	except Exception as e:
		print(f"Error adding {email} to ConvertKit: {str(e)}")

if __name__ == "__main__":
	test_convertkit_integration()