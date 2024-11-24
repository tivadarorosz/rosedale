from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from src.extensions import db
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Customer(db.Model):
    __tablename__ = "customers"

    # Primary Key
    id = db.Column(db.Integer, primary_key=True)

    # External System IDs
    booking_system_id = db.Column(db.Integer, unique=True, nullable=True, comment="LatePoint ID or equivalent")
    payment_system_id = db.Column(db.Text, unique=True, nullable=True, comment="Square ID or equivalent")

    # Customer Info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    gender = db.Column(
        db.String(10),
        nullable=True,
        comment="Values: Male, Female, Non-Binary, Prefer Not to Say"
    )
    birthdate = db.Column(db.Date, nullable=True)

    # Address (JSONB Format)
    address = db.Column(
        JSONB,
        nullable=True,
        comment="Structured address data in JSON format"
    )

    # Preferences (JSONB Format)
    massage_preferences = db.Column(
        JSONB,
        nullable=True,
        comment="Session preferences including aromatherapy, music, etc."
    )

    # Source of Customer Record
    signup_source = db.Column(
        db.String(20),
        nullable=False,
        default="admin",
        comment="Allowed values: 'admin', 'latepoint', 'square', 'acuity'"
    )

    # Timestamps
    created_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        nullable=False,
        comment="Record creation timestamp"
    )

    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Record last updated timestamp"
    )

    # Relationships
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="customer", cascade="all, delete-orphan")

    # Constraints to enforce booking_system_id or payment_system_id
    __table_args__ = (
        db.CheckConstraint(
            "(booking_system_id IS NOT NULL OR payment_system_id IS NOT NULL)",
            name="check_booking_or_payment_id"
        ),
    )

    # Dynamic Full Name Property
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Customer {self.full_name} (ID: {self.id})>"