from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, Index, CheckConstraint
from sqlalchemy.orm import relationship
from src.extensions import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func


class Order(db.Model):
    """
    Order model representing customer orders from various sources.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    confirmation_code = Column(String(50), unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    data_source = Column(  # Keeping original column name
        String(20),
        nullable=False,
        index=True,
        comment="Allowed: 'square', 'latepoint', 'admin', 'acuity'"
    )
    booking_system_order_id = Column(Integer, unique=True)
    payment_system_order_id = Column(String(50), unique=True)
    order_status = Column(  # Keeping original column name
        String(50),
        nullable=False,
        default="open",
        index=True,
        comment="Allowed: 'open', 'cancelled', 'completed'"
    )
    fulfillment_status = Column(
        String(50),
        default="not_fulfilled",
        comment="Allowed: 'fulfilled', 'not_fulfilled', 'partially_fulfilled'"
    )
    payment_status = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Allowed: 'not_paid', 'partially_paid', 'fully_paid', 'processing'"
    )
    subtotal = Column(Numeric(10, 2), nullable=False, comment="Must be >= 0")
    total = Column(Numeric(10, 2), nullable=False, comment="Must be >= 0")
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    line_items = relationship("OrderLineItem", back_populates="order", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="order", cascade="all, delete-orphan")

    # Indexes from schema
    __table_args__ = (
        # Check constraint for order source validation
        CheckConstraint(
            Column('data_source').in_(['square', 'latepoint', 'admin', 'acuity']),
            name='check_order_source'
        ),
        # Check constraint for status validation
        CheckConstraint(
            Column('order_status').in_(['open', 'cancelled', 'completed']),
            name='check_order_status'
        ),
        # Check constraint for fulfillment status validation
        CheckConstraint(
            Column('fulfillment_status').in_(['fulfilled', 'not_fulfilled', 'partially_fulfilled']),
            name='check_fulfillment_status'
        ),
        # Check constraint for payment status validation
        CheckConstraint(
            Column('payment_status').in_(['not_paid', 'partially_paid', 'fully_paid', 'processing']),
            name='check_payment_status'
        ),
        # Check constraint for non-negative amounts
        CheckConstraint('subtotal >= 0', name='check_subtotal_positive'),
        CheckConstraint('total >= 0', name='check_total_positive'),
        # Check constraint for order ID requirement
        CheckConstraint(
            'booking_system_order_id IS NOT NULL OR payment_system_order_id IS NOT NULL',
            name='check_order_id_presence'
        ),
    )

    def __repr__(self):
        return (
            f"<Order("
            f"id={self.id}, "
            f"confirmation_code={self.confirmation_code}, "
            f"source={self.data_source}, "  # Updated to use data_source
            f"status={self.order_status}, "  # Updated to use order_status
            f"total={self.total}"
            f")>"
        )