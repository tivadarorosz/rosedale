from typing import Dict, Any, Tuple, Optional
import re


class CustomerValidator:
    """Validator for customer data."""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
        """Validate phone number format."""
        if not phone:
            return False, "Phone number is required"

        if not phone.startswith("+44"):
            return False, "Phone number must start with +44"

        # Remove spaces and any other formatting
        cleaned_phone = re.sub(r'[^0-9+]', '', phone)
        if len(cleaned_phone) != 13:  # +44 plus 10 digits
            return False, "Phone number must be 10 digits after +44"

        return True, None

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """Validate email format."""
        if not email:
            return False, "Email is required"

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"

        return True, None

    @staticmethod
    def validate_name(name: str, field: str) -> Tuple[bool, Optional[str]]:
        """Validate name fields."""
        if not name:
            return False, f"{field} is required"

        if len(name) < 2:
            return False, f"{field} must be at least 2 characters long"

        if not name.replace(' ', '').isalpha():
            return False, f"{field} can only contain letters"

        return True, None

    @staticmethod
    def validate_latepoint_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate LatePoint customer data."""
        required_fields = {
            'id': 'LatePoint ID',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'phone': 'Phone'
        }

        # Check required fields
        for field, name in required_fields.items():
            if not data.get(field):
                return False, f"{name} is required"

        # Validate email
        valid, error = CustomerValidator.validate_email(data['email'])
        if not valid:
            return False, error

        # Validate phone
        valid, error = CustomerValidator.validate_phone(data['phone'])
        if not valid:
            return False, error

        # Validate names
        valid, error = CustomerValidator.validate_name(data['first_name'], 'First name')
        if not valid:
            return False, error

        valid, error = CustomerValidator.validate_name(data['last_name'], 'Last name')
        if not valid:
            return False, error

        return True, None

    @staticmethod
    def validate_square_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate Square customer data."""
        try:
            customer = data["data"]["object"]["customer"]

            required_fields = {
                'id': 'Square ID',
                'given_name': 'First Name',
                'family_name': 'Last Name',
                'email_address': 'Email'
            }

            # Check required fields
            for field, name in required_fields.items():
                if not customer.get(field):
                    return False, f"{name} is required"

            # Validate email
            valid, error = CustomerValidator.validate_email(customer['email_address'])
            if not valid:
                return False, error

            # Validate names
            valid, error = CustomerValidator.validate_name(customer['given_name'], 'First name')
            if not valid:
                return False, error

            valid, error = CustomerValidator.validate_name(customer['family_name'], 'Last name')
            if not valid:
                return False, error

            return True, None

        except KeyError as e:
            return False, f"Missing required field in Square data: {str(e)}"