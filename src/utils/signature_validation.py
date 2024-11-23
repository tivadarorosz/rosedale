import hmac
import hashlib
import base64

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
        return False

    # Compute the HMAC-SHA256 signature
    hmac_key = bytes(signature_key, 'utf-8')
    digest = hmac.new(hmac_key, msg=body.encode('utf-8'), digestmod=hashlib.sha256).digest()
    expected_signature = base64.b64encode(digest).decode('utf-8')

    # Compare the computed signature with the received signature
    return hmac.compare_digest(expected_signature, square_signature)