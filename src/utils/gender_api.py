import os
import requests
import logging
from src.core.monitoring import handle_error

logger = logging.getLogger(__name__)

def get_gender(first_name):
	try:
		api_key = os.getenv("GENDER_API_KEY")
		if not api_key:
			raise ValueError("GENDER_API_KEY environment variable is not set")

		url = f"https://gender-api.com/get?name={first_name}&key={api_key}"
		response = requests.get(url)
		response.raise_for_status()
		gender_data = response.json()
		gender = gender_data["gender"]
		return gender
	except requests.exceptions.RequestException as e:
		logger.error(f"Error getting gender from API: {str(e)}")
		handle_error(e, f"Gender API error for name: {first_name}")
		return "unknown"
	except Exception as e:
		logger.error(f"Unexpected error getting gender from API: {str(e)}")
		handle_error(e, f"Unexpected gender API error for name: {first_name}")
		return "unknown"