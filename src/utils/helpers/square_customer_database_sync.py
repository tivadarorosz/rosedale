import os
import psycopg2
from psycopg2.extras import RealDictCursor
from square.client import Client
import requests
from convertkit import ConvertKit
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONVERTKIT_API_KEY = os.getenv("CONVERTKIT_API_KEY")
MILLS_FORM_ID = os.getenv("CONVERTKIT_MILLS_FORM_ID")

# Load environment variables
load_dotenv()

def get_db_connection():
	"""Create a database connection"""
	return psycopg2.connect(
		host=os.getenv("DB_HOST"),
		database=os.getenv("DB_NAME"),
		user=os.getenv("DB_USER"),
		password=os.getenv("DB_PASSWORD"),
		port=os.getenv("DB_PORT")
	)

def get_gender(first_name):
	"""Determine gender using Gender API"""
	api_key = os.getenv("GENDER_API_KEY")
	url = f"https://gender-api.com/get?name={first_name}&key={api_key}"
	
	try:
		response = requests.get(url)
		data = response.json()
		return data.get("gender", "unknown")
	except Exception as e:
		logger.error(f"Error determining gender: {e}")
		return "unknown"

def determine_customer_type(email):
	"""Determine customer type based on email domain"""
	try:
		domain = email.split('@')[1].lower()
		
		if domain == "rosedalemassage.co.uk":
			return "employee"
		
		return "client"
	except Exception as e:
		logger.error(f"Error determining customer type: {e}")
		return "client"

def check_email_exists(conn, email):
	"""Check if email exists in database"""
	cur = conn.cursor(cursor_factory=RealDictCursor)
	
	query = "SELECT id FROM customers WHERE email = %(email)s LIMIT 1;"
	
	try:
		cur.execute(query, {"email": email})
		result = cur.fetchone()
		return bool(result)
	finally:
		cur.close()

def insert_customer(conn, customer_data):
	"""Insert new customer into database"""
	cur = conn.cursor(cursor_factory=RealDictCursor)
	
	query = """
		INSERT INTO customers (
			square_id, first_name, last_name, email, phone, gender, location, postcode,
			status, type, is_pregnant, has_cancer, has_blood_clots, has_infectious_disease,
			has_bp_issues, has_severe_pain, newsletter_subscribed, accepted_terms
		)
		VALUES (
			%(square_id)s, %(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(gender)s,
			%(location)s, %(postcode)s, %(status)s, %(type)s, %(is_pregnant)s, %(has_cancer)s,
			%(has_blood_clots)s, %(has_infectious_disease)s, %(has_bp_issues)s,
			%(has_severe_pain)s, %(newsletter_subscribed)s, %(accepted_terms)s
		)
		RETURNING id;
	"""
	
	try:
		cur.execute(query, customer_data)
		conn.commit()
		return cur.fetchone()["id"]
	finally:
		cur.close()

def sync_square_customers():
	"""Main function to sync Square customers with database"""
	# Initialize Square client
	square_client = Client(
		access_token=os.getenv("SQUARE_ACCESS_TOKEN"),
		environment='production'
	)
	
	# Get database connection
	conn = get_db_connection()
	
	try:
		cursor = None
		while True:
			# Get customers from Square
			result = square_client.customers.list_customers(
				cursor=cursor,
				limit=100
			)
			
			if result.is_error():
				logger.error(f"Error fetching Square customers: {result.errors}")
				break
				
			customers = result.body.get("customers", [])
			
			# Process each customer
			for customer in customers:
				try:
					email = customer.get("email_address")
					
					# Skip if no email address
					if not email:
						continue
					
					# Check if customer exists
					if check_email_exists(conn, email):
						logger.info(f"Customer exists: {email}")
						continue
					
					# Get address details
					address = customer.get("address", {})
					
					# Prepare customer data
					customer_data = {
						"square_id": customer.get("id"),
						"first_name": customer.get("given_name", ""),
						"last_name": customer.get("family_name", ""),
						"email": email,
						"phone": customer.get("phone_number", ""),
						"gender": get_gender(customer.get("given_name", "")),
						"location": address.get("locality", ""),
						"postcode": address.get("postal_code", ""),
						"status": "active",
						"type": determine_customer_type(email),
						"is_pregnant": False,
						"has_cancer": False,
						"has_blood_clots": False,
						"has_infectious_disease": False,
						"has_bp_issues": False,
						"has_severe_pain": False,
						"newsletter_subscribed": False,
						"accepted_terms": False
					}
					
					# Insert new customer
					customer_id = insert_customer(conn, customer_data)
					logger.info(f"Inserted new customer: {email} (ID: {customer_id})")
					
					# Add customer to the newsletter (auto opt-in)
					try:
						# ConvertKit API endpoint for adding a subscriber to a form
						url = f"https://api.convertkit.com/v3/forms/{MILLS_FORM_ID}/subscribe"
					
						# Create subscriber data
						subscriber_data = {
							"api_key": CONVERTKIT_API_KEY,
							"email": email,
							"first_name": customer_data.get("first_name"),
							"fields": {
								"last_name": customer_data.get("last_name")
							}
						}
					
						# Send POST request to add subscriber to the form
						headers = {
							"Content-Type": "application/json"
						}
						response = requests.post(url, json=subscriber_data, headers=headers)
					
						# Check the response status
						if response.status_code == 200:
							logger.info(f"Successfully added {email} to ConvertKit form: {MILLS_FORM_ID}")
						else:
							logger.error(f"Failed to add {email} to ConvertKit form: {MILLS_FORM_ID}. Status Code: {response.status_code}")
							logger.error(f"Response Content: {response.text}")
					
					except Exception as e:
						logger.error(f"Error adding {email} to ConvertKit: {str(e)}")
					
				except Exception as e:
					logger.error(f"Error processing customer {email}: {e}")
					continue
			
			# Check if there are more customers
			cursor = result.body.get("cursor")
			if not cursor:
				break
				
	except Exception as e:
		logger.error(f"Sync error: {e}")
	finally:
		conn.close()

if __name__ == "__main__":
	sync_square_customers()	