from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from src.services.customers import CustomerService
from src.services.notification_service import NotificationService
from src.core.monitoring import capture_errors
from src.core.logger import log_webhook_request
from src.utils.gender_api import get_gender
from src.api.middleware.validation_middleware import validate_request_ip
from src.api.middleware.rate_limit import rate_limit
from src.api.middleware.webhook_validation.latepoint.latepoint_validation_decorators import (
    validate_latepoint_customer_webhook,
)
from src.api.middleware.webhook_validation.square.square_validation_decorators import (
    validate_square_customer_webhook,
)
from src.utils.customer_data_processor import CustomerDataProcessor


# Define the blueprint
customers_bp = Blueprint("customers", __name__)


# Utility for handling customer creation and updates
def process_customer_request(customer_data, platform):
    """
    Handles customer creation or update logic.

    Args:
        customer_data (dict): Customer information.
        platform (str): Platform name (e.g., 'LatePoint', 'Square').

    Returns:
        tuple: JSON response and status code.
    """
    try:
        # Check if the customer already exists
        existing_customer = CustomerService.get_customer_by_email(customer_data["email"])
        fields_to_update = ["first_name", "last_name", "email", "phone_number", "payment_system_id"]
        if existing_customer:
            if platform == "latepoint":
                fields_to_update = ["booking_system_id", "first_name", "last_name", "gender", "massage_preferences"]
            elif platform == "square":
                fields_to_update = ["payment_system_id", "phone_number", "address"]
            updated_customer = CustomerService.update_customer(existing_customer.id, customer_data, fields_to_update)
            return (
                jsonify(
                    {
                        "message": "Customer updated successfully",
                        "action": "updated",
                        "id": updated_customer.id,
                    }
                ),
                200,
            )

        # Create a new customer
        new_customer = CustomerService.create_customer(customer_data)

        # Notify about the new customer
        message = (
            f"🎉 New {platform} Customer: {new_customer.first_name} "
            f"{new_customer.last_name} ({new_customer.email}) just signed up!"
        )
        NotificationService.notify_campfire(message, "studio")

        return (
            jsonify(
                {
                    "message": "Customer created successfully",
                    "action": "created",
                    "id": new_customer.id,
                }
            ),
            200,
        )

    except IntegrityError:
        return jsonify({"error": "Customer already exists"}), 409
    except SQLAlchemyError as db_error:
        return jsonify({"error": f"Database error: {str(db_error)}"}), 500


@customers_bp.route("/latepoint/new", methods=["POST"])
@capture_errors(extra_info="LatePoint Customer Webhook Error")
@validate_request_ip
@rate_limit(limit=20, window=60)
@log_webhook_request
@validate_latepoint_customer_webhook
def handle_latepoint_customer_webhook():
    data = request.form.to_dict()
    custom_fields = CustomerDataProcessor.parse_custom_fields(data.get("custom_fields"))

    customer_data = CustomerDataProcessor.extract_core_customer_data(data, source="latepoint")
    customer_data["massage_preferences"] = CustomerDataProcessor.build_massage_preferences(custom_fields)
    customer_data["gender"] = get_gender(data.get("first_name", ""))

    return process_customer_request(customer_data, platform="latepoint")


@customers_bp.route("/square/new", methods=["POST"])
@capture_errors(extra_info="Square Customer Webhook Error")
@validate_request_ip
@rate_limit(limit=15, window=60)
@log_webhook_request
@validate_square_customer_webhook
def handle_square_customer_webhook():
    """
    Handles incoming customer creation or update requests from Square.
    """
    # Parse the payload
    data = request.get_json()["data"]["object"]["customer"]

    # Build customer data
    customer_data = CustomerDataProcessor.extract_core_customer_data(data, source="square")
    customer_data["gender"] = get_gender(data.get("given_name", ""))

    # Process the customer request
    return process_customer_request(customer_data, platform="square")