import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
SQUARE_ACCESS_TOKEN = os.getenv("SQUARE_ACCESS_TOKEN")

# Square API Endpoint
SEARCH_CATALOG_ITEMS_URL = "https://connect.squareup.com/v2/catalog/search-catalog-items"

# Function to search all catalog items
def search_catalog_items():
	headers = {
		"Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
		"Content-Type": "application/json",
	}

	# Request payload
	payload = {
		"limit": 100,  # Adjust the limit if you expect more results per request
	}

	all_items = []
	cursor = None

	while True:
		if cursor:
			payload["cursor"] = cursor

		response = requests.post(SEARCH_CATALOG_ITEMS_URL, headers=headers, json=payload)

		if response.status_code != 200:
			print("Error fetching catalog items:", response.text)
			break

		data = response.json()

		# Append fetched items to the list
		all_items.extend(data.get("items", []))

		# Check if there is a next page
		cursor = data.get("cursor")
		if not cursor:
			break

	return all_items

# Main function
def main():
	try:
		print("Fetching Square catalog items...")
		items = search_catalog_items()
		print(f"Retrieved {len(items)} items from the Square catalog.")

		# Save to JSON file
		output_file = "square_catalog_items.json"
		with open(output_file, "w") as f:
			json.dump(items, f, indent=4)
		print(f"Catalog items saved to {output_file}")

	except Exception as e:
		print("Error:", e)

if __name__ == "__main__":
	main()