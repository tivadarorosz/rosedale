import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging
from src.utils.email_utils import send_error_email

logger = logging.getLogger(__name__)

# Environment configuration
if os.getenv("FLASK_DEBUG") == "1":
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
		send_error_email(str(error))
		raise

def create_customer(customer):
	try:
		conn = get_db_connection()
		cur = conn.cursor(cursor_factory=RealDictCursor)
		
		query = """
			INSERT INTO customers (
				latepoint_id, square_id, first_name, last_name, email, phone, gender, dob, location, postcode, status, type, 
				is_pregnant, has_cancer, has_blood_clots, has_infectious_disease, has_bp_issues, has_severe_pain, 
				newsletter_subscribed, accepted_terms, source
			)
			VALUES (
				%(latepoint_id)s, %(square_id)s, %(first_name)s, %(last_name)s, %(email)s, %(phone)s, %(gender)s, 
				%(dob)s, %(location)s, %(postcode)s, %(status)s, %(type)s, %(is_pregnant)s, %(has_cancer)s, %(has_blood_clots)s, 
				%(has_infectious_disease)s, %(has_bp_issues)s, %(has_severe_pain)s, %(newsletter_subscribed)s, %(accepted_terms)s, %(source)s
			)
			RETURNING id;
		"""
		
		values = {
			"latepoint_id": customer.get("latepoint_id"),
			"square_id": customer.get("square_id"),
			"first_name": customer["first_name"],
			"last_name": customer["last_name"],
			"email": customer["email"],
			"phone": customer["phone"],
			"gender": customer["gender"],
			"dob": customer.get("dob"),
			"location": customer.get("location"),
			"postcode": customer.get("postcode"),
			"status": customer["status"],
			"type": customer["type"],
			"is_pregnant": customer.get("is_pregnant", False),
			"has_cancer": customer.get("has_cancer", False),
			"has_blood_clots": customer.get("has_blood_clots", False),
			"has_infectious_disease": customer.get("has_infectious_disease", False),
			"has_bp_issues": customer.get("has_bp_issues", False),
			"has_severe_pain": customer.get("has_severe_pain", False),
			"newsletter_subscribed": customer.get("newsletter_signup", False),
			"accepted_terms": customer.get("accepted_terms", False),
			"source": customer.get("source")
		}
		
		try:
			cur.execute(query, values)
			conn.commit()
			return cur.fetchone()["id"]
		except (Exception, psycopg2.Error) as error:
			print("Error creating customer:", error)
			send_error_email(str(error))
			conn.rollback()
			raise
		finally:
			cur.close()
			conn.close()
	except (Exception, psycopg2.Error) as error:
		print("Error creating customer:", error)
		send_error_email(str(error))
		conn.rollback()
		raise

def update_latepoint_customer(customer):
# Update existing customer record with Latepoint data, preserving Square ID if exists. Only updates Latepoint-specific fields.
	try:
		conn = get_db_connection()
		cur = conn.cursor(cursor_factory=RealDictCursor)
		
		query = """
			UPDATE customers 
			SET 
				latepoint_id = %(latepoint_id)s,
				first_name = %(first_name)s,
				last_name = %(last_name)s,
				phone = %(phone)s,
				gender = %(gender)s,
				status = %(status)s,
				type = %(type)s,
				is_pregnant = %(is_pregnant)s,
				has_cancer = %(has_cancer)s,
				has_blood_clots = %(has_blood_clots)s,
				has_infectious_disease = %(has_infectious_disease)s,
				has_bp_issues = %(has_bp_issues)s,
				has_severe_pain = %(has_severe_pain)s,
				newsletter_subscribed = %(newsletter_subscribed)s,
				accepted_terms = %(accepted_terms)s,
				last_updated = CURRENT_TIMESTAMP
			WHERE email = %(email)s 
			RETURNING id;
		"""
		
		values = {
			"latepoint_id": customer["latepoint_id"],
			"first_name": customer["first_name"],
			"last_name": customer["last_name"],
			"email": customer["email"],
			"phone": customer["phone"],
			"gender": customer["gender"],
			"status": customer["status"],
			"type": customer["type"],
			"is_pregnant": customer.get("is_pregnant", False),
			"has_cancer": customer.get("has_cancer", False),
			"has_blood_clots": customer.get("has_blood_clots", False),
			"has_infectious_disease": customer.get("has_infectious_disease", False),
			"has_bp_issues": customer.get("has_bp_issues", False),
			"has_severe_pain": customer.get("has_severe_pain", False),
			"newsletter_subscribed": customer.get("newsletter_signup", False),
			"accepted_terms": customer.get("accepted_terms", False)
		}
		
		try:
			cur.execute(query, values)
			conn.commit()
			result = cur.fetchone()
			return result["id"] if result else None
		except (Exception, psycopg2.Error) as error:
			logger.error("Error updating Latepoint customer:", error)
			send_error_email(str(error))
			conn.rollback()
			raise
		finally:
			cur.close()
			conn.close()
	except (Exception, psycopg2.Error) as error:
		logger.error("Error updating Latepoint customer:", error)
		send_error_email(str(error))
		raise
	
def update_square_customer(customer):
	# Update existing customer record with Square ID only. Preserves all other existing customer data.
	try:
		conn = get_db_connection()
		cur = conn.cursor(cursor_factory=RealDictCursor)
		
		query = """
			UPDATE customers 
			SET 
				square_id = %(square_id)s,
				last_updated = CURRENT_TIMESTAMP
			WHERE email = %(email)s 
			RETURNING id;
		"""
		
		values = {
			"square_id": customer["square_id"],
			"email": customer["email"]
		}
		
		try:
			cur.execute(query, values)
			conn.commit()
			result = cur.fetchone()
			return result["id"] if result else None
		except (Exception, psycopg2.Error) as error:
			logger.error("Error updating Square customer:", error)
			send_error_email(str(error))
			conn.rollback()
			raise
		finally:
			cur.close()
			conn.close()
	except (Exception, psycopg2.Error) as error:
		logger.error("Error updating Square customer:", error)
		send_error_email(str(error))
		raise

def validate_latepoint_customer(customer):
	"""Validate required fields for Latepoint customer data."""
	required_fields = [
		'latepoint_id', 'first_name', 'last_name', 
		'email', 'phone', 'gender', 'status', 'type'
	]
	return all(customer.get(field) for field in required_fields)

def validate_square_customer(customer):
	"""Validate required fields for Square customer data."""
	required_fields = ['square_id', 'email']
	return all(customer.get(field) for field in required_fields)
		
def check_email_exists(email):
		try:
			conn = get_db_connection()
			cur = conn.cursor(cursor_factory=RealDictCursor)
			
			query = """
				SELECT id 
				FROM customers 
				WHERE email = %(email)s
				LIMIT 1;
			"""
			
			try:
				cur.execute(query, {"email": email})
				result = cur.fetchone()
				return bool(result)
			except (Exception, psycopg2.Error) as error:
				print("Error checking email existence:", error)
				send_error_email(str(error))
				raise
			finally:
				cur.close()
				conn.close()
		except (Exception, psycopg2.Error) as error:
			print("Error checking email existence:", error)
			send_error_email(str(error))
			raise
		
def determine_customer_type(email):
	"""
	Determine customer type based on email domain and business rules
	"""
	try:
		domain = email.split('@')[1].lower()
		
		# Employee check
		if domain == "rosedalemassage.co.uk":
			return "employee"
			
		# Default to regular client
		return "client"
	except Exception as e:
		logger.error(f"Error determining customer type: {e}")
		send_error_email(str(e))
		return "client"  # Default to client if there's any error