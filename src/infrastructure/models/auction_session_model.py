from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Enum as SQLEnum, DECIMAL, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.databases.base import Base
from src.domain.models.auction_session import SessionStatus

class AuctionSessionModel(Base):
    __tablename__ = 'auction_sessions'
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    created_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Basic information
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Session timing
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Session configuration
    min_bid_increment = Column(DECIMAL(10, 2), nullable=False, default=10.00)
    registration_required = Column(Boolean, nullable=False, default=True)
    max_participants = Column(Integer, nullable=True)

    # Items in this session (stored as JSON array of item IDs)
    item_ids = Column(JSON, nullable=True, default=list)

    # Status
    status = Column(String(20), nullable=False, default='scheduled', index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    creator = relationship("UserModel", back_populates="created_sessions")
    bids = relationship("BidModel", back_populates="auction_session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AuctionSessionModel(id={self.id}, title='{self.title}', status='{self.status.value}')>"