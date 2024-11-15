import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os
from dotenv import load_dotenv
from pathlib import Path

# Get the root directory and load environment variables
ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / '.env.dev'
CSV_PATH = ROOT_DIR / 'Clients-Grid view-4.csv'

# Load environment variables from root directory
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

def update_customer_data():
	# Verify CSV file exists
	if not CSV_PATH.exists():
		raise FileNotFoundError(f"CSV file not found at {CSV_PATH}")

	# Read the CSV file
	try:
		df = pd.read_csv(CSV_PATH)
	except Exception as e:
		print(f"Error reading CSV file: {str(e)}")
		raise

	# Clean and prepare the data
	df['Gender'] = df['Sex'].map({'Female': 'female', 'Male': 'male', 'Unknown': None})
	
	# Convert account creation dates to proper format
	try:
		df['Account Created'] = pd.to_datetime(df['Account Created'], format='%d %B %Y')
	except Exception as e:
		print(f"Error converting dates: {str(e)}")
		raise

	# Prepare update query
	update_query = """
		UPDATE customers 
		SET 
			gender = %(gender)s,
			account_created = %(account_created)s
		WHERE latepoint_id = %(latepoint_id)s
		RETURNING latepoint_id, email;
	"""
	
	# Connect to database
	conn = get_db_connection()
	cur = conn.cursor(cursor_factory=RealDictCursor)
	
	try:
		updated_count = 0
		skipped_count = 0
		
		for _, row in df.iterrows():
			if pd.notna(row['Customer ID']) and str(row['Customer ID']).isdigit():
				values = {
					'latepoint_id': int(row['Customer ID']),
					'gender': row['Gender'],
					'account_created': row['Account Created'].date() if pd.notna(row['Account Created']) else None
				}
				
				try:
					cur.execute(update_query, values)
					result = cur.fetchone()
					
					if result:
						updated_count += 1
						print(f"Updated customer: ID {result['latepoint_id']}, Email: {result['email']}")
					else:
						skipped_count += 1
						print(f"Skipped customer: ID {values['latepoint_id']} (not found in database)")
				
				except psycopg2.Error as e:
					print(f"Error updating customer {values['latepoint_id']}: {str(e)}")
					continue
		
		conn.commit()
		print(f"\nSummary:")
		print(f"Total records updated: {updated_count}")
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
		print(f"Starting update from AirTable data...")
		print(f"Using environment file: {ENV_PATH}")
		print(f"Using CSV file: {CSV_PATH}")
		update_customer_data()
		print("Update completed successfully")
	except Exception as e:
		print(f"Script failed: {str(e)}")