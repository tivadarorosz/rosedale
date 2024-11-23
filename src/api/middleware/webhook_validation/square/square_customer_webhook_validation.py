
class SquareCustomerWebhookValidator:
    """
    Validator for Square customer webhook payloads.
    """

    @staticmethod
    def validate_customer_payload(data):
        """
        Validates the payload of the Square customer webhook.

        Args:
            data (dict): The payload data extracted from the webhook.

        Returns:
            tuple: (bool, str) - A tuple where the first element indicates success
            and the second contains an error message if validation fails.
        """
        required_fields = ["id", "given_name", "family_name", "email_address"]

        # Check for missing fields
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"

        # Ensure the email is in a valid format
        email = data.get("email_address")
        if email and "@" not in email:
            return False, "Invalid email format"

        return True, None