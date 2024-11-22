from flask import request, jsonify
from functools import wraps
import time

# A dictionary to store IP-based request data
RATE_LIMIT_DATA = {}

def rate_limit(limit, window):
    """
    Middleware function for rate limiting by IP address.

    :param limit: Maximum number of requests allowed.
    :param window: Time window in seconds.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            client_ip = request.remote_addr or "unknown"  # Get the client's IP address
            current_time = time.time()

            # Initialize or clean up expired request logs for this IP
            if client_ip not in RATE_LIMIT_DATA:
                RATE_LIMIT_DATA[client_ip] = []
            RATE_LIMIT_DATA[client_ip] = [t for t in RATE_LIMIT_DATA[client_ip] if t > current_time - window]

            # Check if the IP has exceeded the limit
            if len(RATE_LIMIT_DATA[client_ip]) >= limit:
                retry_after = window - (current_time - RATE_LIMIT_DATA[client_ip][0])
                return jsonify({
                    "error": "Rate limit exceeded. Try again later.",
                    "retry_after": f"{retry_after:.1f} seconds"
                }), 429

            # Record the current request timestamp
            RATE_LIMIT_DATA[client_ip].append(current_time)
            return f(*args, **kwargs)
        return wrapped
    return decorator