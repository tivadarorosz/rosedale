from typing import Optional, Dict, Any, Tuple
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from datetime import datetime
from models import Order, Customer
from src.utils.error_monitoring import handle_error
from app import db

logger = logging.getLogger(__name__)


def create_order(order_data: Dict[str, Any]) -> Tuple[Optional[int], Optional[str]]:
    """
    Create a new order in the database.

    Args:
        order_data (Dict[str, Any]): Dictionary containing order information
            Required fields:
            - customer_id (int)
            - source (str): 'square', 'latepoint', 'admin', or 'acuity'
            - payment_status (str)
            - subtotal (float)
            - total (float)

    Returns:
        tuple[Optional[int], Optional[str]]: Tuple containing:
            - order_id if successful, None if failed
            - error message if failed, None if successful

    Example:
        order_data = {
            "customer_id": 123,
            "source": "latepoint",
            "confirmation_code": "LP-123456",
            "latepoint_order_id": 789,
            "status": "open",
            "payment_status": "not_paid",
            "subtotal": 80.00,
            "total": 80.00
        }
        order_id, error = create_order(order_data)
    """
    try:
        # Validate required fields
        required_fields = ['customer_id', 'source', 'payment_status', 'subtotal', 'total']
        missing_fields = [field for field in required_fields if field not in order_data]
        if missing_fields:
            return None, f"Missing required fields: {', '.join(missing_fields)}"

        # Validate source
        valid_sources = {'square', 'latepoint', 'admin', 'acuity'}
        if order_data['source'] not in valid_sources:
            return None, f"Invalid source. Must be one of: {', '.join(valid_sources)}"

        # Validate amounts
        if order_data['subtotal'] < 0 or order_data['total'] < 0:
            return None, "Amounts cannot be negative"

        # Check if customer exists
        if not Customer.query.get(order_data['customer_id']):
            return None, "Customer not found"

        # Create new order instance
        new_order = Order(
            confirmation_code=order_data.get('confirmation_code'),
            customer_id=order_data['customer_id'],
            source=order_data['source'],
            latepoint_order_id=order_data.get('latepoint_order_id'),
            square_order_id=order_data.get('square_order_id'),
            status=order_data.get('status', 'open'),
            fulfillment_status=order_data.get('fulfillment_status', 'not_fulfilled'),
            payment_status=order_data['payment_status'],
            subtotal=order_data['subtotal'],
            total=order_data['total'],
            notes=order_data.get('notes'),
            customer_comment=order_data.get('customer_comment')
        )

        db.session.add(new_order)
        db.session.commit()

        logger.info(f"Created new order with ID {new_order.id}")
        return new_order.id, None

    except IntegrityError as e:
        db.session.rollback()
        error_msg = "Database integrity error while creating order"
        logger.error(f"{error_msg}: {str(e)}")
        handle_error(e, error_msg)
        return None, "Order could not be created due to data conflict"

    except Exception as e:
        db.session.rollback()
        error_msg = "Unexpected error while creating order"
        logger.error(f"{error_msg}: {str(e)}")
        handle_error(e, error_msg)
        return None, str(e)


def update_order(order_id: int, update_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Update an existing order.

    Args:
        order_id (int): ID of the order to update
        update_data (Dict[str, Any]): Dictionary containing fields to update

    Returns:
        tuple[bool, Optional[str]]: Tuple containing:
            - True if successful, False if failed
            - error message if failed, None if successful

    Example:
        update_data = {
            "status": "completed",
            "payment_status": "fully_paid",
            "fulfillment_status": "fulfilled"
        }
        success, error = update_order(order_id, update_data)
    """
    try:
        order = Order.query.get(order_id)
        if not order:
            return False, "Order not found"

        # Protected fields that cannot be updated
        protected_fields = {'id', 'created_at', 'customer_id', 'source'}

        # Validate status updates
        if 'status' in update_data:
            valid_statuses = {'open', 'cancelled', 'completed'}
            if update_data['status'] not in valid_statuses:
                return False, f"Invalid status. Must be one of: {', '.join(valid_statuses)}"

        if 'payment_status' in update_data:
            valid_payment_statuses = {'not_paid', 'partially_paid', 'fully_paid', 'processing'}
            if update_data['payment_status'] not in valid_payment_statuses:
                return False, f"Invalid payment status. Must be one of: {', '.join(valid_payment_statuses)}"

        if 'fulfillment_status' in update_data:
            valid_fulfillment_statuses = {'fulfilled', 'not_fulfilled', 'partially_fulfilled'}
            if update_data['fulfillment_status'] not in valid_fulfillment_statuses:
                return False, f"Invalid fulfillment status. Must be one of: {', '.join(valid_fulfillment_statuses)}"

        # Update allowed fields
        for field, value in update_data.items():
            if field not in protected_fields and hasattr(order, field):
                setattr(order, field, value)

        order.updated_at = datetime.utcnow()
        db.session.commit()

        logger.info(f"Updated order {order_id} with fields: {update_data.keys()}")
        return True, None

    except IntegrityError as e:
        db.session.rollback()
        error_msg = f"Database integrity error while updating order {order_id}"
        logger.error(f"{error_msg}: {str(e)}")
        handle_error(e, error_msg)
        return False, "Order could not be updated due to data conflict"

    except Exception as e:
        db.session.rollback()
        error_msg = f"Unexpected error while updating order {order_id}"
        logger.error(f"{error_msg}: {str(e)}")
        handle_error(e, error_msg)
        return False, str(e)


def get_order_by_confirmation_code(confirmation_code: str, source: str) -> Optional[Order]:
    """
    Get order by confirmation code and source.

    Args:
        confirmation_code (str): Order confirmation code
        source (str): Order source

    Returns:
        Optional[Order]: Order if found, None otherwise
    """
    try:
        return Order.query.filter_by(
            confirmation_code=confirmation_code,
            source=source
        ).first()
    except Exception as e:
        logger.error(f"Error retrieving order with confirmation code {confirmation_code}: {str(e)}")
        handle_error(e, f"Error retrieving order with confirmation code {confirmation_code}")
        return None


def update_order_status(
        order_id: int,
        status: str,
        payment_status: Optional[str] = None,
        fulfillment_status: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Update order statuses.

    Args:
        order_id (int): Order ID
        status (str): New order status
        payment_status (Optional[str]): New payment status
        fulfillment_status (Optional[str]): New fulfillment status

    Returns:
        tuple[bool, Optional[str]]: Success flag and error message if any
    """
    update_data = {'status': status}
    if payment_status:
        update_data['payment_status'] = payment_status
    if fulfillment_status:
        update_data['fulfillment_status'] = fulfillment_status

    return update_order(order_id, update_data)

def process_order_webhook(data, source):
    """
    Processes webhook data to create or update an order.

    Args:
        data (dict): Webhook payload.
        source (str): Source of the webhook ('latepoint' or 'square').

    Returns:
        Order: The created or updated Order object.
    """
    # Map fields based on the source
    if source == "latepoint":
        order_data = {
            "confirmation_code": data.get("confirmation_code"),
            "customer_id": get_customer_id(data, "latepoint"),
            "source": source,
            "latepoint_order_id": int(data.get("id", 0)),
            "status": data.get("status", "open"),
            "fulfillment_status": data.get("fulfillment_status", "not_fulfilled"),
            "payment_status": data.get("payment_status", "not_paid"),
            "subtotal": parse_amount(data.get("subtotal", "0")),
            "total": parse_amount(data.get("total", "0")),
        }
    elif source == "square":
        order_data = {
            "confirmation_code": data.get("receipt_number", ""),
            "customer_id": get_customer_id({"id": data.get("customer_id")}, "square"),
            "source": source,
            "square_order_id": data.get("id"),
            "status": data["status"].lower(),
            "fulfillment_status": "fulfilled" if data["status"] == "COMPLETED" else "not_fulfilled",
            "payment_status": "fully_paid" if data["status"] == "COMPLETED" else "processing",
            "subtotal": data["amount_money"]["amount"] / 100.0,
            "total": data["approved_money"]["amount"] / 100.0,
        }

    # Check if the order exists
    existing_order = Order.query.filter_by(
        confirmation_code=order_data["confirmation_code"], source=source
    ).first()

    if existing_order:
        # Update existing order
        for key, value in order_data.items():
            setattr(existing_order, key, value)
        db.session.commit()
        return existing_order
    else:
        # Create new order
        new_order = Order(**order_data)
        db.session.add(new_order)
        db.session.commit()
        return new_order

def get_customer_id(data, source):
    """
    Retrieves or creates a customer ID.

    Args:
        data (dict): Customer information from the webhook payload.
        source (str): Source of the customer data ('latepoint' or 'square').

    Returns:
        int: The customer ID.
    """
    if source == "latepoint":
        existing_customer = Customer.query.filter_by(latepoint_id=data["customer"]["id"]).first()
        if not existing_customer:
            new_customer = Customer(
                latepoint_id=data["customer"]["id"],
                first_name=data["customer"]["first_name"],
                last_name=data["customer"]["last_name"],
                email=data["customer"]["email"],
                phone=data["customer"].get("phone"),
                source="latepoint",
            )
            db.session.add(new_customer)
            db.session.commit()
            return new_customer.id
        return existing_customer.id

    elif source == "square":
        existing_customer = Customer.query.filter_by(square_id=data["id"]).first()
        if not existing_customer:
            new_customer = Customer(
                square_id=data["id"],
                source="square",
            )
            db.session.add(new_customer)
            db.session.commit()
            return new_customer.id
        return existing_customer.id

def parse_amount(amount_str):
    """
    Converts a string amount (e.g., '£80') into a float.

    Args:
        amount_str (str): The amount string.

    Returns:
        float: Parsed amount.
    """
    return float(amount_str.replace("£", "").strip())