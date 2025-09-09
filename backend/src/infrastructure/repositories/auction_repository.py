"""
Auction repository implementations for the Jewelry Auction System
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from infrastructure.models.auction_model import AuctionSessionModel, SessionItemModel, EnrollmentModel
from infrastructure.models.jewelry_model import JewelryItemModel
from infrastructure.models.user_model import UserModel
from domain.enums import SessionStatus, JewelryStatus
from datetime import datetime
import uuid


class AuctionSessionRepository:
    """Repository for auction session operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, session_data: Dict[str, Any]) -> AuctionSessionModel:
        """Create a new auction session"""
        session_model = AuctionSessionModel(
            id=str(uuid.uuid4()),
            **session_data
        )
        self.session.add(session_model)
        self.session.commit()
        return session_model
    
    def get_by_id(self, session_id: str) -> Optional[AuctionSessionModel]:
        """Get auction session by ID"""
        return self.session.query(AuctionSessionModel).filter_by(id=session_id).first()
    
    def get_by_code(self, code: str) -> Optional[AuctionSessionModel]:
        """Get auction session by code"""
        return self.session.query(AuctionSessionModel).filter_by(code=code).first()
    
    def list_sessions(self, 
                     status: Optional[SessionStatus] = None,
                     page: int = 1, 
                     limit: int = 20) -> Dict[str, Any]:
        """List auction sessions with pagination"""
        query = self.session.query(AuctionSessionModel)
        
        if status:
            query = query.filter(AuctionSessionModel.status == status)
        
        # Order by created_at desc
        query = query.order_by(desc(AuctionSessionModel.created_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        sessions = query.offset(offset).limit(limit).all()
        
        return {
            'items': sessions,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    def update(self, session_id: str, update_data: Dict[str, Any]) -> Optional[AuctionSessionModel]:
        """Update auction session"""
        session_model = self.get_by_id(session_id)
        if not session_model:
            return None
        
        for key, value in update_data.items():
            if hasattr(session_model, key):
                setattr(session_model, key, value)
        
        session_model.updated_at = datetime.utcnow()
        self.session.commit()
        return session_model
    
    def delete(self, session_id: str) -> bool:
        """Delete auction session"""
        session_model = self.get_by_id(session_id)
        if not session_model:
            return False
        
        self.session.delete(session_model)
        self.session.commit()
        return True


class SessionItemRepository:
    """Repository for session item operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, item_data: Dict[str, Any]) -> SessionItemModel:
        """Create a new session item"""
        item_model = SessionItemModel(
            id=str(uuid.uuid4()),
            **item_data
        )
        self.session.add(item_model)
        self.session.commit()
        return item_model
    
    def get_by_id(self, item_id: str) -> Optional[SessionItemModel]:
        """Get session item by ID"""
        return self.session.query(SessionItemModel).filter_by(id=item_id).first()
    
    def get_by_session_id(self, session_id: str) -> List[SessionItemModel]:
        """Get all items in a session"""
        return self.session.query(SessionItemModel)\
            .filter_by(session_id=session_id)\
            .order_by(asc(SessionItemModel.lot_number))\
            .all()
    
    def get_by_session_and_jewelry(self, session_id: str, jewelry_id: str) -> Optional[SessionItemModel]:
        """Get session item by session and jewelry ID"""
        return self.session.query(SessionItemModel)\
            .filter_by(session_id=session_id, jewelry_item_id=jewelry_id)\
            .first()
    
    def update(self, item_id: str, update_data: Dict[str, Any]) -> Optional[SessionItemModel]:
        """Update session item"""
        item_model = self.get_by_id(item_id)
        if not item_model:
            return None
        
        for key, value in update_data.items():
            if hasattr(item_model, key):
                setattr(item_model, key, value)
        
        item_model.updated_at = datetime.utcnow()
        self.session.commit()
        return item_model
    
    def delete(self, item_id: str) -> bool:
        """Delete session item"""
        item_model = self.get_by_id(item_id)
        if not item_model:
            return False
        
        self.session.delete(item_model)
        self.session.commit()
        return True
    
    def get_next_lot_number(self, session_id: str) -> int:
        """Get next available lot number for session"""
        max_lot = self.session.query(SessionItemModel.lot_number)\
            .filter_by(session_id=session_id)\
            .order_by(desc(SessionItemModel.lot_number))\
            .first()
        
        return (max_lot[0] + 1) if max_lot and max_lot[0] else 1


class EnrollmentRepository:
    """Repository for enrollment operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, enrollment_data: Dict[str, Any]) -> EnrollmentModel:
        """Create a new enrollment"""
        enrollment_model = EnrollmentModel(
            id=str(uuid.uuid4()),
            **enrollment_data
        )
        self.session.add(enrollment_model)
        self.session.commit()
        return enrollment_model
    
    def get_by_id(self, enrollment_id: str) -> Optional[EnrollmentModel]:
        """Get enrollment by ID"""
        return self.session.query(EnrollmentModel).filter_by(id=enrollment_id).first()
    
    def get_by_user_and_session(self, user_id: str, session_id: str) -> Optional[EnrollmentModel]:
        """Get enrollment by user and session"""
        return self.session.query(EnrollmentModel)\
            .filter_by(user_id=user_id, session_id=session_id)\
            .first()
    
    def get_by_session_id(self, session_id: str) -> List[EnrollmentModel]:
        """Get all enrollments for a session"""
        return self.session.query(EnrollmentModel)\
            .filter_by(session_id=session_id)\
            .order_by(desc(EnrollmentModel.enrolled_at))\
            .all()
    
    def get_by_user_id(self, user_id: str) -> List[EnrollmentModel]:
        """Get all enrollments for a user"""
        return self.session.query(EnrollmentModel)\
            .filter_by(user_id=user_id)\
            .order_by(desc(EnrollmentModel.enrolled_at))\
            .all()
    
    def update(self, enrollment_id: str, update_data: Dict[str, Any]) -> Optional[EnrollmentModel]:
        """Update enrollment"""
        enrollment_model = self.get_by_id(enrollment_id)
        if not enrollment_model:
            return None
        
        for key, value in update_data.items():
            if hasattr(enrollment_model, key):
                setattr(enrollment_model, key, value)
        
        self.session.commit()
        return enrollment_model
    
    def delete(self, enrollment_id: str) -> bool:
        """Delete enrollment"""
        enrollment_model = self.get_by_id(enrollment_id)
        if not enrollment_model:
            return False
        
        self.session.delete(enrollment_model)
        self.session.commit()
        return True
    
    def is_user_enrolled(self, user_id: str, session_id: str) -> bool:
        """Check if user is enrolled in session"""
        enrollment = self.get_by_user_and_session(user_id, session_id)
        return enrollment is not None
