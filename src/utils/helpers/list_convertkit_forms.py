import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

CONVERTKIT_API_KEY = os.getenv("CONVERTKIT_API_KEY")

def list_convertkit_forms():
	try:
		# ConvertKit API endpoint for listing forms
		url = "https://api.convertkit.com/v3/forms"

		# Create query parameters
		params = {
			"api_key": CONVERTKIT_API_KEY
		}

		# Send GET request to list forms
		response = requests.get(url, params=params)

		# Check the response status
		if response.status_code == 200:
			forms = response.json().get("forms", [])
			if forms:
				print("ConvertKit Forms:")
				for form in forms:
					print(f"Form ID: {form['id']}, Name: {form['name']}")
			else:
				print("No forms found in your ConvertKit account.")
		else:
			print(f"Failed to retrieve forms from ConvertKit. Status Code: {response.status_code}")
			print(f"Response Content: {response.text}")
			print(f"Request URL: {response.request.url}")
			print(f"Request Headers: {response.request.headers}")
			print(f"Request Body: {response.request.body}")

	except Exception as e:
		print(f"Error retrieving forms from ConvertKit: {str(e)}")

if __name__ == "__main__":
	list_convertkit_forms()