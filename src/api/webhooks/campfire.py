from flask import Blueprint, request, jsonify
from src.api.validators.ip_validator import check_allowed_ip
from src.core.monitoring import handle_error
from src.core.integrations.campfire import send_room_message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import traceback
from src.services.chatbot import handle_command
from flask import current_app

logger = logging.getLogger(__name__)
campfire_webhook = Blueprint('campfire_webhook', __name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["20 per minute"],
    storage_uri="memory://"
)

@campfire_webhook.route('/<token>', methods=['POST'], strict_slashes=False)
@limiter.limit("20 per minute")
def chatbot(token):
    is_allowed, response = check_allowed_ip(request)
    if not is_allowed:
        return response

    data = request.json
    room_id = data.get("room", {}).get("id")
    try:
        if token != current_app.config.get("CAMPFIRE_WEBHOOK_TOKEN"):
            logger.warning("Invalid webhook token")
            return jsonify({"error": "Unauthorized"}), 401

        room_id = data.get("room", {}).get("id")
        content = data.get("message", {}).get("body", {}).get("plain", "").strip()

        if not room_id:
            logger.error("No room ID in webhook payload")
            return jsonify({"error": "Missing room ID"}), 400

        if not content:
            return '', 204

        result = handle_command(content)
        if "error" in result:
            send_room_message(room_id, f"❌ {result['error']}")
        else:
            if "message" in result:
                send_room_message(room_id, result["message"])
            elif "codes" in result:  # Bulk codes
                codes_list = "\n".join(result["codes"])
                message = f"""✅ Generated codes:
{codes_list}

Description: {result.get('description', 'Premium Gift Card')}"""
                send_room_message(room_id, message)
            elif "code" in result:  # Single code
                code = result.get("code", "")
                description = result.get("description", "")
                message = f"""✅ Generated code:
{code}

Description: {description}"""
                send_room_message(room_id, message)

        return '', 204

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Campfire webhook error")
        send_room_message(room_id, "Oops! Something went wrong. Please try again later.")
        return '', 500