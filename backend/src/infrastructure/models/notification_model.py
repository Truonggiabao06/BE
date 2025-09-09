"""
Notification and Content SQLAlchemy models for the Jewelry Auction System
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, JSON, ForeignKey, Boolean, ARRAY
from sqlalchemy.orm import relationship
from infrastructure.databases.mssql import db
from domain.enums import NotificationType, FileType, AuditAction
from datetime import datetime
import uuid


class NotificationModel(db.Model):
    """Notification database model"""
    __tablename__ = 'notifications'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Notification details
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    payload = Column(JSON, nullable=True)  # Additional data for the notification
    
    # Status
    is_read = Column(Boolean, nullable=False, default=False)
    read_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserModel", back_populates="notifications", foreign_keys=[user_id])
    
    def __repr__(self):
        return f"<NotificationModel(id={self.id}, user_id={self.user_id}, type={self.type.value})>"


class AttachmentModel(db.Model):
    """Attachment database model (for files associated with various entities)"""
    __tablename__ = 'attachments'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Polymorphic association
    owner_type = Column(String(50), nullable=False, index=True)  # 'jewelry_item', 'sell_request', etc.
    owner_id = Column(String(36), nullable=False, index=True)
    
    # File details
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(String(20), nullable=False)  # Size in bytes
    file_type = Column(Enum(FileType), nullable=False, default=FileType.OTHER)
    
    # Additional metadata
    meta = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AttachmentModel(id={self.id}, filename={self.filename}, owner_type={self.owner_type})>"


class PolicyModel(db.Model):
    """Policy database model (for terms, privacy policy, etc.)"""
    __tablename__ = 'policies'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    
    # Status
    is_published = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<PolicyModel(id={self.id}, slug={self.slug}, title={self.title})>"


class BlogPostModel(db.Model):
    """Blog Post database model"""
    __tablename__ = 'blog_posts'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String(100), nullable=False, unique=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    
    # SEO and categorization
    tags = Column(JSON, nullable=True)  # Array of tags
    meta_description = Column(String(160), nullable=True)
    
    # Author and status
    author_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    is_published = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    author = relationship("UserModel", foreign_keys=[author_id])
    
    def __repr__(self):
        return f"<BlogPostModel(id={self.id}, slug={self.slug}, title={self.title})>"


class AuditLogModel(db.Model):
    """Audit Log database model"""
    __tablename__ = 'audit_logs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Actor and action
    actor_id = Column(String(36), ForeignKey('users.id'), nullable=True, index=True)  # Nullable for system actions
    action = Column(Enum(AuditAction), nullable=False)
    
    # Target entity
    entity_type = Column(String(50), nullable=False, index=True)  # 'user', 'jewelry_item', etc.
    entity_id = Column(String(36), nullable=False, index=True)
    
    # Change details
    before_data = Column(JSON, nullable=True)  # State before change
    after_data = Column(JSON, nullable=True)   # State after change
    
    # Additional context
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    actor = relationship("UserModel", back_populates="audit_logs", foreign_keys=[actor_id])
    
    def __repr__(self):
        return f"<AuditLogModel(id={self.id}, action={self.action.value}, entity_type={self.entity_type})>"
