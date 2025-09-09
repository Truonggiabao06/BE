"""
User SQLAlchemy model for the Jewelry Auction System
"""
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer
from sqlalchemy.orm import relationship
from infrastructure.databases.mssql import db
from domain.enums import UserRole
from datetime import datetime
import uuid


class UserModel(db.Model):
    """User database model"""
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.MEMBER)
    is_active = Column(Boolean, nullable=False, default=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Email verification
    email_verified = Column(Boolean, nullable=False, default=False)
    email_verified_at = Column(DateTime, nullable=True)

    # Login tracking
    last_login_at = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, nullable=False, default=0)
    locked_until = Column(DateTime, nullable=True)

    # Relationships
    jewelry_items = relationship("JewelryItemModel", back_populates="owner")
    sell_requests = relationship("SellRequestModel", back_populates="seller")
    appraisals = relationship("AppraisalModel", back_populates="staff")
    managed_sessions = relationship("AuctionSessionModel", back_populates="assigned_staff")
    enrollments = relationship("EnrollmentModel", back_populates="user", foreign_keys="EnrollmentModel.user_id")
    approved_enrollments = relationship("EnrollmentModel", foreign_keys="EnrollmentModel.approved_by")
    bids = relationship("BidModel", back_populates="bidder")
    payments = relationship("PaymentModel", back_populates="buyer")
    payouts = relationship("PayoutModel", back_populates="seller")
    notifications = relationship("NotificationModel", back_populates="user")
    audit_logs = relationship("AuditLogModel", back_populates="actor")

    def __repr__(self):
        return f"<UserModel(id={self.id}, email={self.email}, role={self.role.value})>"


class RoleModel(db.Model):
    """Role database model (for future role-based permissions)"""
    __tablename__ = 'roles'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<RoleModel(id={self.id}, code={self.code}, name={self.name})>"