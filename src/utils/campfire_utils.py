import os
import requests
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# Map channels to their URLs directly from environment variables
CAMPFIRE_URLS = {
	"studio": os.getenv("CAMPFIRE_STUDIO_URL"),
	"finance": os.getenv("CAMPFIRE_FINANCE_URL"),
	"tech": os.getenv("CAMPFIRE_TECH_URL"),
	"alert": os.getenv("CAMPFIRE_ALERT_URL"),
}

def send_message(channel, message):
	try:
		"""Send a message to the specified Campfire channel."""
		logger.debug(f"Received channel name: {channel}")
		logger.debug(f"CAMPFIRE_URLS dictionary: {CAMPFIRE_URLS}")
		url = CAMPFIRE_URLS.get(channel)
		logger.debug(f"This is the url: {url}")
		
		if not url:
			raise ValueError(f"Unknown channel: {channel}. Available channels: {list(CAMPFIRE_URLS.keys())}")
		
		headers = {
			"Content-Type": "text/html",
		}
		
		# Encode the message in UTF-8
		encoded_message = message.encode("utf-8")
		
		logger.info(f"Sending message to {channel} ({url}): {message}")
		response = requests.post(url, data=encoded_message, headers=headers)
		
		logger.debug(f"Response Status Code: {response.status_code}")
		logger.debug(f"Response Text: {response.text or '<empty>'}")
		
		# Treat 2xx status codes as success
		if 200 <= response.status_code < 300:
			return response.status_code, response.text or "Message sent successfully"
		
		# Handle non-2xx responses as errors
		raise Exception(f"Campfire error: HTTP {response.status_code}, Body: {response.text or '<no response body>'}")
	except requests.exceptions.RequestException as e:
		logger.error(f"Error sending message to Campfire: {str(e)}")
		raise
	except Exception as e:
		logger.error(f"Unexpected error sending message to Campfire: {str(e)}")
		raise