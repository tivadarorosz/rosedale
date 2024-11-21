from flask import Blueprint, request, jsonify
# import os
# from square.utilities.webhooks_helper import is_valid_webhook_event_signature
from src.utils.api_utils import get_gender
# from src.utils.campfire_utils import send_message
# from convertkit import ConvertKit
# import requests
import logging
# import traceback
from src.api.utils.db_utils_customers import (
# 	create_customer,
#	check_email_exists,
#	update_latepoint_customer,
#	update_square_customer,
#	validate_latepoint_customer,
#	validate_square_customer,
	determine_customer_type
)

logger = logging.getLogger(__name__)

orders_bp = Blueprint("orders", __name__)

# CONVERTKIT_API_KEY = os.getenv("CONVERTKIT_API_KEY")
# CHARLOTTE_FORM_ID = os.getenv("CONVERTKIT_CHARLOTTE_FORM_ID")
# MILLS_FORM_ID = os.getenv("CONVERTKIT_MILLS_FORM_ID")

@orders_bp.route("/new/latepoint", methods=["POST"])
def create_latepoint_order():
    try:
        # Parse form data
        data = request.form.to_dict()

        # Log all received data
        logger.info("Received Order Data:")
        logger.info(f"Order ID: {data.get('id')}")
        logger.info(f"Confirmation Code: {data.get('confirmation_code')}")
        logger.info(f"Status: {data.get('status')}")
        logger.info(f"Payment Status: {data.get('payment_status')}")
        logger.info(f"Total: {data.get('total')}")
        logger.info(f"Created: {data.get('created_datetime')}")

        # Log customer details
        logger.info("Customer Details:")
        logger.info(f"Customer ID: {data.get('customer[id]')}")
        logger.info(f"Name: {data.get('customer[full_name]')}")
        logger.info(f"Email: {data.get('customer[email]')}")
        logger.info(f"Phone: {data.get('customer[phone]')}")

        # Log transaction details
        logger.info("Transaction Details:")
        logger.info(f"Transaction ID: {data.get('transactions[0][id]')}")
        logger.info(f"Amount: {data.get('transactions[0][amount]')}")
        logger.info(f"Status: {data.get('transactions[0][status]')}")

        # Log booking details
        logger.info("Booking Details:")
        logger.info(f"Booking Code: {data.get('order_items[0][item_data][booking_code]')}")
        logger.info(f"Service: {data.get('order_items[0][item_data][service_name]')}")
        logger.info(f"Start Time: {data.get('order_items[0][item_data][start_datetime]')}")
        logger.info(f"Agent: {data.get('order_items[0][item_data][agent][full_name]')}")

        return jsonify({"message": "Order data received and logged"}), 200

    except Exception as e:
        logger.error(f"Error processing order: {str(e)}")
        return jsonify({"error": "Failed to process order"}), 500
