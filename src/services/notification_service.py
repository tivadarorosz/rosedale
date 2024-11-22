from flask import current_app
import logging
from src.core.integrations.campfire import send_message
from typing import Optional

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def notify_campfire(message: str, channel: str = "studio") -> Optional[tuple]:
        """
        Send notification to Campfire channel.

        Args:
            message: Message to send
            channel: Campfire channel (studio, alert, tech, etc.)

        Returns:
            Tuple of (status, response) if sent, None if in development
        """
        try:
            if current_app.config["FLASK_ENV"] == "development":
                return None

            status, response = send_message(channel, message)
            logger.info(f"Campfire Response: Status {status}, Body: {response}")
            return status, response

        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return None

# Example usage in webhook:
# NotificationService.notify_campfire(
#     f"🎉 New {source.title()} Customer: {name} ({email}) just signed up!"
# )