import logging
import json
from functools import wraps
from flask import request

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def log_webhook_request(func):
    """
    Decorator to log details of the webhook request and response.

    Logs:
        - Request method
        - Endpoint path
        - Headers
        - Payload (body)
        - Response status and data

    Args:
        func: The function to be decorated.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Log the request details
        try:
            logger.info("Received Webhook Request")
            logger.info(f"Method: {request.method}")
            logger.info(f"Path: {request.path}")
            logger.info(f"Headers: {json.dumps(dict(request.headers), default=str)}")

            # Log the payload (if applicable)
            if request.is_json:
                logger.info(f"Payload: {json.dumps(request.get_json(), default=str)}")
            elif request.form:
                logger.info(f"Form Data: {json.dumps(request.form.to_dict(), default=str)}")
            else:
                logger.info("No payload available")
        except Exception as e:
            logger.warning(f"Failed to log request details: {str(e)}")

        # Execute the decorated function
        response = func(*args, **kwargs)

        # Log the response details
        try:
            if isinstance(response, tuple) and len(response) == 2:
                response_body, status_code = response
                logger.info(f"Response Status: {status_code}")
                logger.info(f"Response Body: {json.dumps(response_body, default=str)}")
            elif isinstance(response, dict):
                logger.info(f"Response: {json.dumps(response, default=str)}")
            else:
                logger.info(f"Response: {response}")
        except Exception as e:
            logger.warning(f"Failed to log response details: {str(e)}")

        return response

    return wrapper