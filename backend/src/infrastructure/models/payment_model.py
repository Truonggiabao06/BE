"""
Payment SQLAlchemy models for the Jewelry Auction System
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, DECIMAL, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from infrastructure.databases.mssql import db
from domain.enums import PaymentStatus, PayoutStatus, PaymentMethod
from datetime import datetime
import uuid


class PaymentModel(db.Model):
    """Payment database model"""
    __tablename__ = 'payments'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    buyer_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    session_item_id = Column(String(36), ForeignKey('session_items.id'), nullable=False, index=True)
    
    # Payment details
    amount = Column(DECIMAL(12, 2), nullable=False)
    method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)
    
    # Payment gateway details
    gateway_transaction_id = Column(String(100), nullable=True)
    gateway_response = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    
    # Additional metadata
    meta = Column(JSON, nullable=True)
    
    # Relationships
    buyer = relationship("UserModel", back_populates="payments", foreign_keys=[buyer_id])
    session_item = relationship("SessionItemModel", back_populates="payments", foreign_keys=[session_item_id])
    refunds = relationship("RefundModel", back_populates="payment")
    
    def __repr__(self):
        return f"<PaymentModel(id={self.id}, buyer_id={self.buyer_id}, amount={self.amount})>"


class PayoutModel(db.Model):
    """Payout database model"""
    __tablename__ = 'payouts'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    seller_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    session_item_id = Column(String(36), ForeignKey('session_items.id'), nullable=False, index=True)
    
    # Payout details
    amount = Column(DECIMAL(12, 2), nullable=False)
    status = Column(Enum(PayoutStatus), nullable=False, default=PayoutStatus.PENDING)
    
    # Bank details
    bank_account_info = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)
    
    # Additional metadata
    meta = Column(JSON, nullable=True)
    
    # Relationships
    seller = relationship("UserModel", back_populates="payouts", foreign_keys=[seller_id])
    session_item = relationship("SessionItemModel", back_populates="payouts", foreign_keys=[session_item_id])
    
    def __repr__(self):
        return f"<PayoutModel(id={self.id}, seller_id={self.seller_id}, amount={self.amount})>"


class TransactionFeeModel(db.Model):
    """Transaction Fee database model"""
    __tablename__ = 'transaction_fees'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Fee structure
    buyer_percentage = Column(DECIMAL(5, 2), nullable=False, default=0.00)  # Percentage fee for buyers
    seller_percentage = Column(DECIMAL(5, 2), nullable=False, default=0.00)  # Percentage fee for sellers
    min_fee = Column(DECIMAL(12, 2), nullable=False, default=0.00)
    max_fee = Column(DECIMAL(12, 2), nullable=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TransactionFeeModel(id={self.id}, name={self.name})>"


class RefundModel(db.Model):
    """Refund database model"""
    __tablename__ = 'refunds'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    payment_id = Column(String(36), ForeignKey('payments.id'), nullable=False, index=True)

    # Refund details
    amount = Column(DECIMAL(12, 2), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)

    # Gateway details
    gateway_refund_id = Column(String(100), nullable=True)
    gateway_response = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    refunded_at = Column(DateTime, nullable=True)

    # Additional metadata
    meta = Column(JSON, nullable=True)

    # Relationships
    payment = relationship("PaymentModel", back_populates="refunds", foreign_keys=[payment_id])

    def __repr__(self):
        return f"<RefundModel(id={self.id}, payment_id={self.payment_id}, amount={self.amount})>"
