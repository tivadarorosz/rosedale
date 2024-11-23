import os
import logging
import traceback
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from functools import wraps
from flask import request
from src.core.integrations.campfire import send_message

logger = logging.getLogger(__name__)


def initialize_sentry():
    """Initialize Sentry for error monitoring."""
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.2 if debug_mode else 1.0,  # Lower sampling rate in debug mode
        environment=os.getenv("FLASK_ENV", "production"),
        debug=debug_mode  # Enable verbose output in development
    )
    if debug_mode:
        logger.info("Sentry initialized in debug mode with reduced sample rate.")


def format_error_message(error, extra_info=None):
    """Format error message for Campfire."""
    message = f"🚨 Application Error\n\n"
    if extra_info:
        message += f"Context: {extra_info}\n\n"
    message += f"Error Type: {type(error).__name__}\n"
    message += f"Error Message: {str(error)}\n\n"

    # Add stack trace (truncate if too long)
    stack_trace = traceback.format_exc()
    if len(stack_trace) > 500:  # Truncate long traces
        stack_trace = stack_trace[:500] + "...(truncated)"
    message += f"Stack Trace:\n{stack_trace}"

    return message


def handle_error(error, extra_info=None):
    """
    Send error to both Sentry and Campfire.
    Only critical errors are sent to Campfire.
    """
    try:
        # Format the error message
        message = format_error_message(error, extra_info)

        # Log locally
        logger.error(message)

        # Send to Sentry
        sentry_sdk.capture_exception(error)

        # Notify Campfire only for critical errors
        if isinstance(error, (ValueError, KeyError, RuntimeError)):
            try:
                status, response = send_message("alert", message)
                logger.info(f"Error notification sent to Campfire. Status: {status}")
            except Exception as e:
                logger.error(f"Failed to send error to Campfire: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to handle error notification: {str(e)}")


def capture_errors(extra_info=None):
    """
    Decorator to capture and report errors in routes or functions.

    Args:
        extra_info (str): Additional context to include in the error message.

    Returns:
        func: A wrapped function with error handling.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as error:
                handle_error(error, extra_info=extra_info or f"Request path: {request.path}")
                return {"error": "Internal server error. The issue has been reported."}, 500
        return wrapper
    return decorator