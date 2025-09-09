"""
Bid repository implementation for the Jewelry Auction System
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from infrastructure.models.auction_model import BidModel, SessionItemModel, AuctionSessionModel
from infrastructure.models.user_model import UserModel
from domain.enums import SessionStatus
from datetime import datetime
from decimal import Decimal
import uuid


class BidRepository:
    """Repository for bid operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, bid_data: Dict[str, Any]) -> BidModel:
        """Create a new bid"""
        bid_model = BidModel(
            id=str(uuid.uuid4()),
            placed_at=datetime.utcnow(),
            **bid_data
        )
        self.session.add(bid_model)
        self.session.commit()
        return bid_model
    
    def get_by_id(self, bid_id: str) -> Optional[BidModel]:
        """Get bid by ID"""
        return self.session.query(BidModel).filter_by(id=bid_id).first()
    
    def get_by_session_id(self, session_id: str, 
                         page: int = 1, 
                         limit: int = 50) -> Dict[str, Any]:
        """Get all bids for a session with pagination"""
        query = self.session.query(BidModel)\
            .filter_by(session_id=session_id)\
            .order_by(desc(BidModel.placed_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        bids = query.offset(offset).limit(limit).all()
        
        return {
            'items': bids,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    def get_by_session_item_id(self, session_item_id: str,
                              page: int = 1,
                              limit: int = 50) -> Dict[str, Any]:
        """Get all bids for a session item with pagination"""
        query = self.session.query(BidModel)\
            .filter_by(session_item_id=session_item_id)\
            .order_by(desc(BidModel.placed_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        bids = query.offset(offset).limit(limit).all()
        
        return {
            'items': bids,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    def get_by_bidder_id(self, bidder_id: str,
                        page: int = 1,
                        limit: int = 50) -> Dict[str, Any]:
        """Get all bids by a bidder with pagination"""
        query = self.session.query(BidModel)\
            .filter_by(bidder_id=bidder_id)\
            .order_by(desc(BidModel.placed_at))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * limit
        bids = query.offset(offset).limit(limit).all()
        
        return {
            'items': bids,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    def get_highest_bid(self, session_item_id: str) -> Optional[BidModel]:
        """Get the highest bid for a session item"""
        return self.session.query(BidModel)\
            .filter_by(session_item_id=session_item_id)\
            .order_by(desc(BidModel.amount))\
            .first()
    
    def get_current_highest_amount(self, session_item_id: str) -> Decimal:
        """Get current highest bid amount for a session item"""
        result = self.session.query(func.max(BidModel.amount))\
            .filter_by(session_item_id=session_item_id)\
            .scalar()
        
        return result if result else Decimal('0.00')
    
    def get_bid_history(self, session_item_id: str, 
                       limit: int = 10) -> List[BidModel]:
        """Get recent bid history for a session item"""
        return self.session.query(BidModel)\
            .filter_by(session_item_id=session_item_id)\
            .order_by(desc(BidModel.placed_at))\
            .limit(limit)\
            .all()
    
    def get_winning_bids_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Get winning bids for each item in a session"""
        # Subquery to get highest bid amount per session item
        subquery = self.session.query(
            BidModel.session_item_id,
            func.max(BidModel.amount).label('max_amount')
        ).filter_by(session_id=session_id)\
         .group_by(BidModel.session_item_id)\
         .subquery()
        
        # Join to get the actual winning bids
        winning_bids = self.session.query(BidModel)\
            .join(subquery, and_(
                BidModel.session_item_id == subquery.c.session_item_id,
                BidModel.amount == subquery.c.max_amount
            ))\
            .filter_by(session_id=session_id)\
            .all()
        
        return winning_bids
    
    def get_user_bids_in_session(self, user_id: str, session_id: str) -> List[BidModel]:
        """Get all bids by a user in a specific session"""
        return self.session.query(BidModel)\
            .filter_by(bidder_id=user_id, session_id=session_id)\
            .order_by(desc(BidModel.placed_at))\
            .all()
    
    def has_user_bid_on_item(self, user_id: str, session_item_id: str) -> bool:
        """Check if user has placed any bid on a session item"""
        bid = self.session.query(BidModel)\
            .filter_by(bidder_id=user_id, session_item_id=session_item_id)\
            .first()
        
        return bid is not None
    
    def get_bid_count_for_item(self, session_item_id: str) -> int:
        """Get total number of bids for a session item"""
        return self.session.query(BidModel)\
            .filter_by(session_item_id=session_item_id)\
            .count()
    
    def get_unique_bidders_count(self, session_item_id: str) -> int:
        """Get number of unique bidders for a session item"""
        return self.session.query(BidModel.bidder_id)\
            .filter_by(session_item_id=session_item_id)\
            .distinct()\
            .count()
    
    def update(self, bid_id: str, update_data: Dict[str, Any]) -> Optional[BidModel]:
        """Update bid (limited use case)"""
        bid_model = self.get_by_id(bid_id)
        if not bid_model:
            return None
        
        for key, value in update_data.items():
            if hasattr(bid_model, key):
                setattr(bid_model, key, value)
        
        self.session.commit()
        return bid_model
    
    def delete(self, bid_id: str) -> bool:
        """Delete bid (admin only, rare use case)"""
        bid_model = self.get_by_id(bid_id)
        if not bid_model:
            return False
        
        self.session.delete(bid_model)
        self.session.commit()
        return True
    
    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get bidding statistics for a session"""
        total_bids = self.session.query(BidModel)\
            .filter_by(session_id=session_id)\
            .count()
        
        unique_bidders = self.session.query(BidModel.bidder_id)\
            .filter_by(session_id=session_id)\
            .distinct()\
            .count()
        
        total_value = self.session.query(func.sum(BidModel.amount))\
            .filter_by(session_id=session_id)\
            .scalar() or Decimal('0.00')
        
        avg_bid = self.session.query(func.avg(BidModel.amount))\
            .filter_by(session_id=session_id)\
            .scalar() or Decimal('0.00')
        
        return {
            'total_bids': total_bids,
            'unique_bidders': unique_bidders,
            'total_bid_value': total_value,
            'average_bid_amount': avg_bid
        }

    def count_by_session_id(self, session_id: str) -> int:
        """Count total bids for a session"""
        return self.session.query(BidModel)\
            .filter_by(session_id=session_id)\
            .count()

    def count_by_session_item_id(self, session_item_id: str) -> int:
        """Count total bids for a session item"""
        return self.session.query(BidModel)\
            .filter_by(session_item_id=session_item_id)\
            .count()

    def get_highest_bid_by_session_item(self, session_item_id: str) -> Optional[BidModel]:
        """Get highest bid for a session item"""
        return self.session.query(BidModel)\
            .filter_by(session_item_id=session_item_id)\
            .order_by(desc(BidModel.amount))\
            .first()

    def get_user_bids_for_session(self, session_id: str, user_id: str) -> List[BidModel]:
        """Get all bids by a user for a specific session"""
        return self.session.query(BidModel)\
            .filter_by(session_id=session_id, bidder_id=user_id)\
            .order_by(desc(BidModel.placed_at))\
            .all()

    def get_winning_bids_by_session(self, session_id: str) -> List[BidModel]:
        """Get winning bids for all items in a session"""
        # This would typically be the highest bid for each item
        # For now, return empty list as this requires more complex logic
        return []
