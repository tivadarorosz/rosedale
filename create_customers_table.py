import os
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env.dev")

def create_customers_table():
	try:
		conn = psycopg2.connect(
			host=os.getenv("DB_HOST"),
			database=os.getenv("DB_NAME"),
			user=os.getenv("DB_USER"),
			password=os.getenv("DB_PASSWORD"),
			port=os.getenv("DB_PORT")
		)
	
		cur = conn.cursor()
	
		# Drop the customers table if it exists
		cur.execute("DROP TABLE IF EXISTS customers")
	
		# Create the customers table with new fields, indexes, and constraints
		cur.execute("""
			CREATE TABLE customers (
				id SERIAL PRIMARY KEY,
				latepoint_id INTEGER UNIQUE,
				square_id TEXT UNIQUE,
				first_name VARCHAR(50) NOT NULL,
				last_name VARCHAR(50) NOT NULL,
				email VARCHAR(100) UNIQUE NOT NULL,
				phone VARCHAR(20),
				gender VARCHAR(10),
				dob DATE DEFAULT NULL,
				location VARCHAR(100) DEFAULT NULL,
				postcode VARCHAR(10) DEFAULT NULL,
				status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'deleted', 'guest', 'vip')),
				is_pregnant BOOLEAN DEFAULT NULL,
				has_cancer BOOLEAN DEFAULT NULL,
				has_blood_clots BOOLEAN DEFAULT NULL,
				has_infectious_disease BOOLEAN DEFAULT NULL,
				has_bp_issues BOOLEAN DEFAULT NULL,
				has_severe_pain BOOLEAN DEFAULT NULL,
				newsletter_subscribed BOOLEAN DEFAULT FALSE,
				accepted_terms BOOLEAN DEFAULT TRUE,
				account_created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
				last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
				CONSTRAINT at_least_one_id CHECK (
					(latepoint_id IS NOT NULL) OR (square_id IS NOT NULL)
				)
			)
		""")

		# Create indexes for faster searching
		cur.execute("""
			CREATE INDEX idx_latepoint_id ON customers(latepoint_id);
			CREATE INDEX idx_square_id ON customers(square_id);
		""")
	
		conn.commit()
		print("customers table created successfully with indexes and constraints")
	
	except (Exception, psycopg2.Error) as error:
		print("Error creating customers table:", error)
	finally:
		if conn:
			conn.close()
			print("Database connection closed")

if __name__ == "__main__":
	create_customers_table()