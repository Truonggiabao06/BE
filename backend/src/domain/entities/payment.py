"""
Payment entity for the Jewelry Auction System
"""
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from datetime import datetime
from domain.enums import PaymentStatus, PaymentMethod


@dataclass
class Payment:
    """Payment entity representing a payment transaction"""
    
    id: Optional[int] = None
    buyer_id: int = None
    session_item_id: int = None
    amount: Decimal = None
    fee_amount: Decimal = None
    total_amount: Decimal = None
    payment_method: PaymentMethod = None
    status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    payment_gateway_response: Optional[str] = None
    payment_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post initialization validation"""
        if self.amount and self.amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        if self.fee_amount and self.fee_amount < 0:
            raise ValueError("Fee amount cannot be negative")
        
        if self.total_amount and self.total_amount <= 0:
            raise ValueError("Total amount must be positive")
    
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status == PaymentStatus.PENDING
    
    def is_processing(self) -> bool:
        """Check if payment is being processed"""
        return self.status == PaymentStatus.PROCESSING
    
    def is_completed(self) -> bool:
        """Check if payment is completed"""
        return self.status == PaymentStatus.COMPLETED
    
    def is_failed(self) -> bool:
        """Check if payment failed"""
        return self.status == PaymentStatus.FAILED
    
    def is_refunded(self) -> bool:
        """Check if payment was refunded"""
        return self.status == PaymentStatus.REFUNDED
    
    def is_cancelled(self) -> bool:
        """Check if payment was cancelled"""
        return self.status == PaymentStatus.CANCELED
    
    def is_overdue(self) -> bool:
        """Check if payment is overdue"""
        if not self.due_date:
            return False
        return datetime.utcnow() > self.due_date and not self.is_completed()
    
    def complete_payment(self, transaction_id: str, gateway_response: Optional[str] = None) -> None:
        """Mark payment as completed"""
        self.status = PaymentStatus.COMPLETED
        self.transaction_id = transaction_id
        self.payment_gateway_response = gateway_response
        self.payment_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def fail_payment(self, reason: str) -> None:
        """Mark payment as failed"""
        self.status = PaymentStatus.FAILED
        self.notes = reason
        self.updated_at = datetime.utcnow()
    
    def cancel_payment(self, reason: Optional[str] = None) -> None:
        """Cancel the payment"""
        self.status = PaymentStatus.CANCELED
        if reason:
            self.notes = reason
        self.updated_at = datetime.utcnow()
    
    def refund_payment(self, reason: Optional[str] = None) -> None:
        """Refund the payment"""
        if not self.is_completed():
            raise ValueError("Can only refund completed payments")
        
        self.status = PaymentStatus.REFUNDED
        if reason:
            self.notes = f"Refunded: {reason}"
        self.updated_at = datetime.utcnow()
    
    def calculate_total(self) -> Decimal:
        """Calculate total amount including fees"""
        if not self.amount:
            return Decimal('0')
        
        fee = self.fee_amount or Decimal('0')
        return self.amount + fee
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'session_item_id': self.session_item_id,
            'amount': float(self.amount) if self.amount else None,
            'fee_amount': float(self.fee_amount) if self.fee_amount else None,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'payment_method': self.payment_method.value if self.payment_method else None,
            'status': self.status.value if self.status else None,
            'transaction_id': self.transaction_id,
            'payment_gateway_response': self.payment_gateway_response,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
