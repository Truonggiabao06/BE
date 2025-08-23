from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from src.infrastructure.database import Base
from src.domain.models.fee_config import FeeType, FeeAppliedTo

class FeeConfigModel(Base):
    """SQLAlchemy model for fee configuration"""
    __tablename__ = 'fee_configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fee_type = Column(SQLEnum(FeeType), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    rate = Column(Numeric(10, 4), nullable=False, default=0.0000)  # 4 decimal places for precision
    fixed_amount = Column(Numeric(15, 2))  # Optional fixed amount
    min_amount = Column(Numeric(15, 2))    # Optional minimum amount
    max_amount = Column(Numeric(15, 2))    # Optional maximum amount
    applied_to = Column(SQLEnum(FeeAppliedTo), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_by = Column(Integer)  # User ID who created this config
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<FeeConfigModel(id={self.id}, type='{self.fee_type}', name='{self.name}')>"
