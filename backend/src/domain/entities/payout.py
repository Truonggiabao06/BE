"""
Payout entity for the Jewelry Auction System
"""
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from datetime import datetime
from domain.enums import PayoutStatus, PaymentMethod


@dataclass
class Payout:
    """Payout entity representing a payment to sellers"""
    
    id: Optional[int] = None
    seller_id: int = None
    session_item_id: int = None
    gross_amount: Decimal = None
    fee_amount: Decimal = None
    net_amount: Decimal = None
    payment_method: PaymentMethod = None
    status: PayoutStatus = PayoutStatus.PENDING
    transaction_id: Optional[str] = None
    payment_gateway_response: Optional[str] = None
    payout_date: Optional[datetime] = None
    scheduled_date: Optional[datetime] = None
    bank_account_info: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post initialization validation"""
        if self.gross_amount and self.gross_amount <= 0:
            raise ValueError("Gross amount must be positive")
        
        if self.fee_amount and self.fee_amount < 0:
            raise ValueError("Fee amount cannot be negative")
        
        if self.net_amount and self.net_amount <= 0:
            raise ValueError("Net amount must be positive")
    
    def is_pending(self) -> bool:
        """Check if payout is pending"""
        return self.status == PayoutStatus.PENDING
    
    def is_processing(self) -> bool:
        """Check if payout is being processed"""
        return self.status == PayoutStatus.PROCESSING
    
    def is_completed(self) -> bool:
        """Check if payout is completed"""
        return self.status == PayoutStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if payout failed"""
        return self.status == PayoutStatus.FAILED
    
    def is_cancelled(self) -> bool:
        """Check if payout was cancelled"""
        return self.status == PayoutStatus.CANCELED
    
    def is_overdue(self) -> bool:
        """Check if payout is overdue"""
        if not self.scheduled_date:
            return False
        return datetime.utcnow() > self.scheduled_date and not self.is_completed()
    
    def complete_payout(self, transaction_id: str, gateway_response: Optional[str] = None) -> None:
        """Mark payout as completed"""
        self.status = PayoutStatus.COMPLETED
        self.transaction_id = transaction_id
        self.payment_gateway_response = gateway_response
        self.payout_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def fail_payout(self, reason: str) -> None:
        """Mark payout as failed"""
        self.status = PayoutStatus.FAILED
        self.notes = reason
        self.updated_at = datetime.utcnow()
    
    def cancel_payout(self, reason: Optional[str] = None) -> None:
        """Cancel the payout"""
        self.status = PayoutStatus.CANCELED
        if reason:
            self.notes = reason
        self.updated_at = datetime.utcnow()
    
    def start_processing(self) -> None:
        """Mark payout as processing"""
        if not self.is_pending():
            raise ValueError("Can only process pending payouts")
        
        self.status = PayoutStatus.PROCESSING
        self.updated_at = datetime.utcnow()
    
    def calculate_net_amount(self) -> Decimal:
        """Calculate net amount after fees"""
        if not self.gross_amount:
            return Decimal('0')
        
        fee = self.fee_amount or Decimal('0')
        return self.gross_amount - fee
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'seller_id': self.seller_id,
            'session_item_id': self.session_item_id,
            'gross_amount': float(self.gross_amount) if self.gross_amount else None,
            'fee_amount': float(self.fee_amount) if self.fee_amount else None,
            'net_amount': float(self.net_amount) if self.net_amount else None,
            'payment_method': self.payment_method.value if self.payment_method else None,
            'status': self.status.value if self.status else None,
            'transaction_id': self.transaction_id,
            'payment_gateway_response': self.payment_gateway_response,
            'payout_date': self.payout_date.isoformat() if self.payout_date else None,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'bank_account_info': self.bank_account_info,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
