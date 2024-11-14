import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

if os.getenv("FLASK_ENV") == "development":
	load_dotenv(".env.dev")
else:
	load_dotenv()

def get_db_connection():
	try:
		conn = psycopg2.connect(
			host=os.getenv("DB_HOST"),
			database=os.getenv("DB_NAME"),
			user=os.getenv("DB_USER"),
			password=os.getenv("DB_PASSWORD"),
			port=os.getenv("DB_PORT")
		)
		return conn
	except (Exception, psycopg2.Error) as error:
		print("Error connecting to the database:", error)
		raise

def create_db_customer(customer):
	conn = get_db_connection()
	cur = conn.cursor(cursor_factory=RealDictCursor)
	
	query = """
		INSERT INTO customers (
			id, first_name, last_name, email, phone, gender, dob, location, postcode, status, custom_data, newsletter_subscribed, accepted_terms
		)
		VALUES (%(id)s, %(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(gender)s, %(dob)s, %(location)s, %(postcode)s, %(status)s, %(custom_data)s, %(newsletter_subscribed)s, %(accepted_terms)s)
		RETURNING id;
	"""
	
	values = {
		"id": customer["id"],
		"first_name": customer["first_name"],
		"last_name": customer["last_name"],
		"email": customer["email"],
		"phone": customer["phone"],
		"gender": customer["gender"],
		"dob": customer.get("dob", None),
		"location": customer.get("location", None),
		"postcode": customer.get("postcode", None),
		"status": customer["status"],
		"custom_data": customer.get("custom_data", None),
		"newsletter_subscribed": customer.get("newsletter_signup", False),
		"accepted_terms": customer.get("accepted_terms", False)
	}
	
	try:
		cur.execute(query, values)
		conn.commit()
		customer_id = cur.fetchone()["id"]
		return customer_id
	except (Exception, psycopg2.Error) as error:
		print("Error creating customer:", error)
		conn.rollback()
		raise
	finally:
		cur.close()
		conn.close()