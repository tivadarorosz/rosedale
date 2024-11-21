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
        form_data = request.form.to_dict()

        # Create order structure
        order = {
            "id": form_data.get('id'),
            "confirmation_code": form_data.get('confirmation_code'),
            "status": form_data.get('status'),
            "fulfillment_status": form_data.get('fulfillment_status'),
            "payment_status": form_data.get('payment_status'),
            "source_url": form_data.get('source_url', ""),
            "total": form_data.get('total'),
            "subtotal": form_data.get('subtotal'),
            "created_datetime": form_data.get('created_datetime'),
            "customer": {
                "id": form_data.get('customer[id]'),
                "first_name": form_data.get('customer[first_name]'),
                "last_name": form_data.get('customer[last_name]'),
                "full_name": form_data.get('customer[full_name]'),
                "email": form_data.get('customer[email]'),
                "phone": form_data.get('customer[phone]'),
                "custom_fields": {
                    "cf_uSnk1aJv": form_data.get('customer[custom_fields][cf_uSnk1aJv]'),
                    "cf_ku8f8Fd8": form_data.get('customer[custom_fields][cf_ku8f8Fd8]'),
                    "cf_i6npNsJK": form_data.get('customer[custom_fields][cf_i6npNsJK]'),
                    "cf_LICrcXyq": form_data.get('customer[custom_fields][cf_LICrcXyq]'),
                    "cf_sIG5JoOc": form_data.get('customer[custom_fields][cf_sIG5JoOc]'),
                    "cf_R5ffCcvB": form_data.get('customer[custom_fields][cf_R5ffCcvB]'),
                    "cf_AYXmttXr": form_data.get('customer[custom_fields][cf_AYXmttXr]'),
                    "cf_13R2jN9C": form_data.get('customer[custom_fields][cf_13R2jN9C]'),
                    "cf_xGQSo978": form_data.get('customer[custom_fields][cf_xGQSo978]')
                }
            },
            "transactions": [],
            "order_items": [
                {
                    "id": form_data.get('order_items[0][id]'),
                    "variant": form_data.get('order_items[0][variant]'),
                    "subtotal": form_data.get('order_items[0][subtotal]'),
                    "total": form_data.get('order_items[0][total]'),
                    "item_data": {
                        "id": form_data.get('order_items[0][item_data][id]'),
                        "booking_code": form_data.get('order_items[0][item_data][booking_code]'),
                        "start_datetime": form_data.get('order_items[0][item_data][start_datetime]'),
                        "end_datetime": form_data.get('order_items[0][item_data][end_datetime]'),
                        "service_name": form_data.get('order_items[0][item_data][service_name]'),
                        "duration": form_data.get('order_items[0][item_data][duration]'),
                        "status": form_data.get('order_items[0][item_data][status]'),
                        "start_date": form_data.get('order_items[0][item_data][start_date]'),
                        "start_time": form_data.get('order_items[0][item_data][start_time]'),
                        "timezone": form_data.get('order_items[0][item_data][timezone]'),
                        "agent": {
                            "id": form_data.get('order_items[0][item_data][agent][id]'),
                            "full_name": form_data.get('order_items[0][item_data][agent][full_name]'),
                            "email": form_data.get('order_items[0][item_data][agent][email]'),
                            "phone": form_data.get('order_items[0][item_data][agent][phone]')
                        }
                    }
                }
            ]
        }

        # Add transactions if they exist
        if form_data.get('transactions[0][id]'):
            order['transactions'] = [{
                "id": form_data.get('transactions[0][id]'),
                "order_id": form_data.get('transactions[0][order_id]'),
                "token": form_data.get('transactions[0][token]'),
                "customer_id": form_data.get('transactions[0][customer_id]'),
                "processor": form_data.get('transactions[0][processor]'),
                "payment_method": form_data.get('transactions[0][payment_method]'),
                "payment_portion": form_data.get('transactions[0][payment_portion]'),
                "kind": form_data.get('transactions[0][kind]'),
                "status": form_data.get('transactions[0][status]'),
                "amount": form_data.get('transactions[0][amount]')
            }]

        # Log the entire structured order
        logger.info(f"Complete Order Data: {order}")

        return jsonify(order), 200

    except Exception as e:
        logger.error(f"Error processing order: {str(e)}")
        return jsonify({"error": "Failed to process order"}), 500
