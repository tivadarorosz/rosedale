import os
import requests
import csv
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch environment variables
SQUARE_ACCESS_TOKEN = os.getenv("SQUARE_ACCESS_TOKEN")

# Fetch all Square customers
def fetch_square_customers():
	url = "https://connect.squareup.com/v2/customers"
	headers = {
		"Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
		"Content-Type": "application/json",
	}
	customers = []
	cursor = None

	while True:
		params = {"cursor": cursor} if cursor else {}
		response = requests.get(url, headers=headers, params=params)

		if response.status_code != 200:
			print("Error fetching customers from Square:", response.text)
			break

		data = response.json()
		customers.extend(data.get("customers", []))
		cursor = data.get("cursor")

		if not cursor:  # No more pages
			break

	return customers

# Save Square customers to a CSV file
def save_customers_to_csv(customers, filename):
	with open(filename, mode="w", newline="", encoding="utf-8") as file:
		writer = csv.writer(file)
		# Write the header
		writer.writerow(["Square ID", "Reference ID", "Customer Name", "Email"])
		
		# Write customer data
		for customer in customers:
			square_id = customer.get("id", "N/A")
			reference_id = customer.get("reference_id", "N/A")
			name = f"{customer.get('given_name', '')} {customer.get('family_name', '')}".strip()
			email = customer.get("email_address", "N/A")
			writer.writerow([square_id, reference_id, name, email])

# Main function
def main():
	try:
		print("Fetching Square customers...")
		square_customers = fetch_square_customers()
		print(f"Retrieved {len(square_customers)} Square customers.\n")

		# Save to CSV
		csv_filename = "square_customers.csv"
		save_customers_to_csv(square_customers, csv_filename)
		print(f"Square customers saved to {csv_filename}")

	except Exception as e:
		print("Error:", e)

if __name__ == "__main__":
	main()