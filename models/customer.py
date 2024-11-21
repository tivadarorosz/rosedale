from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

class Customer(db.Model):
    """
    Customer model representing client information from various sources.
    """
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    latepoint_id = Column(
        Integer,
        unique=True,
        comment="NULL for Square-only customers"
    )
    square_id = Column(
        String(50),
        unique=True,
        comment="NULL for LatePoint-only customers"
    )
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20))
    gender = Column(String(10))
    dob = Column(Date)
    location = Column(String(100))
    postcode = Column(String(10))
    status = Column(
        String(20),
        nullable=False,
        comment="Allowed values: 'active', 'deleted', 'vip'"
    )
    type = Column(
        String(20),
        nullable=False,
        default='client',
        comment="Allowed values: 'client', 'employee'"
    )
    source = Column(
        String(20),
        nullable=False,
        comment="Allowed values: 'admin', 'latepoint', 'square'"
    )
    is_pregnant = Column(Boolean)
    has_cancer = Column(Boolean)
    has_blood_clots = Column(Boolean)
    has_infectious_disease = Column(Boolean)
    has_bp_issues = Column(Boolean)
    has_severe_pain = Column(Boolean)
    newsletter_subscribed = Column(Boolean, default=False)
    accepted_terms = Column(Boolean, default=True)
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
    orders = relationship("Order", back_populates="customer")
    appointments = relationship("Appointment", back_populates="customer")

    # Constraints
    __table_args__ = (
        db.CheckConstraint(
            status.in_(['active', 'deleted', 'vip']),
            name="check_customer_status"
        ),
        db.CheckConstraint(
            type.in_(['client', 'employee']),
            name="check_customer_type"
        ),
        db.CheckConstraint(
            source.in_(['admin', 'latepoint', 'square']),
            name="check_customer_source"
        ),
    )

    def __repr__(self):
        return f"<Customer(id={self.id}, email={self.email}, status={self.status})>"