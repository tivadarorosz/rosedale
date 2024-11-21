from flask import Blueprint, request, jsonify
# import os
# from square.utilities.webhooks_helper import is_valid_webhook_event_signature
# from src.utils.api_utils import get_gender
# from src.utils.campfire_utils import send_message
# import requests
import logging
# import traceback
# from src.api.utils.db_utils_customers import (
# 	create_customer,
#	check_email_exists,
#	update_latepoint_customer,
#	update_square_customer,
#	validate_latepoint_customer,
#	validate_square_customer,
# 	determine_customer_type
# )

logger = logging.getLogger(__name__)

orders_bp = Blueprint("orders", __name__)

@orders_bp.before_request
def log_request_info():
    logger.debug(f"Method: {request.method}")
    logger.debug(f"URL: {request.url}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Data: {request.get_data()}")

# CONVERTKIT_API_KEY = os.getenv("CONVERTKIT_API_KEY")
# CHARLOTTE_FORM_ID = os.getenv("CONVERTKIT_CHARLOTTE_FORM_ID")
# MILLS_FORM_ID = os.getenv("CONVERTKIT_MILLS_FORM_ID")

@orders_bp.route("/new/latepoint", methods=["POST"])
def create_latepoint_order():
    try:
        # Parse form data
        # data = request.form.to_dict()

        # Log raw request data
        logger.info("Raw Request Data:")
        logger.info(f"Headers: {dict(request.headers)}")
        logger.info(f"Form Data: {request.form.to_dict()}")
        logger.info(f"JSON Data: {request.get_json(silent=True)}")
        logger.info(f"Raw Data: {request.get_data(as_text=True)}")

        return jsonify({"message": "Order data received and logged"}), 200

    except Exception as e:
        logger.error(f"Error processing order: {str(e)}")
        return jsonify({"error": "Failed to process order"}), 500
