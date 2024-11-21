from sqlalchemy import Column, Integer, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

class OrderLineItem(db.Model):
    """
    Order line item model representing individual items in an order.
    """
    __tablename__ = "order_line_items"

    id = Column(Integer, primary_key=True)
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    item_id = Column(
        Integer,
        ForeignKey("items.id", ondelete="RESTRICT"),
        nullable=False
    )
    quantity = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Quantity of the item purchased"
    )
    price = Column(
        Integer,
        nullable=False,
        comment="Price of the item for this order in cents"
    )
    total = Column(
        Integer,
        nullable=False,
        comment="Total price for this line item (price * quantity), in cents"
    )
    add_ons = Column(
        JSON,
        comment="Optional JSON field for storing additional details like booking add-ons or service extras"
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
    order = relationship("Order", back_populates="line_items")
    item = relationship("Item")
    appointment = relationship("Appointment", back_populates="line_item", uselist=False)

    # Constraints
    __table_args__ = (
        db.CheckConstraint(quantity > 0, name="check_positive_quantity"),
        db.CheckConstraint(price >= 0, name="check_positive_price"),
        db.CheckConstraint(total >= 0, name="check_positive_total"),
    )

    def __repr__(self):
        return (
            f"<OrderLineItem("
            f"id={self.id}, "
            f"order_id={self.order_id}, "
            f"item_id={self.item_id}, "
            f"quantity={self.quantity}, "
            f"total={self.total}"
            f")>"
        )