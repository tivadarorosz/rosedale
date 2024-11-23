from src.api.validators.customer_validators import CustomerValidator


class LatePointCustomerWebhookValidator:
    @staticmethod
    def validate_customer_payload(data):
        # Validate email
        if not CustomerValidator.validate_email(data.get("email")):
            return False, "Invalid email address"

        # Validate LatePoint-specific fields
        if "id" not in data:
            return False, "Missing 'id' field"

        return True, None