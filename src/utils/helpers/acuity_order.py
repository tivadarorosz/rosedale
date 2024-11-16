import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv
import json
from base64 import b64encode

# Load environment variables
load_dotenv()

class AcuityClient:
	BASE_URL = "https://acuityscheduling.com/api/v1"
	
	def __init__(self):
		self.user_id = os.getenv('ACUITY_USER_ID')
		self.api_key = os.getenv('ACUITY_API_KEY')
		
		if not self.user_id or not self.api_key:
			raise ValueError("Acuity credentials not found in environment variables")
		
		# Create basic auth header
		credentials = f"{self.user_id}:{self.api_key}"
		encoded_credentials = b64encode(credentials.encode('utf-8')).decode('utf-8')
		self.headers = {
			'Authorization': f'Basic {encoded_credentials}',
			'Content-Type': 'application/json'
		}
	
	def get_orders(self, limit=100):
		"""
		Fetch all orders from Acuity Scheduling.
		:param limit: Number of orders to fetch per request
		:return: List of orders
		"""
		all_orders = []
		offset = 0
		
		while True:
			try:
				response = requests.get(
					f"{self.BASE_URL}/orders",
					headers=self.headers,
					params={
						'limit': limit,
						'offset': offset
					}
				)
				
				response.raise_for_status()
				orders = response.json()
				
				if not orders:  # No more orders
					break
				
				all_orders.extend(orders)
				print(f"Fetched {len(orders)} orders (offset: {offset})")
				
				if len(orders) < limit:  # Last page
					break
				
				offset += limit
				
			except requests.exceptions.RequestException as e:
				print(f"Error fetching orders at offset {offset}: {str(e)}")
				break
		
		return all_orders

def format_datetime(dt_str):
	"""Format datetime string for display"""
	if not dt_str:
		return "N/A"
	try:
		dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
		return dt.strftime('%Y-%m-%d %H:%M:%S %Z')
	except (ValueError, AttributeError):
		return dt_str

def format_money(amount):
	"""Format money amount for display"""
	if amount is None:
		return "N/A"
	try:
		return f"${float(amount):.2f}"
	except (ValueError, TypeError):
		return str(amount)

def print_order_details(order):
	"""Print detailed information about an order"""
	print("\n" + "="*80)
	print(f"Order ID: {order.get('id', 'N/A')}")
	print(f"Transaction ID: {order.get('transactionID', 'N/A')}")
	print("-"*80)
	
	# Basic Information
	print("BASIC INFORMATION:")
	print(f"Created: {format_datetime(order.get('datetime'))}")
	print(f"Status: {order.get('status', 'N/A')}")
	print(f"Type: {order.get('type', 'N/A')}")
	
	# Financial Information
	print("\nFINANCIAL INFORMATION:")
	print(f"Total Amount: {format_money(order.get('total'))}")
	print(f"Tax: {format_money(order.get('tax'))}")
	print(f"Processing Fee: {format_money(order.get('processingFee'))}")
	
	# Coupon Information
	if order.get('coupon'):
		print("\nCOUPON USED:")
		coupon = order['coupon']
		print(f"Code: {coupon.get('code', 'N/A')}")
		print(f"Discount: {format_money(coupon.get('amount'))}")
	
	# Payment Information
	print("\nPAYMENT INFORMATION:")
	print(f"Payment Type: {order.get('paymentType', 'N/A')}")
	print(f"Payment Method Details:")
	for key, value in order.items():
		if key.startswith('card') and value:
			print(f"  - {key}: {value}")
	
	# Certificate Information
	if order.get('certificate'):
		print("\nCERTIFICATE INFORMATION:")
		cert = order['certificate']
		print(f"Certificate ID: {cert.get('id', 'N/A')}")
		print(f"Original Amount: {format_money(cert.get('originalAmount'))}")
		print(f"Remaining Amount: {format_money(cert.get('remainingAmount'))}")
	
	# Appointment Information
	if order.get('appointmentID'):
		print("\nAPPOINTMENT INFORMATION:")
		print(f"Appointment ID: {order.get('appointmentID', 'N/A')}")
		print(f"Calendar ID: {order.get('calendarID', 'N/A')}")
		
	# Forms and Custom Fields
	if order.get('forms'):
		print("\nFORM INFORMATION:")
		for form in order['forms']:
			print(f"\nForm: {form.get('name', 'Unnamed Form')}")
			for field in form.get('values', []):
				print(f"  - {field.get('name', 'Unnamed Field')}: {field.get('value', 'N/A')}")

def main():
	try:
		client = AcuityClient()
		
		print("Fetching orders from Acuity Scheduling...")
		orders = client.get_orders(limit=100)  # Fetch 100 orders per request
		
		print(f"\nFound {len(orders)} orders total")
		
		for order in orders:
			print_order_details(order)
			
	except Exception as e:
		print(f"Error: {str(e)}")
		sys.exit(1)

if __name__ == "__main__":
	main()