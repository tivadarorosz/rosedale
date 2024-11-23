from flask import request, jsonify
from functools import wraps
from src.api.validators.ip_validator import check_allowed_ip

def get_client_ip():
    """
    Extract the client's IP address from the request object.

    Returns:
        str: The client's IP address.
    """
    # Check for common headers that contain the client IP
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # If there are multiple IPs in X-Forwarded-For, take the first one
        return x_forwarded_for.split(',')[0].strip()

    x_real_ip = request.headers.get('X-Real-IP')
    if x_real_ip:
        return x_real_ip.strip()

    # Fallback to remote_addr
    return request.remote_addr

def validate_request_ip(func):
    """
    Middleware to validate if the client's IP is allowed.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        client_ip = get_client_ip()

        if not check_allowed_ip(client_ip):
            return jsonify({"error": "Unauthorized IP address"}), 403

        return func(*args, **kwargs)
    return wrapper