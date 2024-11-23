from functools import wraps
from flask import request, jsonify
from .square_customer_webhook_validation import SquareCustomerWebhookValidator

# Square-specific decorators

def validate_square_customer_webhook(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the payload
        data = request.json or request.form.to_dict()

        # Validate the payload using the validator
        is_valid, error_message = SquareCustomerWebhookValidator.validate_customer_payload(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        # Proceed to the main function
        return func(*args, **kwargs)

    return wrapper