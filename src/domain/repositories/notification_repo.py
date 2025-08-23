from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.notification import Notification, NotificationType, NotificationStatus

class INotificationRepository(ABC):
    """Interface for notification repository"""

    @abstractmethod
    def create(self, notification: Notification) -> Notification:
        """Create a new notification"""
        pass

    @abstractmethod
    def get(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        pass

    @abstractmethod
    def get_by_recipient(self, recipient_id: int, page: int = 1, limit: int = 20) -> List[Notification]:
        """Get notifications for a specific recipient"""
        pass

    @abstractmethod
    def get_unread_by_recipient(self, recipient_id: int) -> List[Notification]:
        """Get unread notifications for a recipient"""
        pass

    @abstractmethod
    def get_by_type(self, notification_type: NotificationType, page: int = 1, limit: int = 20) -> List[Notification]:
        """Get notifications by type"""
        pass

    @abstractmethod
    def update(self, notification: Notification) -> Notification:
        """Update notification"""
        pass

    @abstractmethod
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        pass

    @abstractmethod
    def mark_all_as_read(self, recipient_id: int) -> int:
        """Mark all notifications as read for a recipient"""
        pass

    @abstractmethod
    def delete(self, notification_id: int) -> bool:
        """Delete notification"""
        pass

    @abstractmethod
    def count_unread(self, recipient_id: int) -> int:
        """Count unread notifications for a recipient"""
        pass
