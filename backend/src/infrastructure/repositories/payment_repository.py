"""
Payment repository implementations for the Jewelry Auction System
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from infrastructure.models.payment_model import PaymentModel, PayoutModel, TransactionFeeModel, RefundModel
from domain.enums import PaymentStatus, PaymentMethod, PayoutStatus
from datetime import datetime
from decimal import Decimal
import uuid


class PaymentRepository:
    """Repository for payment operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, payment_data: Dict[str, Any]) -> PaymentModel:
        """Create a new payment"""
        payment_model = PaymentModel(
            id=str(uuid.uuid4()),
            **payment_data
        )
        self.session.add(payment_model)
        self.session.commit()
        return payment_model
    
    def get_by_id(self, payment_id: str) -> Optional[PaymentModel]:
        """Get payment by ID"""
        return self.session.query(PaymentModel).filter_by(id=payment_id).first()
    
    def get_by_user_id(self, user_id: str, 
                      page: int = 1, 
                      limit: int = 20) -> Dict[str, Any]:
        """Get payments by user ID with pagination"""
        query = self.session.query(PaymentModel)\
            .filter_by(user_id=user_id)\
            .order_by(desc(PaymentModel.created_at))
        
        total = query.count()
        offset = (page - 1) * limit
        payments = query.offset(offset).limit(limit).all()
        
        return {
            'items': payments,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    def get_by_session_id(self, session_id: str) -> List[PaymentModel]:
        """Get all payments for a session"""
        return self.session.query(PaymentModel)\
            .filter_by(session_id=session_id)\
            .order_by(desc(PaymentModel.created_at))\
            .all()
    
    def update(self, payment_id: str, update_data: Dict[str, Any]) -> Optional[PaymentModel]:
        """Update payment"""
        payment_model = self.get_by_id(payment_id)
        if not payment_model:
            return None
        
        for key, value in update_data.items():
            if hasattr(payment_model, key):
                setattr(payment_model, key, value)
        
        payment_model.updated_at = datetime.utcnow()
        self.session.commit()
        return payment_model


class PayoutRepository:
    """Repository for payout operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, payout_data: Dict[str, Any]) -> PayoutModel:
        """Create a new payout"""
        payout_model = PayoutModel(
            id=str(uuid.uuid4()),
            **payout_data
        )
        self.session.add(payout_model)
        self.session.commit()
        return payout_model
    
    def get_by_id(self, payout_id: str) -> Optional[PayoutModel]:
        """Get payout by ID"""
        return self.session.query(PayoutModel).filter_by(id=payout_id).first()
    
    def get_by_user_id(self, user_id: str, 
                      page: int = 1, 
                      limit: int = 20) -> Dict[str, Any]:
        """Get payouts by user ID with pagination"""
        query = self.session.query(PayoutModel)\
            .filter_by(user_id=user_id)\
            .order_by(desc(PayoutModel.created_at))
        
        total = query.count()
        offset = (page - 1) * limit
        payouts = query.offset(offset).limit(limit).all()
        
        return {
            'items': payouts,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    def update(self, payout_id: str, update_data: Dict[str, Any]) -> Optional[PayoutModel]:
        """Update payout"""
        payout_model = self.get_by_id(payout_id)
        if not payout_model:
            return None
        
        for key, value in update_data.items():
            if hasattr(payout_model, key):
                setattr(payout_model, key, value)
        
        payout_model.updated_at = datetime.utcnow()
        self.session.commit()
        return payout_model


class TransactionFeeRepository:
    """Repository for transaction fee operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, fee_data: Dict[str, Any]) -> TransactionFeeModel:
        """Create a new transaction fee"""
        fee_model = TransactionFeeModel(
            id=str(uuid.uuid4()),
            **fee_data
        )
        self.session.add(fee_model)
        self.session.commit()
        return fee_model
    
    def get_by_id(self, fee_id: str) -> Optional[TransactionFeeModel]:
        """Get transaction fee by ID"""
        return self.session.query(TransactionFeeModel).filter_by(id=fee_id).first()
    
    def get_by_session_id(self, session_id: str) -> List[TransactionFeeModel]:
        """Get all transaction fees for a session"""
        return self.session.query(TransactionFeeModel)\
            .filter_by(session_id=session_id)\
            .order_by(desc(TransactionFeeModel.created_at))\
            .all()


class RefundRepository:
    """Repository for refund operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, refund_data: Dict[str, Any]) -> RefundModel:
        """Create a new refund"""
        refund_model = RefundModel(
            id=str(uuid.uuid4()),
            **refund_data
        )
        self.session.add(refund_model)
        self.session.commit()
        return refund_model
    
    def get_by_id(self, refund_id: str) -> Optional[RefundModel]:
        """Get refund by ID"""
        return self.session.query(RefundModel).filter_by(id=refund_id).first()
    
    def get_by_payment_id(self, payment_id: str) -> List[RefundModel]:
        """Get all refunds for a payment"""
        return self.session.query(RefundModel)\
            .filter_by(payment_id=payment_id)\
            .order_by(desc(RefundModel.created_at))\
            .all()
    
    def update(self, refund_id: str, update_data: Dict[str, Any]) -> Optional[RefundModel]:
        """Update refund"""
        refund_model = self.get_by_id(refund_id)
        if not refund_model:
            return None
        
        for key, value in update_data.items():
            if hasattr(refund_model, key):
                setattr(refund_model, key, value)
        
        refund_model.updated_at = datetime.utcnow()
        self.session.commit()
        return refund_model
