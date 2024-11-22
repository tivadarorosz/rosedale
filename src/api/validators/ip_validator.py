from flask import jsonify
import os
import logging

logger = logging.getLogger(__name__)


def check_allowed_ip(request):
    """
    Check if the request IP is globally whitelisted.

    Args:
        request: Flask request object
    Returns:
        tuple: (bool, response)
    """
    client_ip = request.headers.get('X-Real-Ip')

    # Fetch IPs from all environment variables
    allowed_ips = set(
        os.getenv('LATEPOINT_IP_ADDRESS', '').split(',') +
        os.getenv('CAMPFIRE_IP_ADDRESS', '').split(',') +
        os.getenv('SQUARE_IP_ADDRESS', '').split(',')
    )

    # Check if IP is allowed
    if client_ip in allowed_ips:
        return True, None

    # Log unauthorized attempt and return error response
    logger.warning(f"Unauthorized access attempt from IP: {client_ip}")
    return False, (jsonify({"error": "Unauthorized IP"}), 403)