from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum, DECIMAL, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.databases.base import Base
from src.domain.models.bid import BidStatus

class BidModel(Base):
    __tablename__ = 'bids'
    __table_args__ = (
        # Composite index for efficient queries
        Index('idx_auction_session_item', 'auction_session_id', 'auction_item_id'),
        Index('idx_bidder_session', 'bidder_id', 'auction_session_id'),
        Index('idx_bid_time', 'bid_time'),
        {'extend_existing': True}
    )

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    auction_session_id = Column(Integer, ForeignKey('auction_sessions.id'), nullable=False, index=True)
    auction_item_id = Column(Integer, ForeignKey('auction_items.id'), nullable=False, index=True)
    bidder_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Bid details
    amount = Column(DECIMAL(12, 2), nullable=False)
    status = Column(String(20), nullable=False, default='active', index=True)
    bid_time = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Auto-bidding features (for future implementation)
    is_auto_bid = Column(Boolean, nullable=False, default=False)
    max_auto_bid = Column(DECIMAL(12, 2), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    auction_session = relationship("AuctionSessionModel", back_populates="bids")
    auction_item = relationship("AuctionItemModel", back_populates="bids")
    bidder = relationship("UserModel", back_populates="bids")
    winning_payment = relationship("PaymentModel", back_populates="winning_bid", uselist=False)

    def __repr__(self):
        return f"<BidModel(id={self.id}, amount={self.amount}, bidder_id={self.bidder_id}, status='{self.status.value}')>"