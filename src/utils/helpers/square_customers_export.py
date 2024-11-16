import os
import json
from datetime import datetime
from square.client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_all_customers():
	# Initialize Square client
	client = Client(
		access_token=os.getenv('SQUARE_ACCESS_TOKEN'),
		environment='production'  # Use 'sandbox' for testing
	)
	
	# Initialize customers API instance
	customers_api = client.customers
	
	# Initialize variables for pagination
	cursor = None
	all_customers = []
	
	try:
		while True:
			# Prepare the request parameters
			params = {
				'cursor': cursor,
				'limit': 100,  # Maximum allowed by Square API
				'sort_field': 'CREATED_AT',  # Sort by creation date
				'sort_order': 'ASC'  # Ascending order
			}
			
			# Make the API call
			result = customers_api.list_customers(**params)
			
			if result.is_success():
				# Extract customers from response
				customers = result.body.get('customers', [])
				
				if not customers:
					break
					
				# Add customers to our collection
				all_customers.extend(customers)
				
				# Get cursor for next page
				cursor = result.body.get('cursor')
				
				# Print progress
				print(f"Fetched {len(all_customers)} customers so far...")
				
				# If no cursor, we've reached the end
				if not cursor:
					break
					
			elif result.is_error():
				print(f"Error: {result.errors}")
				return None
				
	except Exception as e:
		print(f"An error occurred: {str(e)}")
		return None
	
	return all_customers

def save_customers_to_file(customers):
	# Create filename with timestamp
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	filename = f'square_customers_{timestamp}.json'
	
	try:
		with open(filename, 'w') as f:
			json.dump(customers, f, indent=2)
		print(f"Successfully saved {len(customers)} customers to {filename}")
		return filename
	except Exception as e:
		print(f"Error saving to file: {str(e)}")
		return None

def summarize_customer_data(customers):
	"""Prints a summary of the customer data"""
	if not customers:
		return
	
	total_customers = len(customers)
	customers_with_email = sum(1 for c in customers if c.get('email_address'))
	customers_with_phone = sum(1 for c in customers if c.get('phone_number'))
	
	print("\nCustomer Data Summary:")
	print(f"Total customers: {total_customers}")
	print(f"Customers with email: {customers_with_email} ({(customers_with_email/total_customers)*100:.1f}%)")
	print(f"Customers with phone: {customers_with_phone} ({(customers_with_phone/total_customers)*100:.1f}%)")

def main():
	# Check for required environment variables
	if not os.getenv('SQUARE_ACCESS_TOKEN'):
		print("Error: Missing SQUARE_ACCESS_TOKEN environment variable. Please check your .env file.")
		return
	
	print("Fetching customers from Square API...")
	customers = fetch_all_customers()
	
	if customers:
		print(f"\nFound {len(customers)} total customers")
		saved_file = save_customers_to_file(customers)
		if saved_file:
			print(f"Data has been saved to {saved_file}")
			summarize_customer_data(customers)
	else:
		print("No customers were retrieved or an error occurred")

if __name__ == "__main__":
	main()