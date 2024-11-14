import json
from flask import Blueprint, request, jsonify
from campfire_utils import send_message
import logging

logger = logging.getLogger(__name__)

# Define the Blueprint
customers = Blueprint("customers", __name__)

@customers.route("/new", methods=["POST"])
def create_customer():
	try:
		# Parse incoming request data
		data = request.get_data(as_text=True)
		logger.info(f"Received data: {data}")

		# Check if the data is a valid JSON string
		try:
			customer_data_list = json.loads(data)
		except json.JSONDecodeError:
			return jsonify({"error": "Invalid JSON data"}), 400

		# Iterate over each customer in the list
		for customer_data in customer_data_list:
			# Extract and validate required fields
			customer_id = customer_data.get("id")
			first_name = customer_data.get("first_name")
			last_name = customer_data.get("last_name")
			full_name = customer_data.get("full_name")
			email = customer_data.get("email")
			phone = customer_data.get("phone")

			if not all([customer_id, first_name, last_name, full_name, email, phone]):
				return jsonify({"error": "Missing required customer fields"}), 400

			# Validate phone number (must start with +44)
			if not phone.startswith("+44"):
				return jsonify({"error": "Invalid phone number format"}), 400

			# Extract custom fields
			custom_fields = customer_data.get("custom_fields", {})
			customer = {
				"id": customer_id,
				"first_name": first_name,
				"last_name": last_name,
				"full_name": full_name,
				"email": email,
				"phone": phone,
				"is_pregnant": custom_fields.get("cf_uSnk1aJv", "off") == "on",
				"has_cancer": custom_fields.get("cf_ku8f8Fd8", "off") == "on",
				"has_blood_clots": custom_fields.get("cf_i6npNsJK", "off") == "on",
				"has_infectious_disease": custom_fields.get("cf_LICrcXyq", "off") == "on",
				"has_bp_issues": custom_fields.get("cf_sIG5JoOc", "off") == "on",
				"has_severe_pain": custom_fields.get("cf_R5ffCcvB", "off") == "on",
				"customer_notes": custom_fields.get("cf_AYXmttXr", ""),
				"newsletter_signup": custom_fields.get("cf_13R2jN9C", "off") == "on",
				"accepted_terms": custom_fields.get("cf_xGQSo978", "off") == "on",
			}

			logger.info(f"Received customer data: {customer}")

			# Post a message to Campfire in the Studio channel
			try:
				message = f"🎉 New Customer: {full_name} ({email}) just signed up!"
				status, response = send_message("studio", message)
				logger.info(f"Campfire Response: Status {status}, Body: {response}")
			except Exception as e:
				logger.error(f"Failed to notify Studio: {str(e)}")
				return jsonify({"error": f"Failed to notify Studio"}), 500

		# Return success response
		return jsonify({"message": "Customer(s) created successfully"}), 201

	except KeyError as e:
		logger.error(f"Missing key: {str(e)}")
		return jsonify({"error": f"Missing key: {str(e)}"}), 400
	except Exception as e:
		# Handle unexpected errors
		logger.error(f"Unexpected error: {str(e)}")
		return jsonify({"error": "An unexpected error occurred"}), 500