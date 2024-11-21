from models import Order
from models.customer import Customer
from app import db

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