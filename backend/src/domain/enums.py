"""
Domain enums for the Jewelry Auction System
"""
from enum import Enum


class UserRole(Enum):
    """User roles in the system"""
    GUEST = "GUEST"
    MEMBER = "MEMBER"
    STAFF = "STAFF"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class SellRequestStatus(Enum):
    """Status of sell requests (jewelry consignment)"""
    SUBMITTED = "SUBMITTED"
    PRELIM_APPRAISED = "PRELIM_APPRAISED"
    RECEIVED = "RECEIVED"
    FINAL_APPRAISED = "FINAL_APPRAISED"
    MANAGER_APPROVED = "MANAGER_APPROVED"
    SELLER_ACCEPTED = "SELLER_ACCEPTED"
    ASSIGNED_TO_SESSION = "ASSIGNED_TO_SESSION"
    REJECTED = "REJECTED"


class SessionStatus(Enum):
    """Status of auction sessions"""
    DRAFT = "DRAFT"
    SCHEDULED = "SCHEDULED"
    OPEN = "OPEN"
    PAUSED = "PAUSED"
    CLOSED = "CLOSED"
    SETTLED = "SETTLED"
    CANCELED = "CANCELED"


class SessionItemStatus(Enum):
    """Status of session items (jewelry items in auction sessions)"""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    UNSOLD = "UNSOLD"
    WITHDRAWN = "WITHDRAWN"


class JewelryStatus(Enum):
    """Status of jewelry items"""
    PENDING_APPRAISAL = "PENDING_APPRAISAL"
    APPRAISED = "APPRAISED"
    APPROVED = "APPROVED"
    IN_AUCTION = "IN_AUCTION"
    SOLD = "SOLD"
    UNSOLD = "UNSOLD"
    RETURNED = "RETURNED"
    WITHDRAWN = "WITHDRAWN"


class BidStatus(Enum):
    """Status of bids"""
    VALID = "VALID"
    INVALID = "INVALID"
    OUTBID = "OUTBID"
    WINNING = "WINNING"


class PaymentStatus(Enum):
    """Status of payments"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"
    CANCELED = "CANCELED"


class PayoutStatus(Enum):
    """Status of payouts to sellers"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class TransactionType(Enum):
    """Types of transactions"""
    PURCHASE = "PURCHASE"
    SALE = "SALE"
    FEE = "FEE"
    REFUND = "REFUND"
    PAYOUT = "PAYOUT"


class EnrollmentStatus(Enum):
    """Status of session enrollments"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELED = "CANCELED"


class NotificationType(Enum):
    """Types of notifications"""
    SELL_REQUEST_UPDATE = "SELL_REQUEST_UPDATE"
    AUCTION_STARTING = "AUCTION_STARTING"
    BID_PLACED = "BID_PLACED"
    AUCTION_WON = "AUCTION_WON"
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    ITEM_SHIPPED = "ITEM_SHIPPED"
    GENERAL = "GENERAL"


class AppraisalType(Enum):
    """Types of appraisals"""
    PRELIMINARY = "PRELIMINARY"
    FINAL = "FINAL"


class PaymentMethod(Enum):
    """Payment methods"""
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    BANK_TRANSFER = "BANK_TRANSFER"
    DIGITAL_WALLET = "DIGITAL_WALLET"
    CASH = "CASH"


class AuditAction(Enum):
    """Actions for audit logging"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    BID_PLACED = "BID_PLACED"
    PAYMENT_MADE = "PAYMENT_MADE"
    STATUS_CHANGE = "STATUS_CHANGE"


class FileType(Enum):
    """Types of file attachments"""
    JEWELRY_PHOTO = "JEWELRY_PHOTO"
    APPRAISAL_DOCUMENT = "APPRAISAL_DOCUMENT"
    PAYMENT_RECEIPT = "PAYMENT_RECEIPT"
    SHIPPING_LABEL = "SHIPPING_LABEL"
    OTHER = "OTHER"
