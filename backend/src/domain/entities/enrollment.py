"""
Enrollment entity for the Jewelry Auction System
"""
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from datetime import datetime
from domain.enums import EnrollmentStatus


@dataclass
class Enrollment:
    """Enrollment entity representing a user's registration for an auction session"""
    
    id: Optional[int] = None
    user_id: int = None
    session_id: int = None
    status: EnrollmentStatus = EnrollmentStatus.PENDING
    deposit_amount: Optional[Decimal] = None
    deposit_paid: bool = False
    deposit_payment_date: Optional[datetime] = None
    paddle_number: Optional[str] = None
    enrollment_date: Optional[datetime] = None
    approved_date: Optional[datetime] = None
    approved_by: Optional[int] = None
    rejection_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post initialization validation"""
        if self.deposit_amount and self.deposit_amount <= 0:
            raise ValueError("Deposit amount must be positive")
    
    def is_approved(self) -> bool:
        """Check if the enrollment is approved"""
        return self.status == EnrollmentStatus.APPROVED
    
    def is_pending(self) -> bool:
        """Check if the enrollment is pending approval"""
        return self.status == EnrollmentStatus.PENDING
    
    def is_rejected(self) -> bool:
        """Check if the enrollment is rejected"""
        return self.status == EnrollmentStatus.REJECTED
    
    def is_cancelled(self) -> bool:
        """Check if the enrollment is cancelled"""
        return self.status == EnrollmentStatus.CANCELLED
    
    def has_paid_deposit(self) -> bool:
        """Check if the required deposit has been paid"""
        return self.deposit_paid and self.deposit_payment_date is not None
    
    def approve(self, approved_by: int, paddle_number: str) -> None:
        """Approve the enrollment"""
        if not self.has_paid_deposit():
            raise ValueError("Cannot approve enrollment without deposit payment")
        
        self.status = EnrollmentStatus.APPROVED
        self.approved_by = approved_by
        self.approved_date = datetime.utcnow()
        self.paddle_number = paddle_number
        self.updated_at = datetime.utcnow()
    
    def reject(self, reason: str) -> None:
        """Reject the enrollment"""
        self.status = EnrollmentStatus.REJECTED
        self.rejection_reason = reason
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """Cancel the enrollment"""
        self.status = EnrollmentStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def pay_deposit(self, amount: Decimal) -> None:
        """Record deposit payment"""
        if amount != self.deposit_amount:
            raise ValueError("Payment amount must match required deposit")
        
        self.deposit_paid = True
        self.deposit_payment_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'status': self.status.value if self.status else None,
            'deposit_amount': float(self.deposit_amount) if self.deposit_amount else None,
            'deposit_paid': self.deposit_paid,
            'deposit_payment_date': self.deposit_payment_date.isoformat() if self.deposit_payment_date else None,
            'paddle_number': self.paddle_number,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'approved_date': self.approved_date.isoformat() if self.approved_date else None,
            'approved_by': self.approved_by,
            'rejection_reason': self.rejection_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
