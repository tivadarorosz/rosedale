import hmac
import hashlib
import base64
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

def is_valid_webhook_event_signature(body, square_signature, signature_key):
    """
    Validates the Square webhook event signature.

    Args:
        body (str): The raw body of the webhook request.
        square_signature (str): The value of the `x-square-hmacsha256-signature` header.
        signature_key (str): Your Square webhook signature key.

    Returns:
        bool: True if the signature is valid, False otherwise.
    """
    if not square_signature or not signature_key:
        logging.debug("Missing signature or signature key.")
        return False

    # Log the inputs
    logging.debug(f"Raw body: {body}")
    logging.debug(f"Provided signature: {square_signature}")
    logging.debug(f"Signature key: {signature_key}")

    # Compute the HMAC-SHA256 signature
    hmac_key = bytes(signature_key, 'utf-8')
    digest = hmac.new(hmac_key, msg=body.encode('utf-8'), digestmod=hashlib.sha256).digest()
    expected_signature = base64.b64encode(digest).decode('utf-8')

    # Log intermediate steps
    logging.debug(f"HMAC Key (bytes): {hmac_key}")
    logging.debug(f"Computed digest (raw bytes): {digest}")
    logging.debug(f"Computed signature (Base64): {expected_signature}")

    # Compare the computed signature with the received signature
    comparison_result = hmac.compare_digest(expected_signature, square_signature)

    # Log the comparison result
    logging.debug(f"Signature comparison result: {comparison_result}")

    return comparison_result