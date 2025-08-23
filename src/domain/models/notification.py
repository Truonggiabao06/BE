from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class NotificationType(Enum):
    """Types of notifications"""
    ITEM_SUBMITTED = "item_submitted"                    # Sản phẩm được gửi ký gửi
    PRELIMINARY_VALUATION = "preliminary_valuation"     # Định giá sơ bộ
    ITEM_RECEIVED = "item_received"                     # Đã nhận trang sức
    FINAL_VALUATION = "final_valuation"                 # Định giá cuối cùng
    MANAGER_APPROVAL_NEEDED = "manager_approval_needed" # Cần phê duyệt manager
    ITEM_APPROVED = "item_approved"                     # Sản phẩm được duyệt
    ITEM_REJECTED = "item_rejected"                     # Sản phẩm bị từ chối
    AUCTION_STARTED = "auction_started"                 # Phiên đấu giá bắt đầu
    BID_PLACED = "bid_placed"                          # Có người đặt giá
    AUCTION_WON = "auction_won"                        # Thắng đấu giá
    PAYMENT_REQUIRED = "payment_required"              # Cần thanh toán
    PAYMENT_RECEIVED = "payment_received"              # Đã nhận thanh toán
    ITEM_DELIVERED = "item_delivered"                  # Đã giao hàng

class NotificationStatus(Enum):
    """Status of notifications"""
    UNREAD = "unread"
    READ = "read"
    ARCHIVED = "archived"

class Notification:
    """Domain model for notifications"""

    def __init__(
        self,
        id: Optional[int] = None,
        recipient_id: int = None,
        sender_id: Optional[int] = None,
        type: NotificationType = NotificationType.ITEM_SUBMITTED,
        title: str = "",
        message: str = "",
        data: Optional[Dict[str, Any]] = None,  # Additional data (item_id, session_id, etc.)
        status: NotificationStatus = NotificationStatus.UNREAD,
        created_at: Optional[datetime] = None,
        read_at: Optional[datetime] = None
    ):
        self.id = id
        self.recipient_id = recipient_id
        self.sender_id = sender_id
        self.type = type
        self.title = title
        self.message = message
        self.data = data or {}
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.read_at = read_at

    @property
    def is_read(self) -> bool:
        """Check if notification is read"""
        return self.status == NotificationStatus.READ

    @property
    def is_archived(self) -> bool:
        """Check if notification is archived"""
        return self.status == NotificationStatus.ARCHIVED

    def mark_as_read(self):
        """Mark notification as read"""
        if self.status == NotificationStatus.UNREAD:
            self.status = NotificationStatus.READ
            self.read_at = datetime.utcnow()

    def archive(self):
        """Archive notification"""
        self.status = NotificationStatus.ARCHIVED

    def get_item_id(self) -> Optional[int]:
        """Get item ID from notification data"""
        return self.data.get('item_id')

    def get_session_id(self) -> Optional[int]:
        """Get session ID from notification data"""
        return self.data.get('session_id')

    def get_amount(self) -> Optional[float]:
        """Get amount from notification data"""
        return self.data.get('amount')

    def __repr__(self):
        return f"<Notification(id={self.id}, type='{self.type.value}', recipient={self.recipient_id})>"

    @staticmethod
    def create_item_submitted_notification(recipient_id: int, item_id: int, item_title: str) -> 'Notification':
        """Create notification for item submission"""
        return Notification(
            recipient_id=recipient_id,
            type=NotificationType.ITEM_SUBMITTED,
            title="Yêu cầu ký gửi đã được gửi",
            message=f"Yêu cầu ký gửi cho sản phẩm '{item_title}' đã được gửi thành công. Chúng tôi sẽ liên hệ với bạn sớm.",
            data={'item_id': item_id}
        )

    @staticmethod
    def create_preliminary_valuation_notification(recipient_id: int, item_id: int, item_title: str, price: float) -> 'Notification':
        """Create notification for preliminary valuation"""
        return Notification(
            recipient_id=recipient_id,
            type=NotificationType.PRELIMINARY_VALUATION,
            title="Định giá sơ bộ đã sẵn sàng",
            message=f"Sản phẩm '{item_title}' đã được định giá sơ bộ: {price:,.0f} VND. Vui lòng gửi trang sức đến công ty để định giá cuối cùng.",
            data={'item_id': item_id, 'price': price}
        )

    @staticmethod
    def create_manager_approval_notification(recipient_id: int, item_id: int, item_title: str) -> 'Notification':
        """Create notification for manager approval needed"""
        return Notification(
            recipient_id=recipient_id,
            type=NotificationType.MANAGER_APPROVAL_NEEDED,
            title="Cần phê duyệt định giá",
            message=f"Sản phẩm '{item_title}' cần được phê duyệt định giá cuối cùng.",
            data={'item_id': item_id}
        )

    @staticmethod
    def create_item_approved_notification(recipient_id: int, item_id: int, item_title: str, final_price: float) -> 'Notification':
        """Create notification for item approval"""
        return Notification(
            recipient_id=recipient_id,
            type=NotificationType.ITEM_APPROVED,
            title="Sản phẩm đã được duyệt",
            message=f"Sản phẩm '{item_title}' đã được duyệt với giá khởi điểm {final_price:,.0f} VND và sẵn sàng đấu giá.",
            data={'item_id': item_id, 'price': final_price}
        )

    @staticmethod
    def create_auction_won_notification(recipient_id: int, session_id: int, item_title: str, winning_amount: float) -> 'Notification':
        """Create notification for auction win"""
        return Notification(
            recipient_id=recipient_id,
            type=NotificationType.AUCTION_WON,
            title="Chúc mừng! Bạn đã thắng đấu giá",
            message=f"Bạn đã thắng đấu giá sản phẩm '{item_title}' với giá {winning_amount:,.0f} VND. Vui lòng thanh toán trong 3 ngày.",
            data={'session_id': session_id, 'amount': winning_amount}
        )
