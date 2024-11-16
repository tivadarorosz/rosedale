import os
import sys
from square.client import Client
from collections import defaultdict
from datetime import datetime
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_square_client():
	"""Create and return a Square API client."""
	access_token = os.getenv('SQUARE_ACCESS_TOKEN')
	if not access_token:
		raise ValueError("Square access token not found in environment variables")
	
	return Client(
		square_version='2024-01-17',  # Using a specific version
		access_token=access_token,     # Using access_token directly
		environment='production'
	)

def get_all_orders(client, location_id):
	"""Fetch all orders from Square API using pagination."""
	orders = []
	cursor = None
	
	while True:
		try:
			result = client.orders.search_orders(
				body={
					"location_ids": [location_id],
					"cursor": cursor
				}
			)
			
			if result.is_success():
				batch_orders = result.body.get('orders', [])
				if not batch_orders:
					break
					
				orders.extend(batch_orders)
				
				# Check if there are more pages
				cursor = result.body.get('cursor')
				if not cursor:
					break
			else:
				print(f"Error fetching orders: {result.errors}")
				break
				
		except Exception as e:
			print(f"Error occurred while fetching orders: {str(e)}")
			break
	
	return orders

def analyze_line_items(orders):
	"""Analyze line items across all orders and collect unique items with their details."""
	unique_items = defaultdict(lambda: {
		'name': '',
		'variations': set(),
		'base_price_money': set(),
		'modifiers': set(),
		'total_quantity': 0,
		'order_count': 0,
		'first_seen': None,
		'last_seen': None
	})
	
	for order in orders:
		if not order.get('line_items'):
			continue
			
		order_date = datetime.fromisoformat(order['created_at'].rstrip('Z'))
		
		for item in order.get('line_items', []):
			# Debug print for the first item to see its structure
			if len(unique_items) == 0:
				print("Sample item structure:", json.dumps(item, indent=2))
			
			# Get the item name safely
			item_name = item.get('name', item.get('catalog_object_id', 'Unknown Item'))
			item_data = unique_items[item_name]
			
			# Update first and last seen dates
			if not item_data['first_seen'] or order_date < item_data['first_seen']:
				item_data['first_seen'] = order_date
			if not item_data['last_seen'] or order_date > item_data['last_seen']:
				item_data['last_seen'] = order_date
			
			# Update basic information
			item_data['name'] = item_name
			try:
				quantity = float(item.get('quantity', 1))
			except (ValueError, TypeError):
				quantity = 1
			item_data['total_quantity'] += quantity
			item_data['order_count'] += 1
			
			# Add variation if present
			variation_name = item.get('variation_name')
			if variation_name:
				item_data['variations'].add(variation_name)
			
			# Add base price
			base_price_money = item.get('base_price_money')
			if base_price_money:
				try:
					amount = int(base_price_money.get('amount', 0))/100
					currency = base_price_money.get('currency', 'USD')
					price_str = f"{amount:.2f} {currency}"
					item_data['base_price_money'].add(price_str)
				except (ValueError, TypeError, AttributeError) as e:
					print(f"Error processing base price for item {item_name}: {e}")
			
			# Add modifiers
			for modifier in item.get('modifiers', []):
				try:
					modifier_name = modifier.get('name', 'Unknown')
					modifier_str = modifier_name
					
					modifier_price = modifier.get('base_price_money')
					if modifier_price:
						amount = int(modifier_price.get('amount', 0))/100
						currency = modifier_price.get('currency', 'USD')
						modifier_str += f" (+{amount:.2f} {currency})"
					
					item_data['modifiers'].add(modifier_str)
				except (ValueError, TypeError, AttributeError) as e:
					print(f"Error processing modifier for item {item_name}: {e}")
	
	return unique_items

def print_analysis(unique_items):
	"""Print the analysis results in a formatted way."""
	print("\n=== Square Orders Line Items Analysis ===\n")
	
	if not unique_items:
		print("No items found in the orders.")
		return
	
	for item_name, data in sorted(unique_items.items()):
		try:
			print(f"Item: {item_name}")
			print(f"Total Quantity Sold: {data['total_quantity']:.2f}")
			print(f"Appeared in {data['order_count']} orders")
			if data['first_seen']:
				print(f"First Seen: {data['first_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
			if data['last_seen']:
				print(f"Last Seen: {data['last_seen'].strftime('%Y-%m-%d %H:%M:%S')}")
			
			if data['variations']:
				print("Variations:")
				for var in sorted(data['variations']):
					print(f"  - {var}")
			
			if data['base_price_money']:
				print("Base Prices:")
				for price in sorted(data['base_price_money']):
					print(f"  - {price}")
			
			if data['modifiers']:
				print("Modifiers:")
				for mod in sorted(data['modifiers']):
					print(f"  - {mod}")
			
			print("-" * 50)
		except Exception as e:
			print(f"Error printing data for {item_name}: {e}")
			continue

def main():
	try:
		# Get location ID from environment variables
		location_id = os.getenv('SQUARE_LOCATION_ID')
		if not location_id:
			raise ValueError("Square location ID not found in environment variables")
		
		# Initialize Square client
		client = create_square_client()
		
		print("Fetching orders from Square API...")
		orders = get_all_orders(client, location_id)
		print(f"Found {len(orders)} orders")
		
		print("Analyzing line items...")
		unique_items = analyze_line_items(orders)
		
		print_analysis(unique_items)
		
	except Exception as e:
		print(f"Error: {str(e)}")
		sys.exit(1)

if __name__ == "__main__":
	main()