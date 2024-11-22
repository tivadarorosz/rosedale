import requests
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class CommandHandler:
    def handle_help(self, params):
        return self.get_help_message()

    def get_help_message(self):
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

    def handle_report(self, params):
        report_message = "Report functionality coming soon"
        return {"message": report_message}

    def handle_code(self, params):
        command = "code"
        result = self.generate_code(command, params)
        return result

    def get_code_type(self, code):
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
            parts = code.split("-")
            if len(parts) > 1 and parts[1] in ["60", "90", "110"]:
                return "personal_duration"
            return "personal_discount"
        return "unknown"

    def parse_code_request(self, content):
        parts = content.split()
        command = parts[0].lower() if parts else ""
        params = {}

        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=")
                params[key.lower()] = value

        return command, params

    def generate_code(self, command, params):
        base_url = current_app.config.get('CODE_GENERATOR_URL')
        api_key = current_app.config.get('ROSEDALE_API_KEY')

        endpoint_map = {
            "code": "/generate",
            # ... other endpoints
        }

        if command not in endpoint_map:
            logger.warning(f"Invalid code generation command: {command}")
            return None

        endpoint = f"{base_url}{endpoint_map[command]}"
        headers = {"X-API-KEY": api_key}

        try:
            response = requests.get(endpoint, params=params, headers=headers)
            if response.ok:
                return response.json()
            else:
                error_message = response.json().get("error", "Failed to generate code")
                logger.warning(f"API request failed: {response.status_code} - {error_message}")
                return {"error": error_message}
        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return {"error": "Failed to connect to code generator service"}

    def handle_customer(self, params):
        # Implement customer-related command handling logic here
        return {"message": "Customer command handled"}

def handle_command(content):
    parts = content.split()
    command = parts[0].lower() if parts else ""
    params = {}

    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=")
            params[key.lower()] = value

    command_handler = CommandHandler()
    if command in COMMAND_HANDLERS:
        return getattr(command_handler, COMMAND_HANDLERS[command])(params)
    else:
        logger.warning(f"Unknown command: {command}")
        return {"error": f"Unknown command: {command}"}

COMMAND_HANDLERS = {
    "help": "handle_help",
    "report": "handle_report",
    "code": "handle_code",
    "customer": "handle_customer",
    # Add more commands and their handlers here
}