from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.extensions import db

class Appointment(db.Model):
    """
    Appointment model representing scheduled services.
    """
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    order_line_item_id = Column(
        Integer,
        ForeignKey("order_line_items.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True,
        comment="Links appointment to a specific order line item"
    )
    customer_id = Column(
        Integer,
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False
    )
    booking_code = Column(String(50), nullable=False)
    start_datetime = Column(DateTime(timezone=True), nullable=False)
    end_datetime = Column(DateTime(timezone=True), nullable=False)
    duration = Column(
        Integer,
        nullable=False,
        comment="Duration in minutes"
    )
    agent_id = Column(
        Integer,
        ForeignKey("agents.id", ondelete="RESTRICT"),
        nullable=False
    )
    location_id = Column(
        Integer,
        ForeignKey("locations.id", ondelete="RESTRICT"),
        nullable=False
    )
    status = Column(
        String(50),
        nullable=False,
        comment="Allowed values: 'approved', 'pending_approval', 'cancelled', 'no_show', 'completed'"
    )
    payment_status = Column(
        String(50),
        nullable=False,
        comment="Allowed values: 'not_paid', 'partially_paid', 'fully_paid', 'processing'"
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
    line_item = relationship("OrderLineItem", back_populates="appointment")
    customer = relationship("Customer", back_populates="appointments")
    agent = relationship("Agent")
    location = relationship("Location")

    # Constraints
    __table_args__ = (
        CheckConstraint(duration > 0, name="check_positive_duration"),
        CheckConstraint(
            end_datetime > start_datetime,
            name="check_end_after_start"
        ),
        CheckConstraint(
            status.in_([
                'approved', 'pending_approval', 'cancelled',
                'no_show', 'completed'
            ]),
            name="check_appointment_status"
        ),
        CheckConstraint(
            payment_status.in_([
                'not_paid', 'partially_paid', 'fully_paid', 'processing'
            ]),
            name="check_appointment_payment_status"
        ),
    )

    def __repr__(self):
        return (
            f"<Appointment("
            f"id={self.id}, "
            f"booking_code={self.booking_code}, "
            f"start={self.start_datetime}, "
            f"status={self.status}"
            f")>"
        )