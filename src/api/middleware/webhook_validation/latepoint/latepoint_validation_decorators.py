from functools import wraps
from flask import request, jsonify
from .latepoint_customer_webhook_validation import LatePointCustomerWebhookValidator

def validate_latepoint_customer_webhook(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract data
        data = request.form.to_dict() # request.json or  for Square

        # Validate payload
        is_valid, error_message = LatePointCustomerWebhookValidator.validate_customer_payload(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        return func(*args, **kwargs)

    return wrapper