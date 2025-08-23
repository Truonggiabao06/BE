from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.databases.base import Base
from src.domain.models.user import UserRole, UserStatus

class UserModel(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Basic information
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(256), nullable=False, unique=True, index=True)
    phone_number = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)

    # Role and status (using string values for SQL Server compatibility)
    role = Column(String(20), nullable=False, default='buyer')
    status = Column(String(30), nullable=False, default='pending_verification')

    # Profile information
    bio = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    address = Column(Text, nullable=True)

    # Verification
    is_email_verified = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    auction_items = relationship("AuctionItemModel", foreign_keys="AuctionItemModel.seller_id", back_populates="seller")
    created_sessions = relationship("AuctionSessionModel", back_populates="creator")
    bids = relationship("BidModel", back_populates="bidder")
    buyer_payments = relationship("PaymentModel", foreign_keys="PaymentModel.buyer_id", back_populates="buyer")
    seller_payments = relationship("PaymentModel", foreign_keys="PaymentModel.seller_id", back_populates="seller")
    verification_codes = relationship("VerificationCodeModel", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UserModel(id={self.id}, email='{self.email}', role='{self.role.value}')>"