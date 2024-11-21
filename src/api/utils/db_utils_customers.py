import logging
from typing import Optional, Dict, Any
from sqlalchemy import text
from flask import current_app
from src.utils.error_monitoring import handle_error

logger = logging.getLogger(__name__)


def create_customer(customer: Dict[str, Any]) -> Optional[int]:
    """
    Create a new customer record in the database.

    Args:
        customer: Dictionary containing customer information
    Returns:
        Optional[int]: The ID of the created customer, or None if creation failed
    """
    try:
        query = text("""
            INSERT INTO customers (
                latepoint_id, square_id, first_name, last_name, email, phone, gender, dob, location, postcode, status, type, 
                is_pregnant, has_cancer, has_blood_clots, has_infectious_disease, has_bp_issues, has_severe_pain, 
                newsletter_subscribed, accepted_terms, source
            )
            VALUES (
                :latepoint_id, :square_id, :first_name, :last_name, :email, :phone, :gender, 
                :dob, :location, :postcode, :status, :type, :is_pregnant, :has_cancer, :has_blood_clots, 
                :has_infectious_disease, :has_bp_issues, :has_severe_pain, :newsletter_subscribed, :accepted_terms, :source
            )
            RETURNING id;
        """)

        values = {
            "latepoint_id": customer.get("latepoint_id"),
            "square_id": customer.get("square_id"),
            "first_name": customer["first_name"],
            "last_name": customer["last_name"],
            "email": customer["email"],
            "phone": customer["phone"],
            "gender": customer["gender"],
            "dob": customer.get("dob"),
            "location": customer.get("location"),
            "postcode": customer.get("postcode"),
            "status": customer["status"],
            "type": customer["type"],
            "is_pregnant": customer.get("is_pregnant", False),
            "has_cancer": customer.get("has_cancer", False),
            "has_blood_clots": customer.get("has_blood_clots", False),
            "has_infectious_disease": customer.get("has_infectious_disease", False),
            "has_bp_issues": customer.get("has_bp_issues", False),
            "has_severe_pain": customer.get("has_severe_pain", False),
            "newsletter_subscribed": customer.get("newsletter_signup", False),
            "accepted_terms": customer.get("accepted_terms", False),
            "source": customer.get("source")
        }

        with current_app.config['db_engine'].connect() as conn:
            with conn.begin():
                result = conn.execute(query, values)
                row = result.first()
                return row[0] if row else None

    except Exception as error:
        logger.error("Error creating customer: %s", error)
        handle_error(error, "Database operation error")
        raise


def update_latepoint_customer(customer: Dict[str, Any]) -> Optional[int]:
    """
    Update existing customer record with Latepoint data.

    Args:
        customer: Dictionary containing customer information
    Returns:
        Optional[int]: The ID of the updated customer, or None if update failed
    """
    try:
        query = text("""
            UPDATE customers 
            SET 
                latepoint_id = :latepoint_id,
                first_name = :first_name,
                last_name = :last_name,
                phone = :phone,
                gender = :gender,
                status = :status,
                type = :type,
                is_pregnant = :is_pregnant,
                has_cancer = :has_cancer,
                has_blood_clots = :has_blood_clots,
                has_infectious_disease = :has_infectious_disease,
                has_bp_issues = :has_bp_issues,
                has_severe_pain = :has_severe_pain,
                newsletter_subscribed = :newsletter_subscribed,
                accepted_terms = :accepted_terms,
                last_updated = CURRENT_TIMESTAMP
            WHERE email = :email 
            RETURNING id;
        """)

        values = {
            "latepoint_id": customer["latepoint_id"],
            "first_name": customer["first_name"],
            "last_name": customer["last_name"],
            "email": customer["email"],
            "phone": customer["phone"],
            "gender": customer["gender"],
            "status": customer["status"],
            "type": customer["type"],
            "is_pregnant": customer.get("is_pregnant", False),
            "has_cancer": customer.get("has_cancer", False),
            "has_blood_clots": customer.get("has_blood_clots", False),
            "has_infectious_disease": customer.get("has_infectious_disease", False),
            "has_bp_issues": customer.get("has_bp_issues", False),
            "has_severe_pain": customer.get("has_severe_pain", False),
            "newsletter_subscribed": customer.get("newsletter_signup", False),
            "accepted_terms": customer.get("accepted_terms", False)
        }

        with current_app.config['db_engine'].connect() as conn:
            with conn.begin():
                result = conn.execute(query, values)
                row = result.first()
                return row[0] if row else None

    except Exception as error:
        logger.error("Error updating Latepoint customer: %s", error)
        handle_error(error, "Database operation error")
        raise


def update_square_customer(customer: Dict[str, Any]) -> Optional[int]:
    """
    Update existing customer record with Square ID only.

    Args:
        customer: Dictionary containing customer information
    Returns:
        Optional[int]: The ID of the updated customer, or None if update failed
    """
    try:
        query = text("""
            UPDATE customers 
            SET 
                square_id = :square_id,
                last_updated = CURRENT_TIMESTAMP
            WHERE email = :email 
            RETURNING id;
        """)

        values = {
            "square_id": customer["square_id"],
            "email": customer["email"]
        }

        with current_app.config['db_engine'].connect() as conn:
            with conn.begin():
                result = conn.execute(query, values)
                row = result.first()
                return row[0] if row else None

    except Exception as error:
        logger.error("Error updating Square customer: %s", error)
        handle_error(error, "Database operation error")
        raise


def check_email_exists(email: str) -> bool:
    """
    Check if an email already exists in the database.

    Args:
        email: Email address to check
    Returns:
        bool: True if email exists, False otherwise
    """
    try:
        query = text("""
            SELECT id 
            FROM customers 
            WHERE email = :email
            LIMIT 1;
        """)

        with current_app.config['db_engine'].connect() as conn:
            result = conn.execute(query, {"email": email})
            return bool(result.first())

    except Exception as error:
        logger.error("Error checking email existence: %s", error)
        handle_error(error, "Database operation error")
        raise


def validate_latepoint_customer(customer: Dict[str, Any]) -> bool:
    """
    Validate required fields for Latepoint customer data.

    Args:
        customer: Dictionary containing customer information
    Returns:
        bool: True if all required fields are present
    """
    required_fields = [
        'latepoint_id', 'first_name', 'last_name',
        'email', 'phone', 'gender', 'status', 'type'
    ]
    return all(customer.get(field) for field in required_fields)


def validate_square_customer(customer: Dict[str, Any]) -> bool:
    """
    Validate required fields for Square customer data.

    Args:
        customer: Dictionary containing customer information
    Returns:
        bool: True if all required fields are present
    """
    required_fields = ['square_id', 'email']
    return all(customer.get(field) for field in required_fields)


def determine_customer_type(email: str) -> str:
    """
    Determine customer type based on email domain and business rules.

    Args:
        email: Customer email address
    Returns:
        str: Customer type ('employee' or 'client')
    """
    try:
        domain = email.split('@')[1].lower()

        # Employee check
        if domain == "rosedalemassage.co.uk":
            return "employee"

        # Default to regular client
        return "client"
    except Exception as error:
        logger.error("Error determining customer type: %s", error)
        handle_error(error, "Error determining customer type")
        return "client"  # Default to client if there's any error