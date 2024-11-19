from flask import Blueprint, request, jsonify
from src.utils.error_monitoring import handle_error
from src.utils.campfire_utils import send_message
import logging
import traceback
import requests
import os

logger = logging.getLogger(__name__)
campfire_webhook = Blueprint('campfire_webhook', __name__)


def get_base_url():
    if os.getenv("FLASK_ENV") == "development":
        return "http://localhost:8080/api/v1/code-generator/generate"
    return "https://app.rosedalemassage.co.uk/api/v1/code-generator/generate"


def parse_code_request(content):
    parts = content.split()
    command = parts[0].lower() if parts else ""
    params = {}

    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=")
            params[key.lower()] = value

    return command, params


def generate_code(command, params):
    base_url = get_base_url()
    api_key = os.getenv("ROSEDALE_API_KEY")

    endpoint_map = {
        "unlimited": "/unlimited",
        "school": "/school-code",
        "referral": "/referral-code",
        "guest": "/guest-pass",
        "gift": "/gift-card",
        "bulk": "/gift-card/bulk",
        "personal": "/personal-code"
    }

    if command not in endpoint_map:
        return None

    endpoint = f"{base_url}{endpoint_map[command]}"
    headers = {"X-API-KEY": api_key}
    response = requests.get(endpoint, params=params, headers=headers)
    return response.json() if response.ok else None


@campfire_webhook.route('/', methods=['POST'])
def handle_webhook():
    try:
        data = request.json
        content = data.get("content", "").strip()

        if not content:
            return jsonify({"status": "no content"}), 200

        command, params = parse_code_request(content)

        if command == "report":
            # Implement report functionality
            report_message = "Report functionality coming soon"
            send_message("studio", report_message)
            return jsonify({"status": "success"}), 200

        result = generate_code(command, params)
        if result:
            message = f"Generated code: {result.get('code', '')}"
            if 'codes' in result:
                message = "Generated codes:\n" + "\n".join(result['codes'])
            send_message("studio", message)

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Campfire webhook error")
        return jsonify({"error": str(e)}), 500