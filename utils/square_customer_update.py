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
					
				print(f"Fetched {len(page_customers)} customers...")
			
			elif result.is_error():
				print(f"Error fetching Square customers: {result.errors}")
				raise Exception(result.errors)
				
		return customers

	except Exception as e:
		print(f"Error in fetch_square_customers: {str(e)}")
		raise

def update_customer_data():
	# First try to update by email
	update_by_email_query = """
		UPDATE customers 
		SET 
			square_id = %(square_id)s,
			first_name = %(first_name)s,
			last_name = %(last_name)s,
			phone = %(phone)s,
			last_updated = CURRENT_TIMESTAMP
		WHERE email = %(email)s AND square_id IS NULL
		RETURNING id, email;
	"""

	# Then update any remaining records by square_id
	update_by_square_id_query = """
		UPDATE customers 
		SET 
			first_name = %(first_name)s,
			last_name = %(last_name)s,
			email = %(email)s,
			phone = %(phone)s,
			last_updated = CURRENT_TIMESTAMP
		WHERE square_id = %(square_id)s
		RETURNING id, square_id, email;
	"""
	
	conn = get_db_connection()
	cur = conn.cursor(cursor_factory=RealDictCursor)
	
	try:
		print("Fetching customers from Square...")
		square_customers = fetch_square_customers()
		print(f"Found {len(square_customers)} customers in Square")

		email_updates = 0
		square_id_updates = 0
		skipped_count = 0
		
		for customer in square_customers:
			customer_data = {
				'square_id': customer.get('id'),
				'first_name': customer.get('given_name', ''),
				'last_name': customer.get('family_name', ''),
				'email': customer.get('email_address', ''),
				'phone': customer.get('phone_number', '')
			}
			
			if not customer_data['square_id']:
				continue

			try:
				# First try to match and update by email
				if customer_data['email']:
					cur.execute(update_by_email_query, customer_data)
					result = cur.fetchone()
					
					if result:
						email_updates += 1
						print(f"Updated customer by email: Database ID {result['id']}, Email: {result['email']}")
						continue

				# If no email match, try to update by square_id
				cur.execute(update_by_square_id_query, customer_data)
				result = cur.fetchone()
				
				if result:
					square_id_updates += 1
					print(f"Updated customer by Square ID: Database ID {result['id']}, Square ID: {result['square_id']}")
				else:
					skipped_count += 1
					if customer_data['email']:
						print(f"Skipped customer: Square ID {customer_data['square_id']}, Email: {customer_data['email']}")
					else:
						print(f"Skipped customer: Square ID {customer_data['square_id']} (no email)")
			
			except psycopg2.Error as e:
				print(f"Error updating customer {customer_data.get('square_id')}: {str(e)}")
				continue
		
		conn.commit()
		print(f"\nSummary:")
		print(f"Total records matched by email and updated: {email_updates}")
		print(f"Total records matched by Square ID and updated: {square_id_updates}")
		print(f"Total records skipped: {skipped_count}")
		
	except Exception as e:
		conn.rollback()
		print(f"Error updating records: {str(e)}")
		raise
	finally:
		cur.close()
		conn.close()

if __name__ == "__main__":
	try:
		print(f"Starting update from Square API...")
		print(f"Using environment file: {ENV_PATH}")
		update_customer_data()
		print("Update completed successfully")
	except Exception as e:
		print(f"Script failed: {str(e)}")