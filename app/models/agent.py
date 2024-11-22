from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

class Agent(db.Model):
    """
    Agent model representing service providers/therapists.
    """
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20))
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
    appointments = relationship("Appointment", back_populates="agent")

    # Constraints
    __table_args__ = (
        db.CheckConstraint(
            db.func.length(first_name) >= 2,
            name="check_first_name_length"
        ),
        db.CheckConstraint(
            db.func.length(last_name) >= 2,
            name="check_last_name_length"
        ),
    )

    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.full_name}, email={self.email})>"

    @property
    def active_appointments(self):
        """Get all active (non-cancelled) appointments for this agent."""
        return [apt for apt in self.appointments if apt.status != 'cancelled']

    @property
    def upcoming_appointments(self):
        """Get all upcoming appointments for this agent."""
        from datetime import datetime
        return [
            apt for apt in self.appointments
            if apt.start_datetime > datetime.now(apt.start_datetime.tzinfo)
            and apt.status != 'cancelled'
        ]