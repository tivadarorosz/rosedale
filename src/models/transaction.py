from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.extensions import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

class Transaction(db.Model):
    """
    Transaction model representing payment transactions for orders.
    """
    __tablename__ = "transactions"

    id = Column(
        String(50),
        primary_key=True,
        comment="Square Transaction ID, linked to orders.transaction_id"
    )
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False
    )
    amount = Column(
        Integer,
        nullable=False,
        comment="Transaction amount in cents"
    )
    payment_method = Column(
        String(50),
        nullable=False,
        comment="e.g., Credit Card, Debit Card"
    )
    status = Column(
        String(50),
        nullable=False,
        comment="e.g., COMPLETED, FAILED"
    )
    card_brand = Column(
        String(50),
        comment="Card type used for payment, e.g., Visa"
    )
    last_4 = Column(
        String(4),
        comment="Last 4 digits of the card used"
    )
    exp_month = Column(
        Integer,
        comment="Card expiration month"
    )
    exp_year = Column(
        Integer,
        comment="Card expiration year"
    )
    receipt_url = Column(
        String(255),
        comment="URL to the Square payment receipt"
    )
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
    order = relationship("Order", back_populates="transactions")

    # Constraints
    __table_args__ = (
        db.CheckConstraint(amount > 0, name="check_positive_amount"),
        db.CheckConstraint(
            status.in_(['COMPLETED', 'FAILED', 'PENDING', 'CANCELLED']),
            name="check_transaction_status"
        ),
    )

    def __repr__(self):
        return (
            f"<Transaction("
            f"id={self.id}, "
            f"order_id={self.order_id}, "
            f"amount={self.amount}, "
            f"status={self.status}"
            f")>"
        )