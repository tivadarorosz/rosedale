from functools import wraps
from flask import request, jsonify
from app.api.validators.customer_validators import CustomerValidator
import logging

logger = logging.getLogger(__name__)


def validate_latepoint_request(f):
    """Middleware to validate LatePoint customer requests."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = request.form.to_dict()
            valid, error = CustomerValidator.validate_latepoint_data(data)

            if not valid:
                logger.warning(f"Invalid LatePoint request data: {error}")
                return jsonify({
                    "error": error,
                    "status": "validation_error"
                }), 400

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error validating LatePoint request: {str(e)}")
            return jsonify({
                "error": "Invalid request data",
                "status": "validation_error"
            }), 400

    return decorated_function


def validate_square_request(f):
    """Middleware to validate Square customer requests."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = request.get_json()
            valid, error = CustomerValidator.validate_square_data(data)

            if not valid:
                logger.warning(f"Invalid Square request data: {error}")
                return jsonify({
                    "error": error,
                    "status": "validation_error"
                }), 400

            return f(*args, **kwargs)

        except Exception as e:
            logger.error(f"Error validating Square request: {str(e)}")
            return jsonify({
                "error": "Invalid request data",
                "status": "validation_error"
            }), 400

    return decorated_function