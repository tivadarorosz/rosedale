import requests
import logging

logger = logging.getLogger(__name__)

# Base URL for ConvertKit API
CONVERTKIT_API_BASE_URL = "https://api.convertkit.com/v3"

class ConvertKitError(Exception):
    """Custom exception for ConvertKit errors."""
    pass

def subscribe_user(api_key: str, form_id: str, email: str, first_name: str) -> dict:
    """
    Subscribe a user to a ConvertKit form.

    :param api_key: Your ConvertKit API key.
    :param form_id: ID of the ConvertKit form.
    :param email: Email of the user to subscribe.
    :param first_name: First name of the user.
    :return: Response data from ConvertKit.
    """
    url = f"{CONVERTKIT_API_BASE_URL}/forms/{form_id}/subscribe"
    payload = {
        "api_key": api_key,
        "email": email,
        "first_name": first_name
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to subscribe user: {e}")
        raise ConvertKitError("Error subscribing user to ConvertKit.") from e