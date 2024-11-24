import re

class CustomerValidator:
    @staticmethod
    def validate_email(email: str) -> bool:
        if not email:
            return False

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            return False

        return True

    @staticmethod
    def validate_customer_id(customer_id: str) -> bool:
        return bool(customer_id and customer_id.isnumeric())