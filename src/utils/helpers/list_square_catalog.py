import os
import csv
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Fetch Square access token
SQUARE_ACCESS_TOKEN = os.getenv("SQUARE_ACCESS_TOKEN")

def list_square_catalog():
	"""Fetch all Square catalog objects."""
	url = "https://connect.squareup.com/v2/catalog/list"
	headers = {
		"Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
		"Content-Type": "application/json",
	}

	# Send the request
	response = requests.get(url, headers=headers)
	if response.status_code != 200:
		raise Exception(f"Error fetching Square catalog: {response.text}")

	# Parse response JSON
	data = response.json()
	return data.get("objects", [])

def save_catalog_to_csv(catalog_objects, output_file="square_catalog.csv"):
	"""Save catalog objects to a CSV file."""
	if not catalog_objects:
		print("No catalog objects found.")
		return

	# Extract all unique keys for the CSV header
	keys = set()
	for obj in catalog_objects:
		keys.update(obj.keys())

	# Write the catalog objects to CSV
	with open(output_file, mode="w", newline="", encoding="utf-8") as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=list(keys))
		writer.writeheader()

		for obj in catalog_objects:
			writer.writerow(obj)

	print(f"Catalog objects saved to {output_file}")

def main():
	try:
		print("Fetching catalog objects from Square...")
		catalog_objects = list_square_catalog()
		print(f"Fetched {len(catalog_objects)} catalog objects.")

		print("Saving catalog objects to CSV...")
		save_catalog_to_csv(catalog_objects)
	except Exception as e:
		print(f"Error: {e}")

if __name__ == "__main__":
	main()