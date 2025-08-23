import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.domain.models.notification import Notification, NotificationType, NotificationStatus
from src.domain.repositories.notification_repo import INotificationRepository
from src.infrastructure.models.notification_model import NotificationModel

logger = logging.getLogger(__name__)

class NotificationRepository(INotificationRepository):
    """Implementation of notification repository using SQLAlchemy"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, notification: Notification) -> Notification:
        """Create a new notification"""
        try:
            # Convert domain model to SQLAlchemy model
            notification_model = NotificationModel(
                recipient_id=notification.recipient_id,
                sender_id=notification.sender_id,
                type=notification.type,
                title=notification.title,
                message=notification.message,
                data=notification.data,
                status=notification.status
            )

            self.session.add(notification_model)
            self.session.commit()
            self.session.refresh(notification_model)

            # Convert back to domain model
            return self._to_domain_model(notification_model)

        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise Exception(f"Error creating notification: {str(e)}")

    def get(self, notification_id: int) -> Optional[Notification]:
        """Get notification by ID"""
        try:
            notification_model = self.session.query(NotificationModel).filter(
                NotificationModel.id == notification_id
            ).first()

            if notification_model:
                return self._to_domain_model(notification_model)
            return None

        except SQLAlchemyError as e:
            logger.error(f"Error getting notification {notification_id}: {str(e)}")
            raise Exception(f"Error getting notification: {str(e)}")

    def get_by_recipient(self, recipient_id: int, page: int = 1, limit: int = 20) -> List[Notification]:
        """Get notifications for a specific recipient"""
        try:
            offset = (page - 1) * limit
            notification_models = self.session.query(NotificationModel).filter(
                NotificationModel.recipient_id == recipient_id
            ).order_by(NotificationModel.created_at.desc()).offset(offset).limit(limit).all()

            return [self._to_domain_model(model) for model in notification_models]

        except SQLAlchemyError as e:
            logger.error(f"Error getting notifications for recipient {recipient_id}: {str(e)}")
            raise Exception(f"Error getting notifications: {str(e)}")

    def get_unread_by_recipient(self, recipient_id: int) -> List[Notification]:
        """Get unread notifications for a recipient"""
        try:
            notification_models = self.session.query(NotificationModel).filter(
                NotificationModel.recipient_id == recipient_id,
                NotificationModel.status == NotificationStatus.UNREAD
            ).order_by(NotificationModel.created_at.desc()).all()

            return [self._to_domain_model(model) for model in notification_models]

        except SQLAlchemyError as e:
            logger.error(f"Error getting unread notifications for recipient {recipient_id}: {str(e)}")
            raise Exception(f"Error getting unread notifications: {str(e)}")

    def get_by_type(self, notification_type: NotificationType, page: int = 1, limit: int = 20) -> List[Notification]:
        """Get notifications by type"""
        try:
            offset = (page - 1) * limit
            notification_models = self.session.query(NotificationModel).filter(
                NotificationModel.type == notification_type
            ).order_by(NotificationModel.created_at.desc()).offset(offset).limit(limit).all()

            return [self._to_domain_model(model) for model in notification_models]

        except SQLAlchemyError as e:
            logger.error(f"Error getting notifications by type {notification_type}: {str(e)}")
            raise Exception(f"Error getting notifications by type: {str(e)}")

    def update(self, notification: Notification) -> Notification:
        """Update notification"""
        try:
            notification_model = self.session.query(NotificationModel).filter(
                NotificationModel.id == notification.id
            ).first()

            if not notification_model:
                raise ValueError(f"Notification with id {notification.id} not found")

            # Update fields
            notification_model.recipient_id = notification.recipient_id
            notification_model.sender_id = notification.sender_id
            notification_model.type = notification.type
            notification_model.title = notification.title
            notification_model.message = notification.message
            notification_model.data = notification.data
            notification_model.status = notification.status
            notification_model.read_at = notification.read_at

            self.session.commit()
            self.session.refresh(notification_model)

            return self._to_domain_model(notification_model)

        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error updating notification {notification.id}: {str(e)}")
            raise Exception(f"Error updating notification: {str(e)}")

    def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        try:
            notification_model = self.session.query(NotificationModel).filter(
                NotificationModel.id == notification_id
            ).first()

            if not notification_model:
                return False

            notification_model.status = NotificationStatus.READ
            notification_model.read_at = datetime.utcnow()

            self.session.commit()
            return True

        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error marking notification {notification_id} as read: {str(e)}")
            raise Exception(f"Error marking notification as read: {str(e)}")

    def mark_all_as_read(self, recipient_id: int) -> int:
        """Mark all notifications as read for a recipient"""
        try:
            from datetime import datetime
            
            count = self.session.query(NotificationModel).filter(
                NotificationModel.recipient_id == recipient_id,
                NotificationModel.status == NotificationStatus.UNREAD
            ).update({
                'status': NotificationStatus.READ,
                'read_at': datetime.utcnow()
            })

            self.session.commit()
            return count

        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error marking all notifications as read for recipient {recipient_id}: {str(e)}")
            raise Exception(f"Error marking all notifications as read: {str(e)}")

    def delete(self, notification_id: int) -> bool:
        """Delete notification"""
        try:
            notification_model = self.session.query(NotificationModel).filter(
                NotificationModel.id == notification_id
            ).first()

            if not notification_model:
                return False

            self.session.delete(notification_model)
            self.session.commit()
            return True

        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Error deleting notification {notification_id}: {str(e)}")
            raise Exception(f"Error deleting notification: {str(e)}")

    def count_unread(self, recipient_id: int) -> int:
        """Count unread notifications for a recipient"""
        try:
            return self.session.query(NotificationModel).filter(
                NotificationModel.recipient_id == recipient_id,
                NotificationModel.status == NotificationStatus.UNREAD
            ).count()

        except SQLAlchemyError as e:
            logger.error(f"Error counting unread notifications for recipient {recipient_id}: {str(e)}")
            raise Exception(f"Error counting unread notifications: {str(e)}")

    def _to_domain_model(self, notification_model: NotificationModel) -> Notification:
        """Convert SQLAlchemy model to domain model"""
        return Notification(
            id=notification_model.id,
            recipient_id=notification_model.recipient_id,
            sender_id=notification_model.sender_id,
            type=notification_model.type,
            title=notification_model.title,
            message=notification_model.message,
            data=notification_model.data or {},
            status=notification_model.status,
            created_at=notification_model.created_at,
            read_at=notification_model.read_at
        )
