import os
import logging
import traceback
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from src.utils.campfire_utils import send_message

logger = logging.getLogger(__name__)

def initialize_sentry():
    """Initialize Sentry for error monitoring."""
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,  # Adjust as needed
        environment=os.getenv("FLASK_ENV", "production"),
        debug=False  # Disable Sentry-specific debug mode
    )

    # Suppress DEBUG logs from Sentry
    sentry_logger = logging.getLogger("sentry_sdk")
    sentry_logger.setLevel(logging.WARNING)

def format_error_message(error, extra_info=None):
	"""Format error message for Campfire"""
	message = f"🚨 Application Error\n\n"
	if extra_info:
		message += f"Context: {extra_info}\n\n"
	message += f"Error Type: {type(error).__name__}\n"
	message += f"Error Message: {str(error)}\n\n"
	
	# Add stack trace but limit its length
	stack_trace = traceback.format_exc()
	if len(stack_trace) > 500:  # Truncate if too long
		stack_trace = stack_trace[:500] + "...(truncated)"
	message += f"Stack Trace:\n{stack_trace}"
	
	return message

def handle_error(error, extra_info=None):
	"""Send error to both Sentry and Campfire"""
	try:
		# Format the error message
		message = format_error_message(error, extra_info)
		
		# Log locally
		logger.error(message)
		
		# Send to Sentry
		sentry_sdk.capture_exception(error)
		
		try:
			status, response = send_message("alert", message)
			logger.info(f"Error notification sent to Campfire. Status: {status}")
		except Exception as e:
			logger.error(f"Failed to send error to Campfire: {str(e)}")
	except Exception as e:
		logger.error(f"Failed to handle error notification: {str(e)}")