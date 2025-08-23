from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.databases.base import Base

class VerificationCodeModel(Base):
    __tablename__ = 'verification_codes'
    __table_args__ = (
        # Composite indexes for efficient queries
        Index('idx_email_type_status', 'email', 'code_type', 'status'),
        Index('idx_user_type', 'user_id', 'code_type'),
        Index('idx_expires_at', 'expires_at'),
        {'extend_existing': True}
    )

    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)  # Nullable for guest users
    
    # Verification details
    email = Column(String(256), nullable=False, index=True)
    code = Column(String(10), nullable=False)  # 6-digit code
    code_type = Column(String(30), nullable=False, default='email_verification')  # email_verification, password_reset, etc.
    status = Column(String(20), nullable=False, default='active', index=True)  # active, used, expired
    
    # Timing
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Attempt tracking
    attempts = Column(Integer, nullable=False, default=0)
    max_attempts = Column(Integer, nullable=False, default=3)
    is_used = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("UserModel", back_populates="verification_codes")
    
    def __repr__(self):
        return f"<VerificationCodeModel(id={self.id}, email='{self.email}', type='{self.code_type}', status='{self.status}')>"
