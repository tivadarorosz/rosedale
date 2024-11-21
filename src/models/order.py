from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

class Order(db.Model):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    confirmation_code = Column(String(50), unique=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    source = Column(String(20), nullable=False)
    latepoint_order_id = Column(Integer, unique=True)
    square_order_id = Column(String(50), unique=True)
    status = Column(String(50), nullable=False, default="open")
    fulfillment_status = Column(String(50), default="not_fulfilled")
    payment_status = Column(String(50), nullable=False)
    subtotal = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    notes = Column(Text)
    customer_comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, source={self.source}, total={self.total}, status={self.status})>"