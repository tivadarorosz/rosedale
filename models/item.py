from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

class Item(db.Model):
    """
    Item model representing services, products, and gift cards.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    external_id = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Identifier from LatePoint, Square or Acuity"
    )
    name = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Name of the item, e.g., 'Swedish Massage', 'Gift Card'"
    )
    type = Column(
        String(50),
        nullable=False,
        comment="Top-level classification, e.g., 'service', 'gift_card', 'package', 'product'"
    )
    category = Column(
        String(50),
        nullable=False,
        comment="Detailed category, e.g., 'swedish blossom', 'deep tissue'"
    )
    base_price = Column(
        Integer,
        nullable=False,
        comment="Base price of the item in cents"
    )
    duration = Column(
        Integer,
        comment="Duration in minutes, for services"
    )
    description = Column(
        Text,
        comment="Detailed description of the item"
    )
    source = Column(
        String(20),
        nullable=False,
        comment="The origin system: 'latepoint' or 'square'"
    )
    status = Column(
        String(10),
        nullable=False,
        default='active',
        comment="Status of the item: 'active' or 'inactive'"
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
    line_items = relationship("OrderLineItem", back_populates="item")

    # Indexes and Constraints
    __table_args__ = (
        Index('idx_items_external_id', external_id, unique=True),
        Index('idx_items_name', name, unique=True),
        Index('idx_items_source', source),
        Index('idx_items_status', status),
        db.CheckConstraint(
            source.in_(['latepoint', 'square']),
            name="check_item_source"
        ),
        db.CheckConstraint(
            status.in_(['active', 'inactive']),
            name="check_item_status"
        ),
        db.CheckConstraint(
            type.in_(['service', 'gift_card', 'package', 'product']),
            name="check_item_type"
        ),
        db.CheckConstraint(base_price >= 0, name="check_positive_base_price"),
        db.CheckConstraint(
            db.or_(
                duration.is_(None),
                duration > 0
            ),
            name="check_valid_duration"
        ),
    )

    def __repr__(self):
        return f"<Item(id={self.id}, name={self.name}, type={self.type})>"