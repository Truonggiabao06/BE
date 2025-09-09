"""
Base repository interface for the Jewelry Auction System
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from sqlalchemy.orm import Session

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Base repository interface"""
    
    def __init__(self, session: Session):
        self.session = session
    
    @abstractmethod
    def create(self, entity: T) -> T:
        """Create a new entity"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID"""
        pass
    
    @abstractmethod
    def update(self, entity: T) -> T:
        """Update an entity"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete an entity"""
        pass
    
    @abstractmethod
    def list(self, filters: Optional[Dict[str, Any]] = None, 
             page: int = 1, page_size: int = 20) -> List[T]:
        """List entities with optional filters and pagination"""
        pass
    
    @abstractmethod
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters"""
        pass
    
    def exists(self, entity_id: str) -> bool:
        """Check if entity exists"""
        return self.get_by_id(entity_id) is not None
    
    def commit(self):
        """Commit transaction"""
        self.session.commit()
    
    def rollback(self):
        """Rollback transaction"""
        self.session.rollback()
    
    def flush(self):
        """Flush session"""
        self.session.flush()


class IUserRepository(BaseRepository[T]):
    """User repository interface"""
    
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[T]:
        """Get user by email"""
        pass
    
    @abstractmethod
    def get_by_role(self, role: str) -> List[T]:
        """Get users by role"""
        pass


class IJewelryItemRepository(BaseRepository[T]):
    """Jewelry item repository interface"""
    
    @abstractmethod
    def get_by_code(self, code: str) -> Optional[T]:
        """Get jewelry item by code"""
        pass
    
    @abstractmethod
    def get_by_owner(self, owner_id: str) -> List[T]:
        """Get jewelry items by owner"""
        pass
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[T]:
        """Get jewelry items by status"""
        pass


class ISellRequestRepository(BaseRepository[T]):
    """Sell request repository interface"""
    
    @abstractmethod
    def get_by_seller(self, seller_id: str) -> List[T]:
        """Get sell requests by seller"""
        pass
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[T]:
        """Get sell requests by status"""
        pass


class IAuctionSessionRepository(BaseRepository[T]):
    """Auction session repository interface"""
    
    @abstractmethod
    def get_by_code(self, code: str) -> Optional[T]:
        """Get auction session by code"""
        pass
    
    @abstractmethod
    def get_by_status(self, status: str) -> List[T]:
        """Get auction sessions by status"""
        pass
    
    @abstractmethod
    def get_active_sessions(self) -> List[T]:
        """Get active auction sessions"""
        pass


class IBidRepository(BaseRepository[T]):
    """Bid repository interface"""
    
    @abstractmethod
    def get_by_session_item(self, session_item_id: str) -> List[T]:
        """Get bids by session item"""
        pass
    
    @abstractmethod
    def get_by_bidder(self, bidder_id: str) -> List[T]:
        """Get bids by bidder"""
        pass
    
    @abstractmethod
    def get_highest_bid(self, session_item_id: str) -> Optional[T]:
        """Get highest bid for session item"""
        pass


class IPaymentRepository(BaseRepository[T]):
    """Payment repository interface"""

    @abstractmethod
    def get_by_buyer(self, buyer_id: str) -> List[T]:
        """Get payments by buyer"""
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[T]:
        """Get payments by status"""
        pass


class IPayoutRepository(BaseRepository[T]):
    """Payout repository interface"""

    @abstractmethod
    def get_by_seller(self, seller_id: str) -> List[T]:
        """Get payouts by seller"""
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[T]:
        """Get payouts by status"""
        pass

    @abstractmethod
    def get_by_session_item(self, session_item_id: str) -> Optional[T]:
        """Get payout by session item"""
        pass


class ITransactionFeeRepository(BaseRepository[T]):
    """Transaction fee repository interface"""

    @abstractmethod
    def get_by_transaction_type(self, transaction_type: str) -> List[T]:
        """Get fees by transaction type"""
        pass

    @abstractmethod
    def get_by_session_item(self, session_item_id: str) -> List[T]:
        """Get fees by session item"""
        pass


class ISessionItemRepository(BaseRepository[T]):
    """Session item repository interface"""

    @abstractmethod
    def get_by_session(self, session_id: str) -> List[T]:
        """Get session items by session"""
        pass

    @abstractmethod
    def get_by_jewelry_item(self, jewelry_item_id: str) -> Optional[T]:
        """Get session item by jewelry item"""
        pass

    @abstractmethod
    def get_by_lot_number(self, session_id: str, lot_number: int) -> Optional[T]:
        """Get session item by lot number"""
        pass


class IEnrollmentRepository(BaseRepository[T]):
    """Enrollment repository interface"""

    @abstractmethod
    def get_by_user_and_session(self, user_id: str, session_id: str) -> Optional[T]:
        """Get enrollment by user and session"""
        pass

    @abstractmethod
    def get_by_session(self, session_id: str) -> List[T]:
        """Get enrollments by session"""
        pass

    @abstractmethod
    def get_by_user(self, user_id: str) -> List[T]:
        """Get enrollments by user"""
        pass


class INotificationRepository(BaseRepository[T]):
    """Notification repository interface"""

    @abstractmethod
    def get_by_user(self, user_id: str) -> List[T]:
        """Get notifications by user"""
        pass

    @abstractmethod
    def get_unread_by_user(self, user_id: str) -> List[T]:
        """Get unread notifications by user"""
        pass

    @abstractmethod
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        pass
