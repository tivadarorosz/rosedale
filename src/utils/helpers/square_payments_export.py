import os
import json
from datetime import datetime
from square.client import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_all_payments():
	# Initialize Square client
	client = Client(
		access_token=os.getenv('SQUARE_ACCESS_TOKEN'),
		environment='production'  # Use 'sandbox' for testing
	)
	
	# Initialize payments API instance
	payments_api = client.payments
	
	# Initialize variables for pagination
	cursor = None
	all_payments = []
	
	try:
		while True:
			# Prepare the request parameters
			params = {
				'location_id': os.getenv('SQUARE_LOCATION_ID'),
				'cursor': cursor,
				'limit': 100  # Maximum allowed by Square API
			}
			
			# Make the API call
			result = payments_api.list_payments(**params)
			
			if result.is_success():
				# Extract payments from response
				payments = result.body.get('payments', [])
				
				if not payments:
					break
					
				# Add payments to our collection
				all_payments.extend(payments)
				
				# Get cursor for next page
				cursor = result.body.get('cursor')
				
				# If no cursor, we've reached the end
				if not cursor:
					break
					
			elif result.is_error():
				print(f"Error: {result.errors}")
				return None
				
	except Exception as e:
		print(f"An error occurred: {str(e)}")
		return None
	
	return all_payments

def save_payments_to_file(payments):
	# Create filename with timestamp
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	filename = f'square_payments_{timestamp}.json'
	
	try:
		with open(filename, 'w') as f:
			json.dump(payments, f, indent=2)
		print(f"Successfully saved {len(payments)} payments to {filename}")
		return filename
	except Exception as e:
		print(f"Error saving to file: {str(e)}")
		return None

def main():
	# Check for required environment variables
	if not os.getenv('SQUARE_ACCESS_TOKEN') or not os.getenv('SQUARE_LOCATION_ID'):
		print("Error: Missing required environment variables. Please check your .env file.")
		return
	
	print("Fetching payments from Square API...")
	payments = fetch_all_payments()
	
	if payments:
		print(f"Found {len(payments)} payments")
		saved_file = save_payments_to_file(payments)
		if saved_file:
			print(f"Data has been saved to {saved_file}")
	else:
		print("No payments were retrieved or an error occurred")

if __name__ == "__main__":
	main()