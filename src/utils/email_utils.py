import requests
import os
import logging

logger = logging.getLogger(__name__)

def send_error_email(error_message):
	api_key = os.getenv("SENDLAYER_API_KEY")
	if not api_key:
		raise ValueError("SENDLAYER_API_KEY environment variable is not set")

	url = "https://api.sendlayer.com/v1/emails"
	data = {
		"from": "server@rosedalemassage.co.uk",
		"to": "admin@rosedalemassage.co.uk",
		"subject": "Application Error Notification",
		"text": f"An error occurred in your application:\n\n{error_message}"
	}

	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {api_key}"
	}

	try:
		response = requests.post(url, json=data, headers=headers)
		response.raise_for_status()
		logger.info("Email sent successfully")
	except requests.exceptions.RequestException as e:
		logger.error(f"Error sending email: {str(e)}")
		raise
	except Exception as e:
		logger.error(f"Unexpected error sending email: {str(e)}")
		raise