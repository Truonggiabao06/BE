from datetime import datetime
from typing import Optional
from enum import Enum
from decimal import Decimal

class FeeType(Enum):
    """Types of fees in the auction system"""
    PLATFORM_FEE = "platform_fee"          # Phí nền tảng
    PAYMENT_PROCESSING = "payment_processing"  # Phí xử lý thanh toán
    LISTING_FEE = "listing_fee"             # Phí đăng bán
    SUCCESS_FEE = "success_fee"             # Phí thành công

class FeeAppliedTo(Enum):
    """Who pays the fee"""
    BUYER = "buyer"      # Người mua trả
    SELLER = "seller"    # Người bán trả
    BOTH = "both"        # Cả hai trả

class FeeConfig:
    """Domain model for fee configuration"""

    def __init__(
        self,
        id: Optional[int] = None,
        fee_type: FeeType = FeeType.PLATFORM_FEE,
        name: str = "",
        description: str = "",
        rate: Decimal = Decimal('0.00'),  # Tỷ lệ phí (0.05 = 5%)
        fixed_amount: Optional[Decimal] = None,  # Số tiền cố định
        min_amount: Optional[Decimal] = None,    # Số tiền tối thiểu
        max_amount: Optional[Decimal] = None,    # Số tiền tối đa
        applied_to: FeeAppliedTo = FeeAppliedTo.BUYER,
        is_active: bool = True,
        created_by: Optional[int] = None,  # Manager ID who created
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.fee_type = fee_type
        self.name = name
        self.description = description
        self.rate = rate
        self.fixed_amount = fixed_amount
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.applied_to = applied_to
        self.is_active = is_active
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def calculate_fee(self, amount: Decimal) -> Decimal:
        """Calculate fee based on amount"""
        if not self.is_active:
            return Decimal('0.00')
        
        # Calculate based on rate
        calculated_fee = amount * self.rate
        
        # Add fixed amount if specified
        if self.fixed_amount:
            calculated_fee += self.fixed_amount
        
        # Apply min/max limits
        if self.min_amount and calculated_fee < self.min_amount:
            calculated_fee = self.min_amount
        
        if self.max_amount and calculated_fee > self.max_amount:
            calculated_fee = self.max_amount
        
        return calculated_fee

    def update_config(self, **kwargs):
        """Update fee configuration"""
        allowed_fields = [
            'name', 'description', 'rate', 'fixed_amount', 
            'min_amount', 'max_amount', 'applied_to', 'is_active'
        ]
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        self.updated_at = datetime.utcnow()

    def activate(self):
        """Activate fee configuration"""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self):
        """Deactivate fee configuration"""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<FeeConfig(id={self.id}, type='{self.fee_type.value}', rate={self.rate})>"
