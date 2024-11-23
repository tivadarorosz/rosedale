import json
import logging

logger = logging.getLogger(__name__)

class CustomerDataProcessor:
    @staticmethod
    def parse_custom_fields(custom_fields_json):
        """
        Safely parse the custom_fields JSON string into a dictionary.
        """
        try:
            if custom_fields_json:
                return json.loads(custom_fields_json)
        except json.JSONDecodeError:
            logger.error("Invalid JSON in custom_fields")
        return {}  # Return an empty dictionary if parsing fails

    @staticmethod
    def extract_core_customer_data(data, source):
        """
        Extract and validate the core customer data from various sources.

        Args:
            data: The webhook payload.
            source: The source of the webhook (e.g., "LatePoint", "Square").

        Raises:
            ValueError: If a required field is missing.
        """
        # Define source-specific mappings
        field_mapping = {
            "LatePoint": {
                "first_name": "first_name",
                "last_name": "last_name",
                "email": "email",
                "id": "id",
            },
            "Square": {
                "first_name": "given_name",
                "last_name": "family_name",
                "email": "email_address",
                "id": "id",
            },
        }

        # Ensure source is supported
        if source not in field_mapping:
            raise ValueError(f"Unsupported source: {source}")

        mapping = field_mapping[source]

        # Validate and extract required fields
        required_fields = ["first_name", "last_name", "email", "id"]
        missing_fields = [
            field for field in required_fields if not data.get(mapping[field])
        ]

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        return {
            "first_name": data[mapping["first_name"]].strip(),
            "last_name": data[mapping["last_name"]].strip(),
            "email": data[mapping["email"]].strip(),
            "booking_system_id": data[mapping["id"]].strip(),
        }

    @staticmethod
    def build_session_preferences(custom_fields):
        """
        Build session preferences from custom fields.
        """
        return {
            "medical_conditions": custom_fields.get("cf_fV6mSkLi", "").strip().lower()
            == "yes",
            "pressure_level": custom_fields.get("cf_BUQVMrtE", "").strip(),
            "session_preference": custom_fields.get("cf_MYTGXxFc", "").strip(),
            "music_preference": custom_fields.get("cf_aMKSBozK", "").strip(),
            "aromatherapy_preference": custom_fields.get("cf_71gt8Um4", "").strip(),
            "referral_source": custom_fields.get("cf_OXZkZKUw", "").strip(),
            "email_subscribed": False,  # Default to False
        }