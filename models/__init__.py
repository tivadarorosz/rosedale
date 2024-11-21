# Import all models for easy access
from models.customer import Customer
from models.order import Order
from models.order_line_item import OrderLineItem
from models.transaction import Transaction
from models.item import Item
from models.appointment import Appointment
from models.agent import Agent
from models.location import Location

# Define which models should be available when importing from models
__all__ = [
    'Customer',
    'Order',
    'OrderLineItem',
    'Transaction',
    'Item',
    'Appointment',
    'Agent',
    'Location',
]