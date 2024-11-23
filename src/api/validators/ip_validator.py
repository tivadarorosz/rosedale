from flask import jsonify
import os
import logging

logger = logging.getLogger(__name__)


def check_allowed_ip(client_ip):
    """
    Check if the given IP address is in the allowed list.

    Args:
        client_ip (str): The IP address to check.

    Returns:
        bool: True if the IP is allowed, False otherwise.
    """

    # Fetch IPs from all environment variables
    allowed_ips = set(
        os.getenv('LATEPOINT_IP_ADDRESS', '').split(',') +
        os.getenv('CAMPFIRE_IP_ADDRESS', '').split(',') +
        os.getenv('SQUARE_IP_ADDRESS', '').split(',') +
        os.getenv('WHITELIST_IP_ADDRESS', '').split(',')
    )

    # Check if IP is allowed
    if client_ip in allowed_ips:
        return True, None

    # Log unauthorized attempt and return error response
    logger.warning(f"Unauthorized access attempt from IP: {client_ip}")
    return False, (jsonify({"error": "Unauthorized IP"}), 403)