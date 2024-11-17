import os
import requests
from dotenv import load_dotenv
from src.utils.email_utils import send_error_email

load_dotenv()

# Map channels to their URLs directly from environment variables
CAMPFIRE_URLS = {
	"studio": os.getenv("CAMPFIRE_STUDIO_URL"),
	"finance": os.getenv("CAMPFIRE_FINANCE_URL"),
	"tech": os.getenv("CAMPFIRE_TECH_URL"),
}

def send_message(channel, message):
	try:
		"""Send a message to the specified Campfire channel."""
		print("Received channel name: ", channel)
		print("CAMPFIRE_URLS dictionary:", CAMPFIRE_URLS)
		url = CAMPFIRE_URLS.get(channel)
		print("This is the url: ", url)
		if not url:
			raise ValueError(f"Unknown channel: {channel}. Available channels: {list(CAMPFIRE_URLS.keys())}")
		
		headers = {
			"Content-Type": "text/html",  # Explicitly set the content type
		}
		
		# Encode the message in UTF-8
		encoded_message = message.encode("utf-8")
		
		print(f"Sending message to {channel} ({url}): {message}")
		response = requests.post(url, data=encoded_message, headers=headers)  # Send encoded data
		
		print(f"Response Status Code: {response.status_code}")
		print(f"Response Text: {response.text or '<empty>'}")
		
		# Treat 2xx status codes as success
		if 200 <= response.status_code < 300:
			return response.status_code, response.text or "Message sent successfully"
		
		# Handle non-2xx responses as errors
		raise Exception(f"Campfire error: HTTP {response.status_code}, Body: {response.text or '<no response body>'}")
	except requests.exceptions.RequestException as e:
		logger.error(f"Error sending message to Campfire: {str(e)}")
		send_error_email(str(e))
		raise
	except Exception as e:
		logger.error(f"Unexpected error sending message to Campfire: {str(e)}")
		send_error_email(str(e))
		raise