from flask import Blueprint, request, jsonify
from src.utils.error_monitoring import handle_error
from src.utils.campfire_utils import send_message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import traceback
import requests
import os

logger = logging.getLogger(__name__)
campfire_webhook = Blueprint('campfire_webhook', __name__)

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


def get_base_url():
    if os.getenv("FLASK_ENV") == "development":
        return "http://localhost:8080/api/v1/code-generator/generate"
    return "https://app.rosedalemassage.co.uk/api/v1/code-generator/generate"


def get_help_message():
    return """
    <p>📋 <strong>Available Commands:</strong></p>
    <ol>
        <li>1️⃣ <strong>Generate unlimited package codes.</strong><br>
            <strong>Usage:</strong> duration=[60/90/110] first_name=[NAME]<br>
            <strong>Example:</strong> unlimited duration=60 first_name=John
        </li>
        <li>2️⃣ <strong>Generate school group discount codes.</strong><br>
            <strong>Usage:</strong> discount=[20/50]<br>
            <strong>Example:</strong> school discount=20
        </li>
        <li>3️⃣ <strong>Generate referral discount codes.</strong><br>
            <strong>Usage:</strong> first_name=[NAME] discount=[20/50]<br>
            <strong>Example:</strong> referral first_name=Jane discount=50
        </li>
        <li>4️⃣ <strong>Generate free guest passes.</strong><br>
            <strong>Usage:</strong> duration=[60/90/110] first_name=[NAME]<br>
            <strong>Example:</strong> guest duration=90 first_name=Bob
        </li>
        <li>5️⃣ <strong>Generate gift card codes.</strong><br>
            <strong>Usage:</strong> amount=[VALUE] type=[DIGITAL/PREMIUM] first_name=[NAME]<br>
            <strong>Example:</strong> gift amount=100 type=DIGITAL first_name=Alice
        </li>
        <li>6️⃣ <strong>Generate multiple premium gift cards.</strong><br>
            <strong>Usage:</strong> amount=[VALUE] quantity=[1-50]<br>
            <strong>Example:</strong> bulk amount=50 quantity=5
        </li>
        <li>7️⃣ <strong>Generate personal massage codes.</strong><br>
            <strong>Usage:</strong> duration=[60/90/110] first_name=[NAME]<br>
            <strong>Example:</strong> personal duration=110 first_name=Carol
        </li>
        <li>8️⃣ <strong>Daily Report</strong><br>
            <strong>Usage:</strong> Get sales and other statistics.<br>
            <strong>Example:</strong> report
        </li>
        <li>9️⃣ <strong>Help</strong><br>
            <strong>Usage:</strong> Show this message.<br>
            <strong>Example:</strong> help
        </li>
    </ol>
    """


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

    try:
        response = requests.get(endpoint, params=params, headers=headers)
        if response.ok:
            return response.json()
        else:
            logger.error(f"API request failed: {response.status_code} - {response.text}")
            return {"error": f"Failed to generate code: {response.text}"}
    except requests.RequestException as e:
        logger.error(f"Request failed: {str(e)}")
        return {"error": "Failed to connect to code generator service"}


@campfire_webhook.route('/<token>/', methods=['POST'])
@limiter.limit("20 per minute")
def handle_webhook(token):
    try:
        if token != os.getenv("CAMPFIRE_WEBHOOK_TOKEN"):
            logger.warning("Invalid webhook token")
            return jsonify({"error": "Unauthorized"}), 401

        data = request.json
        content = data.get("content", "").strip()

        if not content:
            return jsonify({"status": "no content"}), 200

        if content.lower() == "help":
            send_message("bot", get_help_message())
            return jsonify({"status": "success"}), 200

        command, params = parse_code_request(content)

        if command == "report":
            report_message = "Report functionality coming soon"
            send_message("bot", report_message)
            return jsonify({"status": "success"}), 200

        result = generate_code(command, params)
        if result:
            if "error" in result:
                send_message("bot", f"❌ {result['error']}")
            else:
                message = f"Generated code: {result.get('code', '')}"
                if 'codes' in result:
                    message = "Generated codes:\n" + "\n".join(result['codes'])
                send_message("bot", f"✅ {message}")
        else:
            send_message("bot", "❌ Invalid command. Type 'help' to see available commands.")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Campfire webhook error")
        return jsonify({"error": str(e)}), 500