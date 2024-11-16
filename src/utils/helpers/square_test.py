from square.http.auth.o_auth_2 import BearerAuthCredentials
from square.client import Client
from dotenv import load_dotenv
import os

load_dotenv(".env.dev")

token=os.getenv("SQUARE_ACCESS_TOKEN")
studio=os.getenv("SQUARE_LOCATION_ID")
# print(token)

client = Client(
	bearer_auth_credentials=BearerAuthCredentials(
		access_token=token
	),
	environment='production')

# Replace 'LOCATION_ID' with your actual location ID
result = client.payments.list_payments(location_id=studio)

if result.is_success():
	for payment in result.body['payments']:
		amount_in_pounds = payment['amount_money']['amount'] / 100
		formatted_amount = f"£{amount_in_pounds:.2f}"
		
		print(f"Payment ID: {payment['id']}")
		print(f"Amount: {formatted_amount}")
		print(f"Status: {payment['status']}")
		print(f"Created At: {payment['created_at']}")
		print("---")
elif result.is_error():
	for error in result.errors:
		print(error['category'])
		print(error['code'])
		print(error['detail'])
		
print("\nCustomers:")
result = client.customers.list_customers()

if result.is_success():
	for customer in result.body['customers']:
		locality = customer.get('address', {}).get('locality', 'No locality')
		print(f"Customer ID: {customer['id']}")
		print(f"Name: {customer['given_name']} {customer['family_name']}")
		print(f"Email: {customer['email_address']}")
		print(f"Locality: {locality}")
		print("---") 
elif result.is_error():
	for error in result.errors:
		print(error['category'])
		print(error['code'])
		print(error['detail'])