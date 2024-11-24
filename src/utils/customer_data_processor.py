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
                return {
                    key.replace("custom_fields[", "").replace("]", ""): value
                    for key, value in request.form.items()
                    if key.startswith("custom_fields[")
                }
        except (ValueError, TypeError):
            logger.error("Invalid custom_fields data")
        return {}

    @staticmethod
    def extract_core_customer_data(data, source):
        """
        Extract and validate the core customer data from various sources.

        Args:
            data (dict): The webhook payload.
            source (str): The source of the webhook (e.g., "LatePoint", "Square").

        Returns:
            dict: The extracted and validated customer data.

        Raises:
            ValueError: If a required field is missing.
        """
        supported_sources = ["admin", "latepoint", "square", "acuity"]
        if source not in supported_sources:
            raise ValueError(f"Unsupported source: {source}")

        field_mapping = {
            "latepoint": {
                "first_name": "first_name",
                "last_name": "last_name",
                "email": "email",
                "booking_system_id": "id",
                "signup_source": "latepoint",
            },
            "square": {
                "first_name": "given_name",
                "last_name": "family_name",
                "email": "email_address",
                "payment_system_id": "id",
                "signup_source": "square",
                "phone_number": "phone_number",
                "address": "address",
            },
        }

        if source not in field_mapping:
            raise ValueError(f"Unsupported source: {source}")

        mapping = field_mapping[source]
        required_fields = ["first_name", "last_name", "email"]
        missing_fields = [field for field in required_fields if not data.get(mapping[field])]

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        return {
            "first_name": data[mapping["first_name"]].strip(),
            "last_name": data[mapping["last_name"]].strip(),
            "email": data[mapping["email"]].strip(),
            "booking_system_id": int(data[mapping["booking_system_id"]]) if source.lower() == "latepoint" else None,
            "payment_system_id": data[mapping["payment_system_id"]] if source.lower() == "square" else None,
            "signup_source": source.lower(),
            "phone_number": data.get("phone_number", None),
            "address": data.get("address", None),
        }

    @staticmethod
    def build_massage_preferences(data):
        """
        Build and validate massage preferences from custom fields.

        Args:
            data (dict): The custom fields data.

        Returns:
            dict: The built and validated massage preferences.
        """
        custom_fields = data
        preferences = {
            "medical_conditions": custom_fields.get("cf_fV6mSkLi", "").strip().lower() == "yes",
            "pressure_level": custom_fields.get("cf_BUQVMrtE", "").strip() or "Medium",
            "session_preference": custom_fields.get("cf_MYTGXxFc", "").strip() or "Quiet",
            "music_preference": custom_fields.get("cf_aMKSBozK", "").strip() or "Nature Sounds",
            "aromatherapy_preference": custom_fields.get("cf_71gt8Um4", "").strip() or "Lavender",
            "referral_source": custom_fields.get("cf_OXZkZKUw", "").strip() or "",
            "email_subscribed": False,
        }

        for key, value in preferences.items():
            if key in ["medical_conditions", "email_subscribed"]:
                assert isinstance(value, bool)
            else:
                assert isinstance(value, str)

        return preferences