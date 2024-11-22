from typing import Dict, Any, Tuple, Optional
import re


class CustomerValidator:
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        if not email:
            return False, "Email is required"

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Invalid email format"

        return True, None

    @staticmethod
    def validate_name(name: str, field: str) -> Tuple[bool, Optional[str]]:
        if not name:
            return False, f"{field} is required"

        if len(name) < 2:
            return False, f"{field} must be at least 2 characters long"

        if not name.replace(' ', '').isalpha():
            return False, f"{field} can only contain letters"

        return True, None

    @staticmethod
    def validate_latepoint_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        required_fields = {
            'id': 'LatePoint ID',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email'
        }

        # Check required fields
        for field, name in required_fields.items():
            if not data.get(field):
                return False, f"{name} is required"

        # Validate email
        valid, error = CustomerValidator.validate_email(data['email'])
        if not valid:
            return False, error

        # Validate names
        for field, label in [('first_name', 'First name'), ('last_name', 'Last name')]:
            valid, error = CustomerValidator.validate_name(data[field], label)
            if not valid:
                return False, error

        # Validate custom fields if present
        if custom_fields := data.get("custom_fields"):
            if not isinstance(custom_fields, dict):
                return False, "Custom fields must be a dictionary"

            # Validate specific fields
            pressure_levels = ["Light", "Medium", "Deep"]
            if pressure_level := custom_fields.get("cf_BUQVMrtE"):
                if pressure_level not in pressure_levels:
                    return False, f"Invalid pressure level. Must be one of: {', '.join(pressure_levels)}"

        return True, None

    @staticmethod
    def validate_square_data(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        try:
            customer = data["data"]["object"]["customer"]

            required_fields = {
                'id': 'Square ID',
                'given_name': 'First Name',
                'family_name': 'Last Name',
                'email_address': 'Email'
            }

            for field, name in required_fields.items():
                if not customer.get(field):
                    return False, f"{name} is required"

            valid, error = CustomerValidator.validate_email(customer['email_address'])
            if not valid:
                return False, error

            valid, error = CustomerValidator.validate_name(customer['given_name'], 'First name')
            if not valid:
                return False, error

            valid, error = CustomerValidator.validate_name(customer['family_name'], 'Last name')
            if not valid:
                return False, error

            return True, None

        except KeyError as e:
            return False, f"Missing required field in Square data: {str(e)}"