"""
Jewelry SQLAlchemy models for the Jewelry Auction System
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, DECIMAL, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from infrastructure.databases.mssql import db
from domain.enums import JewelryStatus, SellRequestStatus, AppraisalType
from datetime import datetime
import uuid


class JewelryItemModel(db.Model):
    """Jewelry Item database model"""
    __tablename__ = 'jewelry_items'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(20), nullable=False, unique=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    attributes = Column(JSON, nullable=True)  # Store jewelry attributes as JSON
    weight = Column(DECIMAL(10, 3), nullable=True)  # Weight in grams
    photos = Column(JSON, nullable=True)  # Array of photo URLs
    
    # Ownership and status
    owner_user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    status = Column(Enum(JewelryStatus), nullable=False, default=JewelryStatus.PENDING_APPRAISAL)
    
    # Pricing
    estimated_price = Column(DECIMAL(12, 2), nullable=True)
    reserve_price = Column(DECIMAL(12, 2), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("UserModel", back_populates="jewelry_items", foreign_keys=[owner_user_id])
    sell_request = relationship("SellRequestModel", back_populates="jewelry_item", uselist=False)
    session_items = relationship("SessionItemModel", back_populates="jewelry_item")
    appraisals = relationship("AppraisalModel", back_populates="jewelry_item")
    attachments = relationship("AttachmentModel", 
                             primaryjoin="and_(JewelryItemModel.id==AttachmentModel.owner_id, "
                                        "AttachmentModel.owner_type=='jewelry_item')",
                             foreign_keys="AttachmentModel.owner_id")
    
    def __repr__(self):
        return f"<JewelryItemModel(id={self.id}, code={self.code}, title={self.title})>"


class SellRequestModel(db.Model):
    """Sell Request database model"""
    __tablename__ = 'sell_requests'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    seller_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    jewelry_item_id = Column(String(36), ForeignKey('jewelry_items.id'), nullable=False, index=True)
    
    # Status and notes
    status = Column(Enum(SellRequestStatus), nullable=False, default=SellRequestStatus.SUBMITTED)
    notes = Column(Text, nullable=True)
    seller_notes = Column(Text, nullable=True)
    staff_notes = Column(Text, nullable=True)
    manager_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    appraised_at = Column(DateTime, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    
    # Relationships
    seller = relationship("UserModel", back_populates="sell_requests", foreign_keys=[seller_id])
    jewelry_item = relationship("JewelryItemModel", back_populates="sell_request", foreign_keys=[jewelry_item_id])
    appraisals = relationship("AppraisalModel", back_populates="sell_request")
    
    def __repr__(self):
        return f"<SellRequestModel(id={self.id}, seller_id={self.seller_id}, status={self.status.value})>"


class AppraisalModel(db.Model):
    """Appraisal database model"""
    __tablename__ = 'appraisals'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sell_request_id = Column(String(36), ForeignKey('sell_requests.id'), nullable=False, index=True)
    jewelry_item_id = Column(String(36), ForeignKey('jewelry_items.id'), nullable=False, index=True)
    staff_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    
    # Appraisal details
    type = Column(Enum(AppraisalType), nullable=False)
    estimated_price = Column(DECIMAL(12, 2), nullable=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sell_request = relationship("SellRequestModel", back_populates="appraisals", foreign_keys=[sell_request_id])
    jewelry_item = relationship("JewelryItemModel", back_populates="appraisals", foreign_keys=[jewelry_item_id])
    staff = relationship("UserModel", back_populates="appraisals", foreign_keys=[staff_id])
    
    def __repr__(self):
        return f"<AppraisalModel(id={self.id}, type={self.type.value}, estimated_price={self.estimated_price})>"
