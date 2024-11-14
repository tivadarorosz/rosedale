from flask import Blueprint, request, jsonify
import os
from customers.db import create_db_customer
from api_utils import get_gender
from campfire_utils import send_message
import logging
import traceback

logger = logging.getLogger(__name__)

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

@customers_bp.route("/new", methods=["POST"])
def create_customer():
	try:
		# Parse incoming request data
		data = request.form
		logger.info(f"Received data: {data}")

		# Extract and validate required fields
		customer_id = data.get("id")
		first_name = data.get("first_name")
		last_name = data.get("last_name")
		full_name = data.get("full_name")
		email = data.get("email")
		phone = data.get("phone")

		if not all([customer_id, first_name, last_name, full_name, email, phone]):
			return jsonify({"error": "Missing required customer fields"}), 400

		# Validate phone number (must start with +44)
		if not phone.startswith("+44"):
			return jsonify({"error": "Invalid phone number format"}), 400

		# Determine gender from first name using Gender API
		gender = get_gender(first_name)

		# Set the default status to 'active'
		status = "active"

		# Extract custom fields
		# custom_fields = data.to_dict(flat=False).get("custom_fields", {})
		customer = {
			"id": customer_id,
			"first_name": first_name,
			"last_name": last_name,
			"full_name": full_name,
			"email": email,
			"phone": phone,
			"gender": gender,
			"status": status,
			"is_pregnant": data.get('custom_fields[cf_uSnk1aJv]') == "on",
			"has_cancer": data.get('custom_fields[cf_ku8f8Fd8]') == "on",
			"has_blood_clots": data.get('custom_fields[cf_i6npNsJK]') == "on",
			"has_infectious_disease": data.get('custom_fields[cf_LICrcXyq]') == "on",
			"has_bp_issues": data.get('custom_fields[cf_sIG5JoOc]') == "on",
			"has_severe_pain": data.get('custom_fields[cf_R5ffCcvB]') == "on",
			"customer_notes": data.get('custom_fields[cf_AYXmttXr]'),
			"newsletter_signup": data.get('custom_fields[cf_13R2jN9C]') == "on",
			"accepted_terms": data.get('custom_fields[cf_xGQSo978]') == "on"
		}

		logger.info(f"customer_notes: {data.get('custom_fields[cf_AYXmttXr]')}")
		logger.info(f"Received customer data: {customer}")

		# Post a message to Campfire in the Studio channel
		try:
			message = f"🎉 New Customer: {full_name} ({email}) just signed up!"
			
			if os.getenv("FLASK_ENV") != "development":
				status, response = send_message("studio", message)
				logger.info(f"Campfire Response: Status {status}, Body: {response}")
		
		except Exception as e:
			logger.error(f"Failed to notify Studio: {str(e)}")
			return jsonify({"error": f"Failed to notify Studio"}), 500

		# Create the customer in the database
		customer_id = create_db_customer(customer)

		# Return success response
		return jsonify({"id": customer_id, "message": "Customer created successfully"}), 201

	except KeyError as e:
		logger.error(f"Missing key: {str(e)}")
		return jsonify({"error": f"Missing key: {str(e)}"}), 400
	except Exception as e:
		# Handle unexpected errors
		logger.error(f"Unexpected error: {str(e)}")
		logger.error("An unexpected error occurred:\n%s", traceback.format_exc())
		return jsonify({"error": "An unexpected error occurred"}), 500