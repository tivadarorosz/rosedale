from typing import Optional, Dict, Any
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
import logging
from datetime import datetime
from functools import wraps

from src.models import Customer
from src.core.monitoring import handle_error
from src.extensions import db
from src.utils.gender_api import get_gender

logger = logging.getLogger(__name__)


def handle_exceptions(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IntegrityError as e:
            db.session.rollback()
            handle_error(e, "Database integrity violation")
            raise
        except SQLAlchemyError as e:
            db.session.rollback()
            handle_error(e, "Database operation failed")
            raise
        except Exception as e:
            handle_error(e, "Unexpected error in CustomerService")
            raise

    return wrapper


class CustomerService:
    @staticmethod
    @handle_exceptions
    def get_customer_by_email(email: str) -> Optional[Customer]:
        """
        Retrieve a customer by email.

        Args:
            email: Customer's email address

        Returns:
            Customer object if found, None otherwise
        """
        try:
            return Customer.query.filter_by(email=email).one()
        except NoResultFound:
            return None

    @staticmethod
    @handle_exceptions
    def get_customer_by_booking_system_id(booking_system_id: str) -> Optional[Customer]:
        """
        Retrieve a customer by booking system ID.

        Args:
            booking_system_id: External booking system identifier

        Returns:
            Customer object if found, None otherwise
        """
        try:
            return Customer.query.filter_by(booking_system_id=booking_system_id).one()
        except NoResultFound:
            return None

    @staticmethod
    @handle_exceptions
    def get_customer_by_payment_system_id(payment_system_id: str) -> Optional[Customer]:
        """
        Retrieve a customer by payment system ID.

        Args:
            payment_system_id: External payment system identifier

        Returns:
            Customer object if found, None otherwise
        """
        try:
            return Customer.query.filter_by(payment_system_id=payment_system_id).one()
        except NoResultFound:
            return None

    @staticmethod
    @handle_exceptions
    def create_latepoint_customer(data: Dict[str, Any]) -> Customer:
        """
        Create a new customer from LatePoint data.

        Args:
            data: Dictionary containing customer data with keys:
                - first_name (required)
                - last_name (required)
                - email (required)
                - phone_number (optional)
                - booking_system_id (required)
                - session_preferences (optional)

        Returns:
            Newly created Customer object

        Raises:
            ValueError: If required fields are missing
            IntegrityError: If unique constraints are violated
            SQLAlchemyError: For other database errors
        """
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'booking_system_id']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        try:
            gender = get_gender(data["first_name"])
        except Exception as e:
            logger.error(f"Gender API error: {str(e)}")
            gender = None

        customer = Customer(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone_number=data.get("phone_number"),
            booking_system_id=data["booking_system_id"],
            gender_identity=gender,
            session_preferences=data.get("session_preferences"),
            data_source="latepoint"
        )

        db.session.add(customer)
        db.session.commit()
        logger.info(f"Created new customer: {customer.email}")
        return customer

    @staticmethod
    @handle_exceptions
    def update_latepoint_customer(customer_id: int, data: Dict[str, Any]) -> Optional[Customer]:
        """
        Update an existing customer with LatePoint data.

        Args:
            customer_id: ID of the customer to update
            data: Dictionary containing updated customer data (same fields as create_latepoint_customer)

        Returns:
            Updated Customer object or None if customer not found

        Raises:
            IntegrityError: If unique constraints are violated
            SQLAlchemyError: For other database errors
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            logger.warning(f"Attempted to update non-existent customer ID: {customer_id}")
            return None

        # Update fields if provided in data
        updateable_fields = [
            'first_name', 'last_name', 'email', 'phone_number',
            'booking_system_id', 'primary_address', 'session_preferences'
        ]

        for field in updateable_fields:
            if field in data:
                setattr(customer, field, data[field])

        # Update gender if first name changed
        if 'first_name' in data and data['first_name'] != customer.first_name:
            try:
                customer.gender_identity = get_gender(data['first_name'])
            except Exception as e:
                logger.error(f"Gender API error during update: {str(e)}")

        customer.updated_at = datetime.utcnow()
        db.session.commit()
        logger.info(f"Updated customer: {customer.email}")
        return customer

    @staticmethod
    @handle_exceptions
    def delete_customer(customer_id: int) -> bool:
        """
        Delete a customer by ID.

        Args:
            customer_id: ID of the customer to delete

        Returns:
            bool: True if customer was deleted, False if customer not found

        Raises:
            SQLAlchemyError: For database errors
        """
        customer = Customer.query.get(customer_id)
        if not customer:
            return False

        db.session.delete(customer)
        db.session.commit()
        logger.info(f"Deleted customer ID: {customer_id}")
        return True