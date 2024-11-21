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
        data = request.form.to_dict()

        # Construct JSON structure
        order = {
            "id": data.get('id'),
            "confirmation_code": data.get('confirmation_code'),
            "customer_comment": None,
            "status": data.get('status'),
            "fulfillment_status": data.get('fulfillment_status'),
            "payment_status": data.get('payment_status'),
            "source_id": None,
            "source_url": data.get('source_url'),
            "total": data.get('total'),
            "subtotal": data.get('subtotal'),
            "created_datetime": data.get('created_datetime'),
            "customer": {
                "id": data.get('customer[id]'),
                "first_name": data.get('customer[first_name]'),
                "last_name": data.get('customer[last_name]'),
                "full_name": data.get('customer[full_name]'),
                "email": data.get('customer[email]'),
                "phone": data.get('customer[phone]'),
                "custom_fields": {
                    "cf_uSnk1aJv": data.get('customer[custom_fields][cf_uSnk1aJv]'),
                    "cf_ku8f8Fd8": data.get('customer[custom_fields][cf_ku8f8Fd8]'),
                    "cf_i6npNsJK": data.get('customer[custom_fields][cf_i6npNsJK]'),
                    "cf_LICrcXyq": data.get('customer[custom_fields][cf_LICrcXyq]'),
                    "cf_sIG5JoOc": data.get('customer[custom_fields][cf_sIG5JoOc]'),
                    "cf_R5ffCcvB": data.get('customer[custom_fields][cf_R5ffCcvB]'),
                    "cf_AYXmttXr": data.get('customer[custom_fields][cf_AYXmttXr]'),
                    "cf_13R2jN9C": data.get('customer[custom_fields][cf_13R2jN9C]'),
                    "cf_xGQSo978": data.get('customer[custom_fields][cf_xGQSo978]')
                }
            },
            "transactions": [{
                "id": data.get('transactions[0][id]'),
                "order_id": data.get('transactions[0][order_id]'),
                "token": data.get('transactions[0][token]'),
                "customer_id": data.get('transactions[0][customer_id]'),
                "processor": data.get('transactions[0][processor]'),
                "payment_method": data.get('transactions[0][payment_method]'),
                "status": data.get('transactions[0][status]'),
                "amount": data.get('transactions[0][amount]')
            }] if data.get('transactions[0][id]') else [],
            "order_items": [{
                "id": data.get('order_items[0][id]'),
                "variant": data.get('order_items[0][variant]'),
                "subtotal": data.get('order_items[0][subtotal]'),
                "total": data.get('order_items[0][total]'),
                "item_data": {
                    "id": data.get('order_items[0][item_data][id]'),
                    "booking_code": data.get('order_items[0][item_data][booking_code]'),
                    "start_datetime": data.get('order_items[0][item_data][start_datetime]'),
                    "end_datetime": data.get('order_items[0][item_data][end_datetime]'),
                    "service_name": data.get('order_items[0][item_data][service_name]'),
                    "duration": data.get('order_items[0][item_data][duration]'),
                    "status": data.get('order_items[0][item_data][status]'),
                    "start_date": data.get('order_items[0][item_data][start_date]'),
                    "start_time": data.get('order_items[0][item_data][start_time]'),
                    "timezone": data.get('order_items[0][item_data][timezone]'),
                    "agent": {
                        "id": data.get('order_items[0][item_data][agent][id]'),
                        "full_name": data.get('order_items[0][item_data][agent][full_name]'),
                        "email": data.get('order_items[0][item_data][agent][email]'),
                        "phone": data.get('order_items[0][item_data][agent][phone]')
                    }
                }
            }]
        }

        # Add coupon if it exists
        if data.get('coupon[coupon_code]'):
            order["coupon"] = {
                "coupon_code": data.get('coupon[coupon_code]'),
                "coupon_discount": data.get('coupon[coupon_discount]')
            }

        logger.debug(f"Formatted Order Data: {order}")
        return jsonify({"message": "Order received", "data": order}), 200

    except Exception as e:
        logger.error(f"Error processing order: {str(e)}")
        return jsonify({"error": "Failed to process order"}), 500
