from flask import jsonify
import os
import logging

logger = logging.getLogger(__name__)

def check_allowed_ip(request, service_type='latepoint'):
    """
    Check if request IP is allowed for the specified service
    Args:
        request: Flask request object
        service_type: 'latepoint' or 'campfire'
    Returns:
        tuple: (bool, response)
    """
    client_ip = request.headers.get('X-Real-Ip')

    if service_type == 'latepoint':
        allowed_ips = os.getenv('LATEPOINT_IP_ADDRESS', '').split(',')
    elif service_type == 'campfire':
        allowed_ips = os.getenv('CAMPFIRE_IP_ADDRESS', '').split(',')
    else:
        return False, (jsonify({"error": "Invalid service type"}), 400)

    if client_ip not in allowed_ips:
        logger.warning(f"Unauthorized {service_type} access attempt from IP: {client_ip}")
        return False, (jsonify({"error": "Unauthorized IP"}), 403)

    return True, None