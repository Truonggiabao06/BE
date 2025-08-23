"""
Workflow Notification Service - Business logic for workflow notifications
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

from src.domain.models.notification import Notification, NotificationType, NotificationStatus
from src.domain.models.user import User
from src.domain.repositories.notification_repo import INotificationRepository
from src.infrastructure.services.mock_email_service import MockEmailService

logger = logging.getLogger(__name__)

class WorkflowNotificationService:
    """Service for workflow notification business logic"""
    
    def __init__(self, 
                 notification_repo: INotificationRepository,
                 email_service: MockEmailService):
        self.notification_repo = notification_repo
        self.email_service = email_service

    def create_notification(self, notification: Notification) -> Notification:
        """Create a new notification"""
        try:
            created_notification = self.notification_repo.create(notification)
            logger.info(f"Created notification {created_notification.id} for user {notification.recipient_id}")
            return created_notification
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            raise

    def get_user_notifications(self, user_id: int, page: int = 1, limit: int = 20) -> List[Notification]:
        """Get notifications for a user"""
        try:
            return self.notification_repo.get_by_recipient(user_id, page, limit)
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise

    def get_unread_notifications(self, user_id: int) -> List[Notification]:
        """Get unread notifications for a user"""
        try:
            return self.notification_repo.get_unread_by_recipient(user_id)
        except Exception as e:
            logger.error(f"Error getting unread notifications: {str(e)}")
            raise

    def mark_notification_as_read(self, notification_id: int, user: User) -> bool:
        """Mark a notification as read"""
        try:
            notification = self.notification_repo.get(notification_id)
            if not notification:
                raise ValueError("Notification not found")
            
            if notification.recipient_id != user.id:
                raise ValueError("Cannot mark other user's notification as read")
            
            notification.mark_as_read()
            self.notification_repo.update(notification)
            
            logger.info(f"Marked notification {notification_id} as read for user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            raise

    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        try:
            count = self.notification_repo.mark_all_as_read(user_id)
            logger.info(f"Marked {count} notifications as read for user {user_id}")
            return count
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {str(e)}")
            raise

    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user"""
        try:
            return self.notification_repo.count_unread(user_id)
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            raise

    def send_item_submitted_notification(self, seller_id: int, item_id: int, item_title: str):
        """Send notification when item is submitted"""
        try:
            notification = Notification.create_item_submitted_notification(
                recipient_id=seller_id,
                item_id=item_id,
                item_title=item_title
            )
            self.create_notification(notification)
        except Exception as e:
            logger.error(f"Error sending item submitted notification: {str(e)}")
            raise

    def send_preliminary_valuation_notification(self, seller_id: int, item_id: int, item_title: str, price: float):
        """Send notification when preliminary valuation is ready"""
        try:
            notification = Notification.create_preliminary_valuation_notification(
                recipient_id=seller_id,
                item_id=item_id,
                item_title=item_title,
                price=price
            )
            self.create_notification(notification)
        except Exception as e:
            logger.error(f"Error sending preliminary valuation notification: {str(e)}")
            raise

    def send_manager_approval_notification(self, manager_id: int, item_id: int, item_title: str):
        """Send notification when manager approval is needed"""
        try:
            notification = Notification.create_manager_approval_notification(
                recipient_id=manager_id,
                item_id=item_id,
                item_title=item_title
            )
            self.create_notification(notification)
        except Exception as e:
            logger.error(f"Error sending manager approval notification: {str(e)}")
            raise

    def send_item_approved_notification(self, seller_id: int, item_id: int, item_title: str, final_price: float):
        """Send notification when item is approved"""
        try:
            notification = Notification.create_item_approved_notification(
                recipient_id=seller_id,
                item_id=item_id,
                item_title=item_title,
                final_price=final_price
            )
            self.create_notification(notification)
        except Exception as e:
            logger.error(f"Error sending item approved notification: {str(e)}")
            raise

    def send_auction_won_notification(self, winner_id: int, session_id: int, item_title: str, winning_amount: float):
        """Send notification when user wins an auction"""
        try:
            notification = Notification.create_auction_won_notification(
                recipient_id=winner_id,
                session_id=session_id,
                item_title=item_title,
                winning_amount=winning_amount
            )
            self.create_notification(notification)
        except Exception as e:
            logger.error(f"Error sending auction won notification: {str(e)}")
            raise
