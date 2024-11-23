class CustomerValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        if not email or "@" not in email:
            return False
        return True

    @staticmethod
    def validate_customer_id(customer_id: str) -> bool:
        return bool(customer_id and customer_id.isnumeric())