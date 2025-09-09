"""
Auction SQLAlchemy models for the Jewelry Auction System
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, DECIMAL, JSON, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from infrastructure.databases.mssql import db
from domain.enums import SessionStatus, BidStatus, EnrollmentStatus
from datetime import datetime
import uuid


class AuctionSessionModel(db.Model):
    """Auction Session database model"""
    __tablename__ = 'auction_sessions'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Schedule
    start_at = Column(DateTime, nullable=True)
    end_at = Column(DateTime, nullable=True)
    
    # Status and management
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.DRAFT)
    assigned_staff_id = Column(String(36), ForeignKey('users.id'), nullable=True, index=True)
    rules = Column(JSON, nullable=True)  # Session-specific rules
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    opened_at = Column(DateTime, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    settled_at = Column(DateTime, nullable=True)
    
    # Relationships
    assigned_staff = relationship("UserModel", back_populates="managed_sessions", foreign_keys=[assigned_staff_id])
    session_items = relationship("SessionItemModel", back_populates="session")
    enrollments = relationship("EnrollmentModel", back_populates="session")
    bids = relationship("BidModel", back_populates="session")
    
    def __repr__(self):
        return f"<AuctionSessionModel(id={self.id}, code={self.code}, name={self.name})>"


class SessionItemModel(db.Model):
    """Session Item database model (jewelry item in auction session)"""
    __tablename__ = 'session_items'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey('auction_sessions.id'), nullable=False, index=True)
    jewelry_item_id = Column(String(36), ForeignKey('jewelry_items.id'), nullable=False, index=True)
    
    # Pricing
    reserve_price = Column(DECIMAL(12, 2), nullable=True)
    start_price = Column(DECIMAL(12, 2), nullable=False, default=1.00)
    step_price = Column(DECIMAL(12, 2), nullable=False, default=1.00)
    
    # Auction details
    lot_number = Column(Integer, nullable=False)
    current_highest_bid = Column(DECIMAL(12, 2), nullable=True)
    current_winner_id = Column(String(36), ForeignKey('users.id'), nullable=True, index=True)
    bid_count = Column(Integer, nullable=False, default=0)

    # Optimistic locking for concurrent bidding
    version = Column(Integer, nullable=False, default=1)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("AuctionSessionModel", back_populates="session_items", foreign_keys=[session_id])
    jewelry_item = relationship("JewelryItemModel", back_populates="session_items", foreign_keys=[jewelry_item_id])
    current_winner = relationship("UserModel", foreign_keys=[current_winner_id])
    bids = relationship("BidModel", back_populates="session_item")
    payments = relationship("PaymentModel", back_populates="session_item")
    payouts = relationship("PayoutModel", back_populates="session_item")
    
    def __repr__(self):
        return f"<SessionItemModel(id={self.id}, lot_number={self.lot_number}, current_highest_bid={self.current_highest_bid})>"


class BidModel(db.Model):
    """Bid database model"""
    __tablename__ = 'bids'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey('auction_sessions.id'), nullable=False, index=True)
    session_item_id = Column(String(36), ForeignKey('session_items.id'), nullable=False, index=True)
    bidder_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Bid details
    amount = Column(DECIMAL(12, 2), nullable=False)
    placed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_auto = Column(Boolean, nullable=False, default=False)
    status = Column(Enum(BidStatus), nullable=False, default=BidStatus.VALID)

    # Idempotency for duplicate prevention
    idempotency_key = Column(String(100), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("AuctionSessionModel", back_populates="bids", foreign_keys=[session_id])
    session_item = relationship("SessionItemModel", back_populates="bids", foreign_keys=[session_item_id])
    bidder = relationship("UserModel", back_populates="bids", foreign_keys=[bidder_id])
    
    def __repr__(self):
        return f"<BidModel(id={self.id}, bidder_id={self.bidder_id}, amount={self.amount})>"


class EnrollmentModel(db.Model):
    """Enrollment database model (user enrollment in auction session)"""
    __tablename__ = 'enrollments'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey('auction_sessions.id'), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Enrollment details
    status = Column(Enum(EnrollmentStatus), nullable=False, default=EnrollmentStatus.PENDING)
    approved_by = Column(String(36), ForeignKey('users.id'), nullable=True, index=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    session = relationship("AuctionSessionModel", back_populates="enrollments", foreign_keys=[session_id])
    user = relationship("UserModel", back_populates="enrollments", foreign_keys=[user_id])
    approver = relationship("UserModel", foreign_keys=[approved_by], overlaps="approved_enrollments")
    
    def __repr__(self):
        return f"<EnrollmentModel(id={self.id}, user_id={self.user_id}, session_id={self.session_id})>"
