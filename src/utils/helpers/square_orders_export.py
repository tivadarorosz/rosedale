import os
import json
from datetime import datetime
from square.client import Client
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def fetch_order_details(client, order_id):
	"""Fetch detailed information for a specific order"""
	try:
		result = client.orders.retrieve_order(order_id=order_id)
		if result.is_success():
			return result.body.get('order')
		else:
			print(f"Error fetching order {order_id}: {result.errors}")
			return None
	except Exception as e:
		print(f"Error fetching order {order_id}: {str(e)}")
		return None

def fetch_all_orders():
	# Initialize Square client
	client = Client(
		access_token=os.getenv('SQUARE_ACCESS_TOKEN'),
		environment='production'  # Use 'sandbox' for testing
	)
	
	# Initialize variables for pagination
	cursor = None
	all_orders = []
	
	try:
		while True:
			# Prepare the search request body
			body = {
				'location_ids': [os.getenv('SQUARE_LOCATION_ID')],
				'limit': 100,  # Reasonable batch size
			}
			
			if cursor:
				body['cursor'] = cursor
			
			# Search for orders
			result = client.orders.search_orders(body=body)
			
			if result.is_success():
				# Extract order IDs from search results
				orders = result.body.get('orders', [])
				
				if not orders:
					break
				
				print(f"Found {len(orders)} orders in current batch...")
				
				# Fetch detailed information for each order
				for order in orders:
					order_id = order.get('id')
					if order_id:
						print(f"Fetching details for order {order_id}")
						detailed_order = fetch_order_details(client, order_id)
						if detailed_order:
							all_orders.append(detailed_order)
							# Add a small delay to avoid rate limiting
							time.sleep(0.1)
				
				# Get cursor for next page
				cursor = result.body.get('cursor')
				
				# If no cursor, we've reached the end
				if not cursor:
					break
					
			elif result.is_error():
				print(f"Error in search: {result.errors}")
				return None
				
	except Exception as e:
		print(f"An error occurred: {str(e)}")
		return None
	
	return all_orders

def save_orders_to_file(orders):
	# Create filename with timestamp
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	filename = f'square_orders_{timestamp}.json'
	
	try:
		with open(filename, 'w') as f:
			json.dump(orders, f, indent=2)
		print(f"Successfully saved {len(orders)} orders to {filename}")
		return filename
	except Exception as e:
		print(f"Error saving to file: {str(e)}")
		return None

def summarize_order_data(orders):
	"""Prints a summary of the order data"""
	if not orders:
		return
	
	total_orders = len(orders)
	total_amount = 0
	states = {}
	fulfillment_types = {}
	
	for order in orders:
		# Count order states
		state = order.get('state', 'UNKNOWN')
		states[state] = states.get(state, 0) + 1
		
		# Sum total amounts if available
		total_money = order.get('total_money', {})
		if total_money and 'amount' in total_money:
			total_amount += total_money['amount']
		
		# Count fulfillment types
		fulfillments = order.get('fulfillments', [])
		for fulfillment in fulfillments:
			f_type = fulfillment.get('type', 'UNKNOWN')
			fulfillment_types[f_type] = fulfillment_types.get(f_type, 0) + 1
	
	print("\nOrder Data Summary:")
	print(f"Total orders: {total_orders}")
	if total_amount > 0:
		print(f"Total amount: ${total_amount/100:,.2f}")  # Convert cents to dollars
	
	if states:
		print("\nOrder States:")
		for state, count in states.items():
			percentage = (count/total_orders)*100
			print(f"{state}: {count} ({percentage:.1f}%)")
	
	if fulfillment_types:
		print("\nFulfillment Types:")
		for f_type, count in fulfillment_types.items():
			percentage = (count/total_orders)*100
			print(f"{f_type}: {count} ({percentage:.1f}%)")

def main():
	# Check for required environment variables
	if not os.getenv('SQUARE_ACCESS_TOKEN') or not os.getenv('SQUARE_LOCATION_ID'):
		print("Error: Missing required environment variables. Please check your .env file.")
		return
	
	print("Fetching orders from Square API...")
	orders = fetch_all_orders()
	
	if orders:
		print(f"\nFound {len(orders)} total orders")
		saved_file = save_orders_to_file(orders)
		if saved_file:
			print(f"Data has been saved to {saved_file}")
			summarize_order_data(orders)
	else:
		print("No orders were retrieved or an error occurred")

if __name__ == "__main__":
	main()