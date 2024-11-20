from flask import Blueprint, request, jsonify
from src.utils.error_monitoring import handle_error
from src.utils.campfire_utils import send_room_message
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import traceback
import requests
import os

logger = logging.getLogger(__name__)
campfire_webhook = Blueprint('campfire_webhook', __name__)

# Code type descriptions
CODE_DESCRIPTIONS = {
    "unlimited": "Unlimited Package Access",
    "school": "School Group Discount",
    "referral": "Friend & Family Referral Discount",
    "guest": "Free Session Guest Pass",
    "gift_digital": "Digital Gift Card",
    "gift_premium": "Premium Gift Card",
    "personal_duration": "Personal Duration Package",
    "personal_discount": "Personal Discount Code"
}

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
    <div style="line-height: 1.5;">
        <p>📋 <strong>Available Commands:</strong></p>
        <br>

        <div>
            <strong>1️⃣ Unlimited Package Codes</strong><br>
            <strong>Usage:</strong> unlimited duration=[60/90/110] first_name=[NAME] last_name=[NAME] expiration=[YYYY-MM-DD]<br>
            <strong>Example:</strong> unlimited duration=90 first_name=Rebecca last_name=Smith expiration=2024-12-31<br>
            <em>Generates:</em> UL-90-REBECCA-ABCD12<br>
            <em>Description:</em> Unlimited-90-Rebecca Smith-31 Dec 2024
        </div>
        <br>

        <div>
            <strong>2️⃣ School Group Discount Codes</strong><br>
            <strong>Usage:</strong> school discount=[1-100]<br>
            <strong>Example:</strong> school discount=20<br>
            <em>Generates:</em> SCHL-20-ABCD12
        </div>
        <br><br>

        <div>
            <strong>3️⃣ Referral Discount Codes</strong><br>
            <strong>Usage:</strong> referral first_name=[NAME] discount=[1-100]<br>
            <strong>Example:</strong> referral first_name=Jane discount=50<br>
            <em>Generates:</em> REF-50-JANE-ABCD12
        </div>
        <br>

        <div>
            <strong>4️⃣ Free Guest Pass Codes</strong><br>
            <strong>Usage:</strong> guest duration=[60/90/110] first_name=[NAME]<br>
            <strong>Example:</strong> guest duration=60 first_name=Bob<br>
            <em>Generates:</em> FREE-60-BOB-ABCD12
        </div>
        <br>

        <div>
            <strong>5️⃣ Gift Card Codes</strong><br>
            <strong>Usage:</strong> gift amount=[VALUE] type=[DIGITAL/PREMIUM] first_name=[NAME]<br>
            <strong>Examples:</strong><br>
            With name: gift amount=100 type=DIGITAL first_name=Alice<br>
            <em>Generates:</em> GIFT-DGTL-100-ALICE-K7M2P9X4<br>
            Without name: gift amount=150 type=PREMIUM<br>
            <em>Generates:</em> GIFT-PREM-150-B7K2N8L4
        </div>
        <br>

        <div>
            <strong>6️⃣ Bulk Premium Gift Cards</strong><br>
            <strong>Usage:</strong> bulk amount=[VALUE] quantity=[1-50]<br>
            <strong>Example:</strong> bulk amount=50 quantity=2<br>
            <em>Generates multiple codes like:</em><br>
            GIFT-PREM-50-B7K2N8L4<br>
            GIFT-PREM-50-X9Y4M7P2
        </div>
        <br>

        <div>
            <strong>7️⃣ Personal Massage Codes</strong><br>
            <strong>Usage:</strong><br>
            Duration-based: personal duration=[60/90/110] first_name=[NAME]<br>
            Discount-based: personal discount=[1-100] first_name=[NAME]<br>
            <strong>Examples:</strong><br>
            Duration: personal duration=90 first_name=Carol<br>
            <em>Generates:</em> PERS-90-CAROL-ABCD12<br>
            Discount: personal discount=25 first_name=Emily<br>
            <em>Generates:</em> PERS-25-EMILY-ABCD12
        </div>
        <br>

        <div>
            <strong>8️⃣ Daily Report</strong><br>
            <strong>Usage:</strong> Get sales and other statistics<br>
            <strong>Example:</strong> report
        </div>
        <br>

        <div>
            <strong>9️⃣ Help</strong><br>
            <strong>Usage:</strong> Show this help message<br>
            <strong>Example:</strong> help
        </div>
        <br>

        <div>
            <em>Note: All codes are automatically converted to uppercase. Gift cards use 8-character unique endings, all others use 6 characters.</em>
        </div>
        <br>

        <div>
            Further information is at <a href="https://github.com/tivadarorosz/rosedale/blob/main/src/api/code_generator/README.md">GitHub Documentation</a>
        </div>
    </div>
    """

def get_code_type(code):
    """Determine code type from the generated code"""
    if code.startswith("UL-"):
        return "unlimited"
    elif code.startswith("SCHL-"):
        return "school"
    elif code.startswith("REF-"):
        return "referral"
    elif code.startswith("FREE-"):
        return "guest"
    elif code.startswith("GIFT-DGTL-"):
        return "gift_digital"
    elif code.startswith("GIFT-PREM-"):
        return "gift_premium"
    elif code.startswith("PERS-"):
        # Check if it's duration or discount based
        parts = code.split("-")
        if len(parts) > 1 and parts[1] in ["60", "90", "110"]:
            return "personal_duration"
        return "personal_discount"
    return "unknown"

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

@campfire_webhook.route('/<token>', methods=['POST'], strict_slashes=False)
@limiter.limit("20 per minute")
def handle_webhook(token):
    try:
        if token != os.getenv("CAMPFIRE_WEBHOOK_TOKEN"):
            logger.warning("Invalid webhook token")
            return jsonify({"error": "Unauthorized"}), 401

        data = request.json
        room_id = data.get("room", {}).get("id")
        content = data.get("message", {}).get("body", {}).get("plain", "").strip()

        if not room_id:
            logger.error("No room ID in webhook payload")
            return jsonify({"error": "Missing room ID"}), 400

        if not content:
            return '', 204

        if content.lower() == "help":
            send_room_message(room_id, get_help_message())
            return '', 204

        command, params = parse_code_request(content)

        if command == "report":
            report_message = "Report functionality coming soon"
            send_room_message(room_id, report_message)
            return '', 204

        result = generate_code(command, params)
        if result:
            if "error" in result:
                send_room_message(room_id, f"❌ {result['error']}")
            else:
                if 'codes' in result:  # Bulk codes
                    codes_list = "\n".join(result['codes'])
                    message = f"""✅ Generated codes:
{codes_list}

Description: {CODE_DESCRIPTIONS['gift_premium']}"""
                else:  # Single code
                    code = result.get('code', '')
                    code_type = get_code_type(code)
                    message = f"""✅ Generated code:
{code}

Description: {CODE_DESCRIPTIONS[code_type]}"""
                send_room_message(room_id, message)
        else:
            send_room_message(room_id, "❌ Invalid command. Type 'help' to see available commands.")

        return '', 204

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        logger.error(traceback.format_exc())
        handle_error(e, "Campfire webhook error")
        return jsonify({"error": str(e)}), 500