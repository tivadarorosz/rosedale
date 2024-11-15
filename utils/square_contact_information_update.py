from square.client import Client
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime

# Get the root directory and load environment variables
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / '.env.dev'
load_dotenv(ENV_PATH)

def get_db_connection():
	try:
		return psycopg2.connect(
			host=os.getenv("DB_HOST"),
			database=os.getenv("DB_NAME"),
			user=os.getenv("DB_USER"),
			password=os.getenv("DB_PASSWORD"),
			port=os.getenv("DB_PORT")
		)
	except psycopg2.Error as e:
		print(f"Database connection error: {str(e)}")
		raise

def get_square_client():
	try:
		return Client(
			access_token=os.getenv('SQUARE_ACCESS_TOKEN'),
			environment='production'
		)
	except Exception as e:
		print(f"Square client initialization error: {str(e)}")
		raise

def fetch_square_customers():
	client = get_square_client()
	customers_api = client.customers
	customers = []
	cursor = None

	try:
		while True:
			result = customers_api.list_customers(
				cursor=cursor,
				limit=100
			)

			if result.is_success():
				page_customers = result.body.get('customers', [])
				customers.extend(page_customers)
				cursor = result.body.get('cursor')
				
				if not cursor:
					break
					
				print(f"Fetched {len(page_customers)} customers from Square...")
			
			elif result.is_error():
				print(f"Error fetching Square customers: {result.errors}")
				raise Exception(result.errors)
				
		return customers

	except Exception as e:
		print(f"Error in fetch_square_customers: {str(e)}")
		raise

def update_empty_customer_fields():
	# Update query that only updates empty fields
	update_query = """
		UPDATE customers 
		SET 
			phone = CASE 
				WHEN phone IS NULL OR phone = '' 
				THEN %(phone)s 
				ELSE phone 
			END,
			location = CASE 
				WHEN location IS NULL OR location = '' 
				THEN %(location)s 
				ELSE location 
			END,
			postcode = CASE 
				WHEN postcode IS NULL OR postcode = '' 
				THEN %(postcode)s 
				ELSE postcode 
			END,
			last_updated = CURRENT_TIMESTAMP
		WHERE 
			email = %(email)s
			AND (
				(phone IS NULL OR phone = '')
				OR (location IS NULL OR location = '')
				OR (postcode IS NULL OR postcode = '')
			)
		RETURNING id, email, phone, location, postcode;
	"""
	
	conn = get_db_connection()
	cur = conn.cursor(cursor_factory=RealDictCursor)
	
	try:
		print("Fetching customers from Square...")
		square_customers = fetch_square_customers()
		print(f"Found {len(square_customers)} customers in Square")

		updates_count = 0
		skipped_count = 0
		no_email_count = 0
		
		for customer in square_customers:
			# Skip if no email address
			if not customer.get('email_address'):
				no_email_count += 1
				continue

			# Get address details if available
			address = customer.get('address', {})
			
			customer_data = {
				'email': customer.get('email_address'),
				'phone': customer.get('phone_number', ''),
				'location': address.get('locality', ''),  # City/Town
				'postcode': address.get('postal_code', '')
			}

			try:
				cur.execute(update_query, customer_data)
				result = cur.fetchone()
				
				if result:
					updates_count += 1
					print(f"\nUpdated customer: ID {result['id']}, Email: {result['email']}")
					if result['phone']: print(f"  Phone: {result['phone']}")
					if result['location']: print(f"  Location: {result['location']}")
					if result['postcode']: print(f"  Postcode: {result['postcode']}")
				else:
					skipped_count += 1
			
			except psycopg2.Error as e:
				print(f"Error updating customer {customer_data['email']}: {str(e)}")
				continue
		
		conn.commit()
		print(f"\nSummary:")
		print(f"Total records updated: {updates_count}")
		print(f"Total records skipped (no empty fields or no match): {skipped_count}")
		print(f"Total records without email: {no_email_count}")
		
	except Exception as e:
		conn.rollback()
		print(f"Error updating records: {str(e)}")
		raise
	finally:
		cur.close()
		conn.close()

if __name__ == "__main__":
	try:
		print(f"Starting contact information update from Square API...")
		print(f"Using environment file: {ENV_PATH}")
		update_empty_customer_fields()
		print("Update completed successfully")
	except Exception as e:
		print(f"Script failed: {str(e)}")