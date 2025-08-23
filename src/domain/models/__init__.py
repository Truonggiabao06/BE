# Domain Models package
# Contains business logic models and entities

from .user import User, UserRole, UserStatus
from .auction_item import AuctionItem, ItemCategory, ItemCondition, ItemStatus
from .auction_session import AuctionSession, SessionStatus
from .bid import Bid, BidStatus
from .payment import Payment, PaymentStatus, PaymentMethod
from .verification_code import VerificationCode, VerificationCodeType, VerificationCodeStatus
from .fee_config import FeeConfig, FeeType, FeeAppliedTo
from .notification import Notification, NotificationType, NotificationStatus

__all__ = [
    # Core models
    'User',

    # Auction system models
    'AuctionItem',
    'AuctionSession',
    'Bid',
    'Payment',
    'VerificationCode',
    'FeeConfig',
    'Notification',

    # User enums
    'UserRole',
    'UserStatus',

    # Auction item enums
    'ItemCategory',
    'ItemCondition',
    'ItemStatus',

    # Session enums
    'SessionStatus',

    # Bid enums
    'BidStatus',

    # Payment enums
    'PaymentStatus',
    'PaymentMethod',

    # Verification code enums
    'VerificationCodeType',
    'VerificationCodeStatus',

    # Fee config enums
    'FeeType',
    'FeeAppliedTo',

    # Notification enums
    'NotificationType',
    'NotificationStatus'
]
