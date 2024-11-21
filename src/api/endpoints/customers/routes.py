from flask import Blueprint, request, jsonify, current_app
from square.utilities.webhooks_helper import is_valid_webhook_event_signature
from src.utils.api_utils import get_gender
from src.utils.campfire_utils import send_message
from src.api.utils.ip_validator import check_allowed_ip
from src.api.middleware.validation_middleware import (
    validate_latepoint_request,
    validate_square_request
)
from services.customers import (
    create_customer,
    email_exists,
    update_customer,
    determine_customer_type
)
import requests
import logging

logger = logging.getLogger(__name__)
customers_bp = Blueprint("customers", __name__, url_prefix="/customers")


def notify_campfire(name: str, email: str, source: str) -> None:
    """Send notification to Campfire about new customer."""
    try:
        message = f"🎉 New {source.title()} Customer: {name} ({email}) just signed up!"
        if current_app.config["FLASK_ENV"] != "development":
            status, response = send_message("studio", message)
            logger.info(f"Campfire Response: Status {status}, Body: {response}")
    except Exception as e:
        logger.error(f"Failed to notify Studio: {str(e)}")
        # Don't raise the error - we don't want to fail the customer creation


def subscribe_to_convertkit(email: str, first_name: str, last_name: str, form_id: str) -> None:
    """Subscribe customer to ConvertKit."""
    try:
        url = f"https://api.convertkit.com/v3/forms/{form_id}/subscribe"
        subscriber_data = {
            "api_key": current_app.config["CONVERTKIT_API_KEY"],
            "email": email,
            "first_name": first_name,
            "fields": {"last_name": last_name}
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=subscriber_data, headers=headers)

        if response.status_code == 200:
            logger.info(f"Successfully added {email} to ConvertKit form: {form_id}")
        else:
            logger.error(f"Failed to add {email} to ConvertKit. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error adding {email} to ConvertKit: {str(e)}")
        # Don't raise the error - we don't want to fail the customer creation


@customers_bp.route("/new/latepoint", methods=["POST"])
@validate_latepoint_request
def create_or_update_latepoint_customer():
    """Handle new customer creation/update from LatePoint."""
    is_allowed, response = check_allowed_ip(request, 'latepoint')
    if not is_allowed:
        return response

    try:
        data = request.form
        logger.info(f"Received LatePoint customer data: {data}")

        # Prepare customer data
        customer_data = {
            "latepoint_id": data.get("id"),
            "square_id": None,
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "email": data.get("email"),
            "phone": data.get("phone"),
            "gender": get_gender(data.get("first_name")),
            "status": "active",
            "type": determine_customer_type(data.get("email")),
            "source": "latepoint",
            "is_pregnant": data.get('custom_fields[cf_uSnk1aJv]') == "on",
            "has_cancer": data.get('custom_fields[cf_ku8f8Fd8]') == "on",
            "has_blood_clots": data.get('custom_fields[cf_i6npNsJK]') == "on",
            "has_infectious_disease": data.get('custom_fields[cf_LICrcXyq]') == "on",
            "has_bp_issues": data.get('custom_fields[cf_sIG5JoOc]') == "on",
            "has_severe_pain": data.get('custom_fields[cf_R5ffCcvB]') == "on",
            "newsletter_subscribed": data.get('custom_fields[cf_13R2jN9C]') == "on",
            "accepted_terms": data.get('custom_fields[cf_xGQSo978]') == "on"
        }

        customer_exists = email_exists(customer_data["email"])

        if customer_exists:
            # Update existing customer
            success, error = update_customer(customer_data)
            if error:
                return jsonify({"error": error}), 400

            return jsonify({
                "message": "Customer updated successfully with Latepoint data",
                "action": "updated"
            }), 200

        # Create new customer
        customer_id, error = create_customer(customer_data)
        if error:
            return jsonify({"error": error}), 400

        # Notify about new customer
        notify_campfire(
            f"{customer_data['first_name']} {customer_data['last_name']}",
            customer_data['email'],
            "LatePoint"
        )

        # Handle newsletter signup
        if customer_data["newsletter_subscribed"]:
            subscribe_to_convertkit(
                customer_data["email"],
                customer_data["first_name"],
                customer_data["last_name"],
                current_app.config['CONVERTKIT_CHARLOTTE_FORM_ID']
            )

        return jsonify({
            "id": customer_id,
            "message": "Customer created successfully",
            "action": "created"
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500


@customers_bp.route("/new/square", methods=["POST"])
@validate_square_request
def create_or_update_square_customer():
    """Handle new customer creation/update from Square."""
    try:
        data = request.get_json()
        logger.info(f"Received Square customer data: {data}")

        # Validate Square signature
        square_signature = request.headers.get('x-square-hmacsha256-signature')
        is_from_square = is_valid_webhook_event_signature(
            request.data.decode('utf-8'),
            square_signature,
            current_app.config['SQUARE_NEW_CUSTOMER_SIGNATURE_KEY'],
            current_app.config['SQUARE_NEW_CUSTOMER_NOTIFICATION_URL']
        )

        if not is_from_square:
            logger.warning("Invalid Square signature")
            return jsonify({"error": "Invalid signature"}), 403

        customer = data["data"]["object"]["customer"]

        # Prepare customer data
        customer_data = {
            "square_id": customer["id"],
            "first_name": customer["given_name"],
            "last_name": customer["family_name"],
            "email": customer["email_address"],
            "phone": customer.get("phone_number", ""),
            "location": customer.get("address", {}).get("locality"),
            "postcode": customer.get("address", {}).get("postal_code"),
            "gender": get_gender(customer["given_name"]),
            "status": "active",
            "type": determine_customer_type(customer["email_address"]),
            "source": "square",
            "newsletter_subscribed": False,
            "accepted_terms": True
        }

        customer_exists = email_exists(customer_data["email"])

        if customer_exists:
            # Update existing customer
            success, error = update_customer(customer_data)
            if error:
                return jsonify({"error": error}), 400

            return jsonify({
                "message": "Customer updated successfully with Square ID",
                "action": "updated"
            }), 200

        # Create new customer
        customer_id, error = create_customer(customer_data)
        if error:
            return jsonify({"error": error}), 400

        # Auto subscribe to newsletter
        subscribe_to_convertkit(
            customer_data["email"],
            customer_data["first_name"],
            customer_data["last_name"],
            current_app.config['CONVERTKIT_MILLS_FORM_ID']
        )

        # Notify about new customer
        notify_campfire(
            f"{customer_data['first_name']} {customer_data['last_name']}",
            customer_data['email'],
            "Square"
        )

        return jsonify({
            "id": customer_id,
            "message": "Customer created successfully",
            "action": "created"
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500