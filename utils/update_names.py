import os
import csv
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env.dev file in the root folder
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.dev'))

def update_names():
	try:
		# Connect to the PostgreSQL database
		conn = psycopg2.connect(
			host=os.getenv("DB_HOST"),
			database=os.getenv("DB_NAME"),
			user=os.getenv("DB_USER"),
			password=os.getenv("DB_PASSWORD"),
			port=os.getenv("DB_PORT")
		)
		cur = conn.cursor()

		# Read the CSV file
		csv_path = os.path.join(os.path.dirname(__file__), '..', 'customers_766499.csv')
		with open(csv_path, 'r') as file:
			csv_reader = csv.DictReader(file)
			for row in csv_reader:
				full_name = row['full_name']
				email = row['email']
				latepoint_id = row['latepoint_id']

				# Split the full name into first and last names
				names = full_name.split(' ')
				first_name = names[0]
				last_name = ' '.join(names[1:]) if len(names) > 1 else ''

				# Update the first and last names in the customers table based on email match
				update_query = """
					UPDATE customers
					SET first_name = %s, last_name = %s, latepoint_id = %s
					WHERE email = %s
				"""
				cur.execute(update_query, (first_name, last_name, latepoint_id, email))

		conn.commit()
		print("First and last names updated successfully")

	except (Exception, psycopg2.Error) as error:
		print("Error updating first and last names:", error)

	finally:
		if conn:
			cur.close()
			conn.close()
			print("Database connection closed")

if __name__ == "__main__":
	update_names()