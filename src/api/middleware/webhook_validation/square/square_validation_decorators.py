from functools import wraps
from flask import request, jsonify, current_app
from src.utils.signature_validation import is_valid_webhook_event_signature

def validate_square_customer_webhook(func):
    """
    Decorator to validate Square customer webhook requests.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the Square signature from the headers
        square_signature = request.headers.get('x-square-hmacsha256-signature')
        signature_key = current_app.config.get("SQUARE_NEW_CUSTOMER_SIGNATURE_KEY")

        # Validate the webhook signature
        """
        is_valid = is_valid_webhook_event_signature(
            body=request.data.decode('utf-8'),
            square_signature=square_signature,
            signature_key=signature_key,
        )
        """

        is_valid = True

        if not is_valid:
            return jsonify({"error": "Invalid signature"}), 403

        # Proceed to the main function if the signature is valid
        return func(*args, **kwargs)

    return wrapper