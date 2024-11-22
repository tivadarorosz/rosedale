from src.services.notification_service import NotificationService
from flask import Blueprint, request, jsonify, current_app
import json
from src.services.customers import CustomerService
from square.utilities.webhooks_helper import is_valid_webhook_event_signature
from src.utils.gender_api import get_gender
from src.core.integrations.convertkit import subscribe_user, ConvertKitError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.core.monitoring import handle_error
from src.api.middleware.validation_middleware import (
    validate_latepoint_request,
    validate_square_request
)

import logging

logger = logging.getLogger(__name__)

# Define the blueprint
customers_bp = Blueprint("customers", __name__)

@customers_bp.route("/latepoint/new", methods=["POST"])
@validate_latepoint_request
def latepoint_new_customer():
    try:

        data = request.form.to_dict()
        custom_fields = json.loads(data.get("custom_fields", "{}"))

        # Prepare customer data (validation already done by middleware)
        customer_data = {
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
            "booking_system_id": data["id"],
            "session_preferences": {
                "medical_conditions": custom_fields.get("cf_fV6mSkLi", "").lower() == "yes",
                "pressure_level": custom_fields.get("cf_BUQVMrtE", ""),
                "session_preference": custom_fields.get("cf_MYTGXxFc", ""),
                "music_preference": custom_fields.get("cf_aMKSBozK", ""),
                "aromatherapy_preference": custom_fields.get("cf_71gt8Um4", ""),
                "referral_source": custom_fields.get("cf_OXZkZKUw", ""),
                "email_subscribed": False
            }
        }

        # Check for existing customer
        existing_customer = CustomerService.get_customer_by_email(customer_data["email"])
        if existing_customer:
            updated_customer = CustomerService.update_latepoint_customer(
                existing_customer.id,
                customer_data
            )
            return jsonify({
                "message": "Customer updated successfully",
                "action": "updated",
                "id": updated_customer.id
            }), 200

        # Create new customer
        new_customer = CustomerService.create_latepoint_customer(customer_data)

        # Notify Campfire about new customer
        message = f"🎉 New LatePoint Customer: {new_customer.first_name} {new_customer.last_name} ({new_customer.email}) just signed up!"
        NotificationService.notify_campfire(message, "studio")

        return jsonify({
            "message": "Customer created successfully",
            "action": "created",
            "id": new_customer.id
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except IntegrityError:
        return jsonify({"error": "Customer already exists"}), 409
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        handle_error(e, "Unexpected error processing LatePoint webhook")
        return jsonify({"error": "Internal server error"}), 500


@customers_bp.route("/square/new", methods=["POST"])
@validate_square_request
def square_customer_webhook():
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