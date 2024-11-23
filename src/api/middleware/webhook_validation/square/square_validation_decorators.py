from functools import wraps
from flask import request, jsonify, current_app
from square.utilities.webhooks_helper import is_valid_webhook_event_signature
from .square_customer_webhook_validation import SquareCustomerWebhookValidator

def validate_square_customer_webhook(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the Square signature from headers
        square_signature = request.headers.get('x-square-hmacsha256-signature')

        # Validate the Square signature
        is_from_square = is_valid_webhook_event_signature(
            request.data.decode("utf-8"),
            square_signature,
            current_app.config["SQUARE_NEW_CUSTOMER_SIGNATURE_KEY"],
            current_app.config["SQUARE_NEW_CUSTOMER_NOTIFICATION_URL"],
        )
        if not is_from_square:
            return jsonify({"error": "Invalid signature"}), 403

        # Extract the payload
        data = request.get_json()["data"]["object"]["customer"]

        # Validate the payload using the validator
        is_valid, error_message = SquareCustomerWebhookValidator.validate_customer_payload(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400

        # Proceed to the main function
        return func(*args, **kwargs)

    return wrapper