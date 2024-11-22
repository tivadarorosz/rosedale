from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db


class Location(db.Model):
    """
    Location model representing service locations/branches.
    """
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    address = Column(String(255), nullable=False)
    email = Column(String(100))
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
    appointments = relationship("Appointment", back_populates="location")

    # Indexes and Constraints
    __table_args__ = (
        db.Index('idx_location_name', name),
        db.CheckConstraint(
            db.func.length(name) >= 3,
            name="check_name_length"
        ),
        db.CheckConstraint(
            db.func.length(address) >= 10,
            name="check_address_length"
        ),
    )

    def __repr__(self):
        return f"<Location(id={self.id}, name={self.name}, address={self.address})>"

    @property
    def active_appointments(self):
        """Get all active (non-cancelled) appointments at this location."""
        return [apt for apt in self.appointments if apt.status != 'cancelled']

    @property
    def upcoming_appointments(self):
        """Get all upcoming appointments at this location."""
        from datetime import datetime
        return [
            apt for apt in self.appointments
            if apt.start_datetime > datetime.now(apt.start_datetime.tzinfo)
               and apt.status != 'cancelled'
        ]

    def get_appointments_for_date(self, date):
        """
        Get all appointments for a specific date at this location.

        Args:
            date: datetime.date object
        Returns:
            list: List of appointments for the given date
        """
        return [
            apt for apt in self.appointments
            if apt.start_datetime.date() == date
               and apt.status != 'cancelled'
        ]

    def is_available(self, start_datetime, duration_minutes):
        """
        Check if the location is available for a given time slot.

        Args:
            start_datetime: datetime object for the start time
            duration_minutes: int, duration of the appointment in minutes
        Returns:
            bool: True if the location is available, False otherwise
        """
        from datetime import timedelta
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)

        # Get existing appointments that overlap with the requested time slot
        overlapping = [
            apt for apt in self.active_appointments
            if (apt.start_datetime < end_datetime and
                apt.end_datetime > start_datetime)
        ]

        return len(overlapping) == 0