from flask import Blueprint, request, jsonify, current_app
from square.utilities.webhooks_helper import is_valid_webhook_event_signature
from src.utils.api_utils import get_gender
from src.utils.campfire_utils import send_message
from src.api.utils.ip_validator import check_allowed_ip
import requests
import logging
import traceback
from src.api.utils.db_utils_customers import (
    create_customer,
    check_email_exists,
    update_latepoint_customer,
    update_square_customer,
    validate_latepoint_customer,
    validate_square_customer,
    determine_customer_type
)

logger = logging.getLogger(__name__)

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")


@customers_bp.route("/new/latepoint", methods=["POST"])
def create_or_update_latepoint_customer():
    is_allowed, response = check_allowed_ip(request, 'latepoint')
    if not is_allowed:
        return response

    try:
        # Parse incoming request data
        data = request.form
        logger.info(f"Received LatePoint customer data: {data}")

        # Extract and validate required fields
        latepoint_id = data.get("id")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        full_name = data.get("full_name")
        email = data.get("email")
        phone = data.get("phone")
        source = "latepoint"

        if not all([latepoint_id, first_name, last_name, full_name, email, phone]):
            return jsonify({"error": "Missing required customer fields"}), 400

        # Validate phone number (must start with +44)
        if not phone.startswith("+44"):
            return jsonify({"error": "Invalid phone number format"}), 400

        # Determine gender from first name using Gender API
        gender = get_gender(first_name)

        # Determine customer type based on email
        customer_type = determine_customer_type(email)
        logger.info(f"Determined customer type for {email}: {customer_type}")

        # Set the default status to 'active'
        status = "active"

        # Prepare customer data
        customer = {
            "latepoint_id": latepoint_id,
            "square_id": None,
            "first_name": first_name,
            "last_name": last_name,
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "gender": gender,
            "status": status,
            "type": customer_type,
            "is_pregnant": data.get('custom_fields[cf_uSnk1aJv]') == "on",
            "has_cancer": data.get('custom_fields[cf_ku8f8Fd8]') == "on",
            "has_blood_clots": data.get('custom_fields[cf_i6npNsJK]') == "on",
            "has_infectious_disease": data.get('custom_fields[cf_LICrcXyq]') == "on",
            "has_bp_issues": data.get('custom_fields[cf_sIG5JoOc]') == "on",
            "has_severe_pain": data.get('custom_fields[cf_R5ffCcvB]') == "on",
            "customer_notes": data.get('custom_fields[cf_AYXmttXr]'),
            "newsletter_signup": data.get('custom_fields[cf_13R2jN9C]') == "on",
            "accepted_terms": data.get('custom_fields[cf_xGQSo978]') == "on",
            "source": source
        }

        logger.info(f"Processing customer data: {customer}")

        # Validate customer data
        if not validate_latepoint_customer(customer):
            return jsonify({"error": "Missing required Latepoint customer fields"}), 400

        # Check if customer exists
        customer_exists = check_email_exists(email)

        if customer_exists:
            # Update existing customer
            logger.info(f"Updating existing customer with Latepoint data: {email}")
            customer_id = update_latepoint_customer(customer)
            message = "Customer updated successfully with Latepoint data"
        else:
            # Create new customer
            logger.info(f"Creating new Latepoint customer: {email}")
            customer_id = create_customer(customer)

            # Post a message to Campfire only for new customers
            try:
                message = f"🎉 New LatePoint Customer: {full_name} ({email}) just signed up!"

                if current_app.config["FLASK_ENV"] != "development":
                    status, response = send_message("studio", message)
                    logger.info(f"Campfire Response: Status {status}, Body: {response}")

            except Exception as e:
                logger.error(f"Failed to notify Studio: {str(e)}")
                return jsonify({"error": f"Failed to notify Studio"}), 500

            message = "Customer created successfully"

            # Check if the customer opted for newsletter signup
            if customer["newsletter_signup"]:
                try:
                    # ConvertKit API endpoint for adding a subscriber to a form
                    url = f"https://api.convertkit.com/v3/forms/{current_app.config['CONVERTKIT_CHARLOTTE_FORM_ID']}/subscribe"

                    # Create subscriber data
                    subscriber_data = {
                        "api_key": current_app.config["CONVERTKIT_API_KEY"],
                        "email": email,
                        "first_name": first_name,
                        "fields": {
                            "last_name": last_name
                        }
                    }

                    # Send POST request to add subscriber to the form
                    headers = {
                        "Content-Type": "application/json"
                    }
                    response = requests.post(url, json=subscriber_data, headers=headers)

                    # Check the response status
                    if response.status_code == 200:
                        logger.info(
                            f"Successfully added {email} to ConvertKit form: {current_app.config['CONVERTKIT_CHARLOTTE_FORM_ID']}")
                    else:
                        logger.error(
                            f"Failed to add {email} to ConvertKit form: {current_app.config['CONVERTKIT_CHARLOTTE_FORM_ID']}. Status Code: {response.status_code}")
                        logger.error(f"Response Content: {response.text}")

                except Exception as e:
                    logger.error(f"Error adding {email} to ConvertKit: {str(e)}")

        # Return success response
        return jsonify({
            "id": customer_id,
            "message": message,
            "action": "updated" if customer_exists else "created"
        }), 200

    except KeyError as e:
        logger.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        logger.error("An unexpected error occurred:\n%s", traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred"}), 500


@customers_bp.route("/new/square", methods=["POST"])
def create_or_update_square_customer():
    try:
        # Parse incoming JSON data
        data = request.get_json()
        logger.info(f"Received data: {data}")

        # Extract the signature from the request headers
        square_signature = request.headers.get('x-square-hmacsha256-signature')

        # Validate the signature
        is_from_square = is_valid_webhook_event_signature(
            request.data.decode('utf-8'),
            square_signature,
            current_app.config['SQUARE_NEW_CUSTOMER_SIGNATURE_KEY'],
            current_app.config['SQUARE_NEW_CUSTOMER_NOTIFICATION_URL']
        )

        if not is_from_square:
            logger.warning("Invalid Square signature")
            return jsonify({"error": "Invalid signature"}), 403

        # Extract and validate required fields
        square_id = data["data"]["object"]["customer"]["id"]
        first_name = data["data"]["object"]["customer"]["given_name"]
        last_name = data["data"]["object"]["customer"]["family_name"]
        email = data["data"]["object"]["customer"]["email_address"]
        phone = data["data"]["object"]["customer"].get("phone_number", "")
        address = data["data"]["object"]["customer"].get("address", {})
        location = address.get("locality")
        postcode = address.get("postal_code")
        source = "square"

        # Determine gender from first name using Gender API
        gender = get_gender(first_name)

        # Determine customer type based on email
        customer_type = determine_customer_type(email)
        logger.info(f"Determined customer type for {email}: {customer_type}")

        # Prepare customer data
        customer = {
            "latepoint_id": None,
            "square_id": square_id,
            "first_name": first_name,
            "last_name": last_name,
            "gender": gender,
            "email": email,
            "phone": phone,
            "location": location,
            "postcode": postcode,
            "status": "active",
            "type": customer_type,
            "newsletter_signup": False,
            "accepted_terms": False,
            "source": source
        }

        # Validate customer data
        if not validate_square_customer(customer):
            return jsonify({"error": "Missing required Square customer fields"}), 400

        # Check if customer exists
        customer_exists = check_email_exists(email)

        if customer_exists:
            # Update existing customer with Square ID only
            logger.info(f"Updating existing customer with Square ID: {email}")
            customer_id = update_square_customer(customer)
            message = "Customer updated successfully with Square ID"
        else:
            # Create new customer
            logger.info(f"Creating new Square customer: {email}")
            customer_id = create_customer(customer)
            message = "Customer created successfully"

            # Add customer to the newsletter (auto opt-in)
            try:
                # ConvertKit API endpoint for adding a subscriber to a form
                url = f"https://api.convertkit.com/v3/forms/{current_app.config['CONVERTKIT_MILLS_FORM_ID']}/subscribe"

                # Create subscriber data
                subscriber_data = {
                    "api_key": current_app.config["CONVERTKIT_API_KEY"],
                    "email": email,
                    "first_name": first_name,
                    "fields": {
                        "last_name": last_name
                    }
                }

                # Send POST request to add subscriber to the form
                headers = {
                    "Content-Type": "application/json"
                }
                response = requests.post(url, json=subscriber_data, headers=headers)

                # Check the response status
                if response.status_code == 200:
                    logger.info(
                        f"Successfully added {email} to ConvertKit form: {current_app.config['CONVERTKIT_MILLS_FORM_ID']}")
                else:
                    logger.error(
                        f"Failed to add {email} to ConvertKit form: {current_app.config['CONVERTKIT_MILLS_FORM_ID']}. Status Code: {response.status_code}")
                    logger.error(f"Response Content: {response.text}")

            except Exception as e:
                logger.error(f"Error adding {email} to ConvertKit: {str(e)}")

            # Post a message to Campfire only for new customers
            try:
                message = f"🎉 New Square Customer: {first_name} {last_name} ({email}) just signed up!"

                if current_app.config["FLASK_ENV"] != "development":
                    status, response = send_message("studio", message)
                    logger.info(f"Campfire Response: Status {status}, Body: {response}")

            except Exception as e:
                logger.error(f"Failed to notify Studio: {str(e)}")
                return jsonify({"error": f"Failed to notify Studio"}), 500

        # Return success response
        return jsonify({
            "id": customer_id,
            "message": message,
            "action": "updated" if customer_exists else "created"
        }), 200

    except KeyError as e:
        logger.error(f"Missing key: {str(e)}")
        return jsonify({"error": f"Missing key: {str(e)}"}), 400
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500