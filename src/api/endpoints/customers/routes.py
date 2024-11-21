from flask import Blueprint, request, jsonify, current_app
from square.utilities.webhooks_helper import is_valid_webhook_event_signature
from src.core.integrations.gender_api import get_gender
from src.core.integrations.campfire import send_message
from src.core.integrations.convertkit import subscribe_user, ConvertKitError
from src.api.validators.ip_validator import check_allowed_ip
from src.api.middleware.validation_middleware import (
    validate_latepoint_request,
    validate_square_request
)
from services.customers import (
    create_customer,
    email_exists,
    update_latepoint_customer,
    update_square_customer,
    determine_customer_type
)

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
            success, error = update_latepoint_customer(customer_data)
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

        # Subscribe to ConvertKit
        if customer_data.get("newsletter_subscribed"):
            try:
                ck_api_key = current_app.config["CONVERTKIT_API_KEY"]
                ck_form_id = current_app.config["CONVERTKIT_CHARLOTTE_FORM_ID"]
                ck_email = customer_data["email"]
                ck_first_name = customer_data["first_name"]

                # Subscribe using the external module
                subscribe_user(ck_api_key, ck_form_id, ck_email, ck_first_name)
                logger.info(f"Successfully subscribed {ck_email} to ConvertKit form {ck_form_id}.")
            except ConvertKitError as e:
                logger.error(f"ConvertKit subscription failed for {ck_email}: {str(e)}")
                # Log the error, but do not block the customer creation process

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
            success, error = update_square_customer(customer_data)
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

        # Auto-Subscribe to newsletter
        if customer_data.get("newsletter_subscribed"):
            try:
                ck_api_key = current_app.config["CONVERTKIT_API_KEY"]
                ck_form_id = current_app.config["CONVERTKIT_MILLS_FORM_ID"]
                ck_email = customer_data["email"]
                ck_first_name = customer_data["first_name"]

                # Subscribe using the external module
                subscribe_user(ck_api_key, ck_form_id, ck_email, ck_first_name)
                logger.info(f"Successfully subscribed {ck_email} to ConvertKit form {ck_form_id}.")
            except ConvertKitError as e:
                logger.error(f"ConvertKit subscription failed for {ck_email}: {str(e)}")
                # Log the error, but do not block the customer creation process

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