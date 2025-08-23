from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum as SQLEnum, DECIMAL, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.databases.base import Base
from src.domain.models.auction_item import ItemCategory, ItemCondition, ItemStatus

class AuctionItemModel(Base):
    __tablename__ = 'auction_items'
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    seller_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    approved_by = Column(Integer, ForeignKey('users.id'), nullable=True)

    # Basic information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(20), nullable=False, default='other')
    condition = Column(String(20), nullable=False, default='good')

    # Item details
    material = Column(String(100), nullable=True)  # e.g., "Gold 18K", "Silver 925"
    weight = Column(Float, nullable=True)  # in grams
    dimensions = Column(String(100), nullable=True)  # e.g., "2.5cm x 1.8cm"
    brand = Column(String(100), nullable=True)
    year_made = Column(Integer, nullable=True)
    certificate_number = Column(String(100), nullable=True)

    # Images stored as JSON array of URLs
    images = Column(JSON, nullable=True, default=list)

    # Pricing
    starting_price = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    reserve_price = Column(DECIMAL(12, 2), nullable=True)  # Minimum price to sell
    estimated_value = Column(DECIMAL(12, 2), nullable=True)  # Appraised value

    # Status and workflow
    status = Column(String(30), nullable=False, default='pending_approval', index=True)
    staff_notes = Column(Text, nullable=True)  # Internal notes from staff
    rejection_reason = Column(Text, nullable=True)

    # New fields for pricing workflow
    preliminary_price = Column(DECIMAL(12, 2), nullable=True)  # Định giá sơ bộ
    final_price = Column(DECIMAL(12, 2), nullable=True)        # Định giá cuối cùng
    preliminary_valued_by = Column(Integer, ForeignKey('users.id'), nullable=True)   # Staff ID who did preliminary valuation
    preliminary_valued_at = Column(DateTime(timezone=True), nullable=True)
    final_valued_by = Column(Integer, ForeignKey('users.id'), nullable=True)        # Staff ID who did final valuation
    final_valued_at = Column(DateTime(timezone=True), nullable=True)
    item_received_by = Column(Integer, ForeignKey('users.id'), nullable=True)       # Staff ID who received the item
    item_received_at = Column(DateTime(timezone=True), nullable=True)
    manager_notes = Column(Text, nullable=True)          # Manager's notes

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    seller = relationship("UserModel", foreign_keys=[seller_id], back_populates="auction_items")
    approver = relationship("UserModel", foreign_keys=[approved_by])
    bids = relationship("BidModel", back_populates="auction_item", cascade="all, delete-orphan")
    payments = relationship("PaymentModel", back_populates="auction_item", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AuctionItemModel(id={self.id}, title='{self.title}', status='{self.status.value}')>"