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

orders_bp = Blueprint("orders", __name__, url_prefix="/orders")

# CONVERTKIT_API_KEY = os.getenv("CONVERTKIT_API_KEY")
# CHARLOTTE_FORM_ID = os.getenv("CONVERTKIT_CHARLOTTE_FORM_ID")
# MILLS_FORM_ID = os.getenv("CONVERTKIT_MILLS_FORM_ID")

@orders_bp.route("/new/latepoint", methods=["POST"])
def create_latepoint_order():

    # Parse incoming request data
    # data = request.form

    # Convert form data to dictionary
    form_data = request.form.to_dict()
    # Print the entire data
    print("Request Data:", form_data)
    logger.info(f"Received LatePoint order data: {form_data}")
    return "Data printed to console", 200
