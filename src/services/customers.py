from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from typing import Optional, Dict, Any, List
import logging
# from datetime import datetime
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
    def create_customer(data: Dict[str, Any]) -> Customer:
        """
        Creates a new Customer object based on the provided data dictionary.

        Args:
            data: A dictionary of attributes for the new Customer.

        Returns:
            The newly created Customer object.
        """

        # Create a new Customer object with the provided data
        customer = Customer(**data)

        # Add the new customer to the session and commit
        db.session.add(customer)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"IntegrityError when creating customer: {str(e)}")
            raise e

        return customer

    @staticmethod
    @handle_exceptions
    def update_customer(customer_id: int, data: Dict[str, Any], fields_to_update: List[str]) -> Optional[Customer]:
        """
        Updates a Customer object with the provided data.

        Args:
            customer_id: The ID of the customer to update.
            data: A dictionary of attributes and their new values.

        Returns:
            The updated Customer object, or None if the customer does not exist.
        """
        try:
            # Retrieve the customer by ID
            customer = Customer.query.filter_by(id=customer_id).one()

            # Update the customer's attributes based on the provided data and fields_to_update
            for field in fields_to_update:
                if field in data:
                    setattr(customer, field, data[field])

            # Commit the changes to the database
            db.session.commit()

            return customer
        except NoResultFound:
            # If the customer does not exist, return None
            return None

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