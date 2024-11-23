from flask import Blueprint, request, jsonify, current_app
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

# Utility for sending notifications
def notify_new_customer(platform, first_name, last_name, email):
    message = f"🎉 New {platform} Customer: {first_name} {last_name} ({email}) just signed up!"
    NotificationService.notify_campfire(message, "studio")


@customers_bp.route("/latepoint/new", methods=["POST"])
@capture_errors(extra_info="LatePoint Customer Webhook Error")
@validate_request_ip
@rate_limit(limit=20, window=60)
@log_webhook_request
@validate_latepoint_customer_webhook
def handle_latepoint_customer_webhook():
    """
    Handles incoming customer creation or update requests from LatePoint.
    """
    try:
        # Parse the payload
        data = request.form.to_dict()
        custom_fields = CustomerDataProcessor.parse_custom_fields(data.get("custom_fields", "{}"))
        customer_data = CustomerDataProcessor.extract_core_customer_data(data, source="LatePoint")
        customer_data["session_preferences"] = CustomerDataProcessor.build_session_preferences(custom_fields)
        customer_data["gender_identity"] = get_gender(data.get("first_name", ""))

        # Check if the customer already exists
        existing_customer = CustomerService.get_customer_by_email(customer_data["email"])
        if existing_customer:
            updated_customer = CustomerService.update_customer(existing_customer.id, customer_data)
            return jsonify({
                "message": "Customer updated successfully",
                "action": "updated",
                "id": updated_customer.id,
            }), 200

        # Create a new customer
        new_customer = CustomerService.create_customer(customer_data)

        # Notify about the new customer
        notify_new_customer("LatePoint", new_customer.first_name, new_customer.last_name, new_customer.email)

        return jsonify({
            "message": "Customer created successfully",
            "action": "created",
            "id": new_customer.id,
        }), 200

    except IntegrityError:
        return jsonify({"error": "Customer already exists"}), 409
    except SQLAlchemyError:
        return jsonify({"error": "Database error"}), 500


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
    try:
        # Extract customer data
        customer = request.get_json()["data"]["object"]["customer"]
        customer_data = CustomerDataProcessor.extract_core_customer_data(customer, source="Square")

        # Check if the customer already exists
        existing_customer = CustomerService.get_customer_by_email(customer_data["email"])
        if existing_customer:
            updated_customer = CustomerService.update_customer(existing_customer.id, customer_data)
            return jsonify({
                "message": "Customer updated successfully",
                "action": "updated",
                "id": updated_customer.id,
            }), 200

        # Create a new customer
        new_customer = CustomerService.create_customer(customer_data)

        # Notify about the new customer
        notify_new_customer("Square", new_customer.first_name, new_customer.last_name, new_customer.email)

        return jsonify({
            "message": "Customer created successfully",
            "action": "created",
            "id": new_customer.id,
        }), 200

    except IntegrityError:
        return jsonify({"error": "Customer already exists"}), 409
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error"}), 500