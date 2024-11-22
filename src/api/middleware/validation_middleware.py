from functools import wraps
from flask import request, jsonify
import json
import logging
from src.api.validators.customer_validators import CustomerValidator
from src.api.validators.ip_validator import check_allowed_ip
from src.core.monitoring import handle_error

logger = logging.getLogger(__name__)


def validate_latepoint_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # IP validation
            is_allowed, response = check_allowed_ip(request, 'latepoint')
            if not is_allowed:
                return response

            data = request.form.to_dict()

            # Parse custom fields if present
            if "custom_fields" in data:
                try:
                    data["custom_fields"] = json.loads(data["custom_fields"])
                except json.JSONDecodeError:
                    logger.error("Invalid custom fields JSON format")
                    return jsonify({
                        "error": "Invalid custom fields format",
                        "status": "validation_error"
                    }), 400

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
            handle_error(e, "Validation error in LatePoint webhook")
            return jsonify({
                "error": "Invalid request data",
                "status": "validation_error"
            }), 400

    return decorated_function


def validate_square_request(f):
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
            handle_error(e, "Validation error in Square webhook")
            return jsonify({
                "error": "Invalid request data",
                "status": "validation_error"
            }), 400

    return decorated_function