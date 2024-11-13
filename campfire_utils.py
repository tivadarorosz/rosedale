import os
import requests

# Load Campfire URLs from environment variables
CAMPFIRE_STUDIO_URL = os.getenv("CAMPFIRE_STUDIO_URL")
CAMPFIRE_FINANCE_URL = os.getenv("CAMPFIRE_FINANCE_URL")
CAMPFIRE_TECH_URL = os.getenv("CAMPFIRE_TECH_URL")

# Map channels to their URLs
CAMPFIRE_URLS = {
	"studio": CAMPFIRE_STUDIO_URL,
	"finance": CAMPFIRE_FINANCE_URL,
	"tech": CAMPFIRE_TECH_URL,
}

def send_message(channel, message):
	"""Send a message to the specified Campfire channel."""
	url = CAMPFIRE_URLS.get(channel)
	if not url:
		raise ValueError(f"Unknown channel: {channel}")

	response = requests.post(url, data=message)
	return response.status_code, response.text