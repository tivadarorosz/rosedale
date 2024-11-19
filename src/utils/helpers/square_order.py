import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get Square Access Token and Location ID from environment variables
SQUARE_ACCESS_TOKEN = os.getenv("SQUARE_ACCESS_TOKEN")
SQUARE_LOCATION_ID = os.getenv("SQUARE_LOCATION_ID")

# Function to search for a customer by email
def search_customer_by_email(email):
	search_customers_url = "https://connect.squareup.com/v2/customers/search"
	headers = {
		"Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
		"Content-Type": "application/json"
	}
	payload = {
		"query": {
			"filter": {
				"email_address": {
					"exact": email
				}
			}
		}
	}
	
	response = requests.post(search_customers_url, headers=headers, json=payload)
	if response.status_code == 200:
		customers = response.json().get("customers", [])
		if customers:
			return customers[0]["id"]  # Return the first customer's ID
		else:
			print("No customer found with the provided email.")
			return None
	else:
		print(f"Error searching for customer: {response.status_code} - {response.text}")
		return None

# Function to search for orders by customer ID
def search_orders_by_customer_id(customer_id):
	search_orders_url = "https://connect.squareup.com/v2/orders/search"
	headers = {
		"Authorization": f"Bearer {SQUARE_ACCESS_TOKEN}",
		"Content-Type": "application/json"
	}
	payload = {
		"location_ids": [SQUARE_LOCATION_ID],  # Include location ID here
		"query": {
			"filter": {
				"customer_filter": {
					"customer_ids": [customer_id]
				}
			}
		}
	}
	
	response = requests.post(search_orders_url, headers=headers, json=payload)
	if response.status_code == 200:
		orders = response.json().get("orders", [])
		if orders:
			return orders[0]  # Return the first order
		else:
			print("No orders found for the customer.")
			return None
	else:
		print(f"Error searching for orders: {response.status_code} - {response.text}")
		return None

# Main function
if __name__ == "__main__":
	# Replace with the email you are searching for
	email = "evelyn.tinker@hotmail.com"
	
	# Step 1: Search for customer by email
	print("Searching for customer...")
	customer_id = search_customer_by_email(email)
	
	if customer_id:
		print(f"Customer found. ID: {customer_id}")
		
		# Step 2: Search for orders by customer ID
		print("Searching for orders...")
		order = search_orders_by_customer_id(customer_id)
		
		if order:
			print("Order Details:")
			print(order)  # Print the full JSON of the order
		else:
			print("No orders found for the given customer.")
	else:
		print("Customer not found.")