from typing import Optional, Dict, Any, Tuple
from sqlalchemy.exc import IntegrityError
import logging
from datetime import datetime
from models import Customer
from src.core.monitoring import handle_error
from app import db

logger = logging.getLogger(__name__)

def get_customer_by_email(email: str) -> Optional[Customer]:
    """
    Get customer by email address.

    Args:
        email (str): Customer's email address

    Returns:
        Optional[Customer]: Customer object if found, None otherwise
    """
    try:
        return Customer.query.filter_by(email=email.lower().strip()).first()
    except Exception as e:
        logger.error(f"Error retrieving customer by email {email}: {str(e)}")
        handle_error(e, f"Error retrieving customer by email")
        return None

def get_customer_by_id(customer_id: int) -> Optional[Customer]:
    """
    Get customer by ID.

    Args:
        customer_id (int): Customer's ID

    Returns:
        Optional[Customer]: Customer object if found, None otherwise
    """
    try:
        return Customer.query.get(customer_id)
    except Exception as e:
        logger.error(f"Error retrieving customer by ID {customer_id}: {str(e)}")
        handle_error(e, f"Error retrieving customer by ID")
        return None

def get_customers_by_type(customer_type: str) -> list[Customer]:
    """
    Get all customers of a specific type.

    Args:
        customer_type (str): Type of customers to retrieve ('client' or 'employee')

    Returns:
        list[Customer]: List of customers of the specified type
    """
    try:
        return Customer.query.filter_by(type=customer_type).all()
    except Exception as e:
        logger.error(f"Error retrieving customers of type {customer_type}: {str(e)}")
        handle_error(e, f"Error retrieving customers by type")
        return []


def determine_customer_type(email: str) -> str:
    """
    Determine customer type based on email domain and business rules.

    Args:
        email (str): Customer's email address

    Returns:
        str: 'employee' for company emails, 'client' for all others
    """
    try:
        domain = email.split('@')[1].lower()

        # Employee check
        if domain == "rosedalemassage.co.uk":
            logger.info(f"Determined {email} as employee based on domain")
            return "employee"

        # Default to regular client
        logger.info(f"Determined {email} as client based on domain")
        return "client"

    except Exception as error:
        logger.error(f"Error determining customer type for {email}: {str(error)}")
        handle_error(error, "Error determining customer type")
        return "client"  # Default to client if there's any error


def email_exists(email: str) -> bool:
    """
    Check if an email address exists in the database.

    Args:
        email (str): Email address to check

    Returns:
        bool: True if email exists, False otherwise
    """
    try:
        return Customer.query.filter_by(email=email.lower().strip()).count() > 0
    except Exception as e:
        logger.error(f"Error checking email existence for {email}: {str(e)}")
        handle_error(e, f"Error checking email existence for {email}")
        return False


def create_customer(customer_data: Dict[str, Any]) -> tuple[Optional[int], Optional[str]]:
    """
    Create a new customer record in the database.

    Args:
        customer_data (Dict[str, Any]): Dictionary containing customer information
            Required fields:
            - email (str)
            - first_name (str)
            - last_name (str)
            - status (str)
            - type (str)
            - source (str)

    Returns:
        tuple[Optional[int], Optional[str]]: Tuple containing:
            - customer_id if successful, None if failed
            - error message if failed, None if successful
    """
    try:
        # Validate required fields
        required_fields = ['email', 'first_name', 'last_name', 'status', 'type', 'source']
        missing_fields = [field for field in required_fields if not customer_data.get(field)]

        if missing_fields:
            return None, f"Missing required fields: {', '.join(missing_fields)}"

        # Check if email already exists
        if email_exists(customer_data['email']):
            return None, "Email already exists"

        # Create new customer instance
        new_customer = Customer(
            latepoint_id=customer_data.get('latepoint_id'),
            square_id=customer_data.get('square_id'),
            first_name=customer_data['first_name'],
            last_name=customer_data['last_name'],
            email=customer_data['email'].lower().strip(),
            phone=customer_data.get('phone'),
            gender=customer_data.get('gender'),
            dob=customer_data.get('dob'),
            location=customer_data.get('location'),
            postcode=customer_data.get('postcode'),
            status=customer_data['status'],
            type=customer_data['type'],
            source=customer_data['source'],
            is_pregnant=customer_data.get('is_pregnant', False),
            has_cancer=customer_data.get('has_cancer', False),
            has_blood_clots=customer_data.get('has_blood_clots', False),
            has_infectious_disease=customer_data.get('has_infectious_disease', False),
            has_bp_issues=customer_data.get('has_bp_issues', False),
            has_severe_pain=customer_data.get('has_severe_pain', False),
            newsletter_subscribed=customer_data.get('newsletter_subscribed', False),
            accepted_terms=customer_data.get('accepted_terms', True)
        )

        db.session.add(new_customer)
        db.session.commit()

        logger.info(f"Created new customer with ID {new_customer.id}")
        return new_customer.id, None

    except IntegrityError as e:
        db.session.rollback()
        error_msg = "Database integrity error while creating customer"
        logger.error(f"{error_msg}: {str(e)}")
        handle_error(e, error_msg)
        return None, "Customer could not be created due to data conflict"

    except Exception as e:
        db.session.rollback()
        error_msg = "Unexpected error while creating customer"
        logger.error(f"{error_msg}: {str(e)}")
        handle_error(e, error_msg)
        return None, str(e)


def update_latepoint_customer(customer_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Update customer with Latepoint data.

    Args:
        customer_data: Dictionary containing updated customer information

    Returns:
        tuple[bool, Optional[str]]: Success flag and error message if any
    """
    try:
        customer = Customer.query.filter_by(email=customer_data['email'].lower().strip()).first()
        if not customer:
            return False, "Customer not found"

        # Update fields
        customer.latepoint_id = customer_data['latepoint_id']
        customer.first_name = customer_data['first_name']
        customer.last_name = customer_data['last_name']
        customer.phone = customer_data['phone']
        customer.gender = customer_data['gender']
        customer.is_pregnant = customer_data.get('is_pregnant', False)
        customer.has_cancer = customer_data.get('has_cancer', False)
        customer.has_blood_clots = customer_data.get('has_blood_clots', False)
        customer.has_infectious_disease = customer_data.get('has_infectious_disease', False)
        customer.has_bp_issues = customer_data.get('has_bp_issues', False)
        customer.has_severe_pain = customer_data.get('has_severe_pain', False)
        customer.newsletter_subscribed = customer_data.get('newsletter_subscribed', False)
        customer.accepted_terms = customer_data.get('accepted_terms', True)
        customer.updated_at = datetime.utcnow()

        db.session.commit()
        logger.info(f"Updated Latepoint customer {customer.id}")
        return True, None

    except IntegrityError as e:
        db.session.rollback()
        error_msg = f"Database integrity error while updating Latepoint customer: {str(e)}"
        logger.error(error_msg)
        handle_error(e, error_msg)
        return False, "Customer could not be updated due to data conflict"

    except Exception as e:
        db.session.rollback()
        error_msg = f"Error updating Latepoint customer: {str(e)}"
        logger.error(error_msg)
        handle_error(e, error_msg)
        return False, str(e)

def update_square_customer(customer_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Update customer with Square data.

    Args:
        customer_data: Dictionary containing updated customer information

    Returns:
        tuple[bool, Optional[str]]: Success flag and error message if any
    """
    try:
        customer = Customer.query.filter_by(email=customer_data['email'].lower().strip()).first()
        if not customer:
            return False, "Customer not found"

        # Update Square-specific fields
        customer.square_id = customer_data['square_id']
        customer.first_name = customer_data['first_name']
        customer.last_name = customer_data['last_name']
        if customer_data.get('phone'):
            customer.phone = customer_data['phone']
        if customer_data.get('location'):
            customer.location = customer_data['location']
        if customer_data.get('postcode'):
            customer.postcode = customer_data['postcode']
        customer.updated_at = datetime.utcnow()

        db.session.commit()
        logger.info(f"Updated Square customer {customer.id}")
        return True, None

    except IntegrityError as e:
        db.session.rollback()
        error_msg = f"Database integrity error while updating Square customer: {str(e)}"
        logger.error(error_msg)
        handle_error(e, error_msg)
        return False, "Customer could not be updated due to data conflict"

    except Exception as e:
        db.session.rollback()
        error_msg = f"Error updating Square customer: {str(e)}"
        logger.error(error_msg)
        handle_error(e, error_msg)
        return False, str(e)