from sqlalchemy import Column, Integer, String, Numeric, Text, ForeignKey, DateTime, Index, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db


class Order(db.Model):
    """
    Order model representing customer orders from various sources.
    """
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    confirmation_code = Column(String(50), unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    source = Column(
        String(20),
        nullable=False,
        index=True,
        comment="Allowed: 'square', 'latepoint', 'admin', 'acuity'"
    )
    latepoint_order_id = Column(Integer, unique=True)
    square_order_id = Column(String(50), unique=True)
    status = Column(
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
    # Changed from Float to Numeric for precise decimal handling
    subtotal = Column(Numeric(10, 2), nullable=False, comment="Must be >= 0")
    total = Column(Numeric(10, 2), nullable=False, comment="Must be >= 0")
    notes = Column(Text)
    customer_comment = Column(Text)
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
        db.CheckConstraint(
            source.in_(['square', 'latepoint', 'admin', 'acuity']),
            name='check_order_source'
        ),
        # Check constraint for status validation
        db.CheckConstraint(
            status.in_(['open', 'cancelled', 'completed']),
            name='check_order_status'
        ),
        # Check constraint for fulfillment status validation
        db.CheckConstraint(
            fulfillment_status.in_(['fulfilled', 'not_fulfilled', 'partially_fulfilled']),
            name='check_fulfillment_status'
        ),
        # Check constraint for payment status validation
        db.CheckConstraint(
            payment_status.in_(['not_paid', 'partially_paid', 'fully_paid', 'processing']),
            name='check_payment_status'
        ),
        # Check constraint for non-negative amounts
        db.CheckConstraint(subtotal >= 0, name='check_subtotal_positive'),
        db.CheckConstraint(total >= 0, name='check_total_positive'),
        # Check constraint for order ID requirement
        db.CheckConstraint(
            db.or_(latepoint_order_id.is_not(None), square_order_id.is_not(None)),
            name='check_order_id_presence'
        ),
    )

    def __repr__(self):
        return (
            f"<Order("
            f"id={self.id}, "
            f"confirmation_code={self.confirmation_code}, "
            f"source={self.source}, "
            f"status={self.status}, "
            f"total={self.total}"
            f")>"
        )