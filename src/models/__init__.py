# src/models/__init__.py

# Import all models for easy access
from .customer import Customer
from .order import Order
from .appointment import Appointment
from .agent import Agent
from .location import Location
from .item import Item
from .order_line_item import OrderLineItem
from .transaction import Transaction

def load_models():
    """Load and return all models"""
    return {
        'Customer': Customer,
        'Order': Order,
        'Appointment': Appointment,
        'Agent': Agent,
        'Location': Location,
        'Item': Item,
        'OrderLineItem': OrderLineItem,
        'Transaction': Transaction
    }

__all__ = [
    'Customer',
    'Order',
    'Appointment',
    'Agent',
    'Location',
    'Item',
    'OrderLineItem',
    'Transaction',
    'load_models'  # Added this line
]