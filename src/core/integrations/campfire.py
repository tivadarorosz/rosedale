import os
import requests
import logging

logger = logging.getLogger(__name__)

# Load environment variables
CAMPFIRE_URLS = {
    "studio": os.getenv("CAMPFIRE_STUDIO_URL"),
    "finance": os.getenv("CAMPFIRE_FINANCE_URL"),
    "tech": os.getenv("CAMPFIRE_TECH_URL"),
    "alert": os.getenv("CAMPFIRE_ALERT_URL"),
    "bot": os.getenv("CAMPFIRE_BOT_URL"),
}

def get_campfire_url(room_id: str) -> str:
    """
    Generate the URL for sending messages to a specific Campfire room.

    :param room_id: The ID of the Campfire room.
    :return: The full Campfire URL for the room.
    """
    base_url = "https://chat.rosedalemassage.co.uk/rooms"
    room_token = os.getenv("CAMPFIRE_ROOM_TOKEN")
    return f"{base_url}/{room_id}/{room_token}/messages"

def send_message(channel: str, message: str):
    """
    Send a message to a specific Campfire channel.

    :param channel: The Campfire channel (e.g., "studio").
    :param message: The message to send.
    :return: Tuple of HTTP status code and response text.
    """
    try:
        logger.debug(f"Preparing to send message to channel: {channel}")
        url = CAMPFIRE_URLS.get(channel)

        if not url:
            raise ValueError(f"Unknown channel: {channel}. Available channels: {list(CAMPFIRE_URLS.keys())}")

        headers = {
            "Content-Type": "text/html",
        }
        encoded_message = message.encode("utf-8")

        logger.info(f"Sending message to {channel} ({url}): {message}")
        response = requests.post(url, data=encoded_message, headers=headers)

        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Text: {response.text or '<empty>'}")

        if 200 <= response.status_code < 300:
            return response.status_code, response.text or "Message sent successfully"

        raise Exception(f"Campfire error: HTTP {response.status_code}, Body: {response.text or '<no response body>'}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending message to Campfire: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending message to Campfire: {str(e)}")
        raise

def send_room_message(room_id: str, message: str, user_name: str = None):
    """
    Send a message to a specific Campfire room.

    :param room_id: The ID of the Campfire room.
    :param message: The message to send.
    :param user_name: Optional username to mention in the message.
    :return: Tuple of HTTP status code and response text.
    """
    try:
        url = get_campfire_url(room_id)

        if user_name:
            message = f"@{user_name} {message}"

        headers = {
            "Content-Type": "text/html",
        }
        encoded_message = message.encode("utf-8")

        logger.info(f"Sending message to room {room_id}: {message}")
        response = requests.post(url, data=encoded_message, headers=headers)

        logger.debug(f"Response Status Code: {response.status_code}")
        logger.debug(f"Response Text: {response.text or '<empty>'}")

        if 200 <= response.status_code < 300:
            return response.status_code, response.text or "Message sent successfully"

        raise Exception(f"Campfire error: HTTP {response.status_code}, Body: {response.text or '<no response body>'}")
    except Exception as e:
        logger.error(f"Error sending room message: {str(e)}")
        raise