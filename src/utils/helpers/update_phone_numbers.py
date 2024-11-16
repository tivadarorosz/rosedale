import os
import csv
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env.dev file in the root folder
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env.dev'))

def update_phone_numbers():
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
				email = row['email']
				phone = row['phone']

				# Update the phone number in the customers table based on email match
				update_query = """
					UPDATE customers
					SET phone = %s
					WHERE email = %s
				"""
				cur.execute(update_query, (phone, email))

		conn.commit()
		print("Phone numbers updated successfully")

	except (Exception, psycopg2.Error) as error:
		print("Error updating phone numbers:", error)

	finally:
		if conn:
			cur.close()
			conn.close()
			print("Database connection closed")

if __name__ == "__main__":
	update_phone_numbers()