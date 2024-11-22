# Import all models for easy access
from src.models.order import Order
from src.models.customer import Customer
from src.models.order_line_item import OrderLineItem
from src.models.transaction import Transaction
from src.models.item import Item
from src.models.appointment import Appointment
from src.models.agent import Agent
from src.models.location import Location

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