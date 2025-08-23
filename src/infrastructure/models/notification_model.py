from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from src.infrastructure.database import Base
from src.domain.models.notification import NotificationType, NotificationStatus

class NotificationModel(Base):
    """SQLAlchemy model for notifications"""
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient_id = Column(Integer, nullable=False)  # User ID who receives the notification
    sender_id = Column(Integer)  # User ID who sent the notification (optional)
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON)  # Additional data as JSON
    status = Column(SQLEnum(NotificationStatus), nullable=False, default=NotificationStatus.UNREAD)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<NotificationModel(id={self.id}, type='{self.type}', recipient={self.recipient_id})>"
