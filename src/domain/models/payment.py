from datetime import datetime, timedelta
from typing import Optional
from enum import Enum
from decimal import Decimal

class PaymentStatus(Enum):
    """Status of payments"""
    PENDING = "pending"           # Chờ thanh toán
    PROCESSING = "processing"     # Đang xử lý
    COMPLETED = "completed"       # Đã hoàn thành
    FAILED = "failed"            # Thất bại
    CANCELLED = "cancelled"      # Đã hủy
    REFUNDED = "refunded"        # Đã hoàn tiền

class PaymentMethod(Enum):
    """Payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"
    STRIPE = "stripe"
    CASH = "cash"  # For in-person payments

class Payment:
    """Domain model for payments"""

    def __init__(
        self,
        id: Optional[int] = None,
        auction_item_id: int = None,
        winning_bid_id: int = None,
        buyer_id: int = None,
        seller_id: int = None,
        amount: Decimal = Decimal('0.00'),
        service_fee: Decimal = Decimal('0.00'),  # Platform service fee
        seller_fee: Decimal = Decimal('0.00'),   # Fee deducted from seller
        net_amount: Decimal = Decimal('0.00'),   # Amount seller receives
        payment_method: Optional[PaymentMethod] = None,
        status: PaymentStatus = PaymentStatus.PENDING,
        gateway_transaction_id: Optional[str] = None,  # External payment gateway ID
        gateway_response: Optional[str] = None,        # Gateway response data
        payment_deadline: Optional[datetime] = None,   # Deadline for payment
        paid_at: Optional[datetime] = None,
        failed_reason: Optional[str] = None,
        refund_reason: Optional[str] = None,
        refunded_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.auction_item_id = auction_item_id
        self.winning_bid_id = winning_bid_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.amount = amount
        self.service_fee = service_fee
        self.seller_fee = seller_fee
        self.net_amount = net_amount
        self.payment_method = payment_method
        self.status = status
        self.gateway_transaction_id = gateway_transaction_id
        self.gateway_response = gateway_response
        self.payment_deadline = payment_deadline or (datetime.utcnow() + timedelta(days=3))
        self.paid_at = paid_at
        self.failed_reason = failed_reason
        self.refund_reason = refund_reason
        self.refunded_at = refunded_at
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def is_pending(self) -> bool:
        """Check if payment is pending"""
        return self.status == PaymentStatus.PENDING

    @property
    def is_completed(self) -> bool:
        """Check if payment is completed"""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if payment failed"""
        return self.status == PaymentStatus.FAILED

    @property
    def is_overdue(self) -> bool:
        """Check if payment is overdue"""
        return (
            self.status == PaymentStatus.PENDING and
            self.payment_deadline and
            datetime.utcnow() > self.payment_deadline
        )

    @property
    def time_remaining(self) -> Optional[timedelta]:
        """Get remaining time for payment"""
        if self.status != PaymentStatus.PENDING or not self.payment_deadline:
            return None
        remaining = self.payment_deadline - datetime.utcnow()
        return remaining if remaining.total_seconds() > 0 else timedelta(0)

    def calculate_fees(self, service_fee_rate: float = 0.05, seller_fee_rate: float = 0.03):
        """Calculate service fees"""
        self.service_fee = self.amount * Decimal(str(service_fee_rate))
        self.seller_fee = self.amount * Decimal(str(seller_fee_rate))
        self.net_amount = self.amount - self.seller_fee
        self.updated_at = datetime.utcnow()

    def start_processing(self, gateway_transaction_id: str):
        """Mark payment as processing"""
        if self.status != PaymentStatus.PENDING:
            raise ValueError("Can only process pending payments")
        self.status = PaymentStatus.PROCESSING
        self.gateway_transaction_id = gateway_transaction_id
        self.updated_at = datetime.utcnow()

    def complete_payment(self, gateway_response: Optional[str] = None):
        """Mark payment as completed"""
        if self.status != PaymentStatus.PROCESSING:
            raise ValueError("Can only complete processing payments")
        self.status = PaymentStatus.COMPLETED
        self.paid_at = datetime.utcnow()
        self.gateway_response = gateway_response
        self.updated_at = datetime.utcnow()

    def fail_payment(self, reason: str, gateway_response: Optional[str] = None):
        """Mark payment as failed"""
        if self.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise ValueError("Can only fail pending or processing payments")
        self.status = PaymentStatus.FAILED
        self.failed_reason = reason
        self.gateway_response = gateway_response
        self.updated_at = datetime.utcnow()

    def cancel_payment(self):
        """Cancel the payment"""
        if self.status == PaymentStatus.COMPLETED:
            raise ValueError("Cannot cancel completed payment")
        self.status = PaymentStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def refund_payment(self, reason: str):
        """Refund the payment"""
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError("Can only refund completed payments")
        self.status = PaymentStatus.REFUNDED
        self.refund_reason = reason
        self.refunded_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def extend_deadline(self, additional_days: int):
        """Extend payment deadline"""
        if self.status != PaymentStatus.PENDING:
            raise ValueError("Can only extend deadline for pending payments")
        if self.payment_deadline:
            self.payment_deadline += timedelta(days=additional_days)
        else:
            self.payment_deadline = datetime.utcnow() + timedelta(days=additional_days)
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, buyer_id={self.buyer_id}, status='{self.status.value}')>"