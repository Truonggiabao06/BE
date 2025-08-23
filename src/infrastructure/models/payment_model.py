from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.databases.base import Base
from src.domain.models.payment import PaymentStatus, PaymentMethod

class PaymentModel(Base):
    __tablename__ = 'payments'
    __table_args__ = {'extend_existing': True}

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    auction_item_id = Column(Integer, ForeignKey('auction_items.id'), nullable=False, index=True)
    winning_bid_id = Column(Integer, ForeignKey('bids.id'), nullable=False, unique=True)
    buyer_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    seller_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    # Payment amounts
    amount = Column(DECIMAL(12, 2), nullable=False)  # Total amount buyer pays
    service_fee = Column(DECIMAL(12, 2), nullable=False, default=0.00)  # Platform service fee
    seller_fee = Column(DECIMAL(12, 2), nullable=False, default=0.00)   # Fee deducted from seller
    net_amount = Column(DECIMAL(12, 2), nullable=False, default=0.00)   # Amount seller receives

    # Payment details
    payment_method = Column(String(20), nullable=True)
    status = Column(String(20), nullable=False, default='pending', index=True)

    # Gateway integration
    gateway_transaction_id = Column(String(255), nullable=True, unique=True)
    gateway_response = Column(Text, nullable=True)  # Store gateway response data

    # Payment timeline
    payment_deadline = Column(DateTime(timezone=True), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Failure and refund handling
    failed_reason = Column(Text, nullable=True)
    refund_reason = Column(Text, nullable=True)
    refunded_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    auction_item = relationship("AuctionItemModel", back_populates="payments")
    winning_bid = relationship("BidModel", back_populates="winning_payment")
    buyer = relationship("UserModel", foreign_keys=[buyer_id], back_populates="buyer_payments")
    seller = relationship("UserModel", foreign_keys=[seller_id], back_populates="seller_payments")

    def __repr__(self):
        return f"<PaymentModel(id={self.id}, amount={self.amount}, buyer_id={self.buyer_id}, status='{self.status.value}')>"