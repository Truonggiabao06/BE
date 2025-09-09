"""
Bidding service for the Jewelry Auction System
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from domain.entities.bid import Bid
from domain.enums import SessionStatus, BidStatus, EnrollmentStatus
from domain.exceptions import (
    ValidationError, 
    NotFoundError, 
    BusinessRuleViolationError,
    AuthorizationError,
    ConcurrencyError
)
from domain.business_rules import BiddingRules
from domain.repositories.base_repository import (
    IBidRepository,
    IAuctionSessionRepository, 
    ISessionItemRepository, 
    IEnrollmentRepository
)
from infrastructure.databases.mssql import get_db_session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import text
import uuid


class BiddingService:
    """Bidding service with transactional support"""
    
    def __init__(self, 
                 bid_repository: IBidRepository,
                 session_repository: IAuctionSessionRepository,
                 session_item_repository: ISessionItemRepository,
                 enrollment_repository: IEnrollmentRepository):
        self.bid_repository = bid_repository
        self.session_repository = session_repository
        self.session_item_repository = session_item_repository
        self.enrollment_repository = enrollment_repository
    
    def place_bid(self, session_id: str, session_item_id: str, bidder_id: str, 
                  amount: Decimal, idempotency_key: Optional[str] = None) -> Dict[str, Any]:
        """Place a bid with transactional safety and business rules"""
        
        # Check for duplicate bid using idempotency key
        if idempotency_key:
            existing_bid = self.bid_repository.get_by_idempotency_key(bidder_id, session_item_id, idempotency_key)
            if existing_bid:
                return self._bid_to_dict(existing_bid)
        
        # Get session with lock
        session = self.session_repository.get_by_id_with_lock(session_id)
        if not session:
            raise NotFoundError("Auction session not found")
        
        # Check session status
        if session.status != SessionStatus.OPEN:
            raise BusinessRuleViolationError("Bidding is only allowed when session is open")
        
        # Check if session has ended
        if session.end_at and datetime.utcnow() > session.end_at:
            raise BusinessRuleViolationError("Auction session has ended")
        
        # Get session item with optimistic lock
        session_item = self.session_item_repository.get_by_id_with_lock(session_item_id)
        if not session_item or session_item.session_id != session_id:
            raise NotFoundError("Session item not found")
        
        # Check user enrollment
        enrollment = self.enrollment_repository.get_by_session_and_user(session_id, bidder_id)
        if not enrollment or enrollment.status != EnrollmentStatus.APPROVED:
            raise BusinessRuleViolationError("User must be enrolled and approved to bid")
        
        # Validate bid amount
        is_valid, error_message = BiddingRules.can_place_bid(
            bid_amount=amount,
            current_highest_bid=session_item.current_highest_bid,
            step_price=session_item.step_price,
            reserve_price=session_item.reserve_price,
            current_winner_id=session_item.current_winner_id,
            bidder_id=bidder_id
        )
        
        if not is_valid:
            raise BusinessRuleViolationError(error_message)
        
        try:
            # Start database transaction
            db_session = get_db_session()
            
            # Create bid
            bid = Bid(
                session_id=session_id,
                session_item_id=session_item_id,
                bidder_id=bidder_id,
                amount=amount,
                placed_at=datetime.utcnow(),
                status=BidStatus.VALID,
                idempotency_key=idempotency_key
            )
            
            # Save bid
            created_bid = self.bid_repository.create(bid)
            
            # Update session item with optimistic locking
            old_version = session_item.version
            session_item.current_highest_bid = amount
            session_item.current_winner_id = bidder_id
            session_item.bid_count += 1
            session_item.version += 1
            session_item.updated_at = datetime.utcnow()
            
            # Update with version check
            updated_rows = db_session.execute(
                text("""
                    UPDATE session_items 
                    SET current_highest_bid = :bid_amount,
                        current_winner_id = :winner_id,
                        bid_count = bid_count + 1,
                        version = version + 1,
                        updated_at = :updated_at
                    WHERE id = :item_id AND version = :old_version
                """),
                {
                    'bid_amount': float(amount),
                    'winner_id': bidder_id,
                    'updated_at': datetime.utcnow(),
                    'item_id': session_item_id,
                    'old_version': old_version
                }
            ).rowcount
            
            if updated_rows == 0:
                raise ConcurrencyError("Another bid was placed simultaneously. Please try again.")
            
            # Mark previous bids as outbid
            self.bid_repository.mark_previous_bids_as_outbid(session_item_id, created_bid.id)
            
            # Check for anti-sniping
            self._check_anti_sniping(session, created_bid)
            
            # Commit transaction
            db_session.commit()
            
            # TODO: Send real-time notifications
            # self._notify_bid_placed(created_bid, session_item)
            
            return self._bid_to_dict(created_bid)
            
        except IntegrityError:
            db_session.rollback()
            raise ConcurrencyError("Another bid was placed simultaneously. Please try again.")
        except Exception as e:
            db_session.rollback()
            raise e
    
    def get_bid(self, bid_id: str) -> Optional[Dict[str, Any]]:
        """Get bid by ID"""
        bid = self.bid_repository.get_by_id(bid_id)
        if not bid:
            return None
        
        return self._bid_to_dict(bid)
    
    def get_session_bids(self, session_id: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """Get all bids for a session"""
        result = self.bid_repository.get_by_session_id(session_id, page, page_size)
        bids = result['items']  # Extract bids from repository result
        total_count = self.bid_repository.count_by_session_id(session_id)

        return {
            'items': [self._bid_to_dict(bid) for bid in bids],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
    
    def get_session_item_bids(self, session_item_id: str, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """Get all bids for a specific session item"""
        result = self.bid_repository.get_by_session_item_id(session_item_id, page, page_size)
        bids = result['items']  # Extract bids from repository result
        total_count = self.bid_repository.count_by_session_item_id(session_item_id)

        return {
            'items': [self._bid_to_dict(bid) for bid in bids],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
    
    def get_user_bids(self, user_id: str, session_id: Optional[str] = None, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """Get all bids by a user"""
        filters = {'bidder_id': user_id}
        if session_id:
            filters['session_id'] = session_id
        
        bids = self.bid_repository.list(filters, page, page_size)
        total_count = self.bid_repository.count(filters)
        
        return {
            'items': [self._bid_to_dict(bid) for bid in bids],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
    
    def get_current_highest_bid(self, session_item_id: str) -> Optional[Dict[str, Any]]:
        """Get current highest bid for a session item"""
        bid = self.bid_repository.get_highest_bid_for_item(session_item_id)
        if not bid:
            return None
        
        return self._bid_to_dict(bid)
    
    def get_bid_history(self, session_item_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get bid history for a session item"""
        bids = self.bid_repository.get_bid_history(session_item_id, limit)
        return [self._bid_to_dict(bid) for bid in bids]
    
    def _check_anti_sniping(self, session, bid):
        """Check and apply anti-sniping rules"""
        if not session.end_at:
            return
        
        # Get anti-sniping configuration from session rules or config
        anti_sniping_enabled = session.rules.get('anti_sniping_enabled', True)
        if not anti_sniping_enabled:
            return
        
        trigger_seconds = session.rules.get('anti_sniping_trigger_seconds', 60)
        extension_seconds = session.rules.get('anti_sniping_extension_seconds', 300)
        
        # Check if bid was placed in the last trigger_seconds
        time_until_end = (session.end_at - bid.placed_at).total_seconds()
        
        if time_until_end <= trigger_seconds:
            # Extend auction end time
            new_end_time = session.end_at + timedelta(seconds=extension_seconds)
            session.end_at = new_end_time
            session.updated_at = datetime.utcnow()
            
            self.session_repository.update(session)
            
            # TODO: Notify about time extension
            # self._notify_time_extension(session, extension_seconds)
    
    def _bid_to_dict(self, bid: Bid) -> Dict[str, Any]:
        """Convert bid to dictionary"""
        return {
            'id': bid.id,
            'session_id': bid.session_id,
            'session_item_id': bid.session_item_id,
            'bidder_id': bid.bidder_id,
            'amount': float(bid.amount),
            'placed_at': bid.placed_at.isoformat() if bid.placed_at else None,
            'is_auto': bid.is_auto,
            'status': bid.status.value,
            'idempotency_key': bid.idempotency_key,
            'created_at': bid.created_at.isoformat() if bid.created_at else None,
            'updated_at': bid.updated_at.isoformat() if bid.updated_at else None
        }

    def get_session_item_bids(self, session_id: str, item_id: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Get bids for a specific session item with pagination"""
        # First verify session and item exist
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")

        session_item = self.session_item_repository.get_by_id(item_id)
        if not session_item or session_item.session_id != session_id:
            raise NotFoundError("Session item not found")

        # Get bids with pagination
        bids = self.bid_repository.get_by_session_item_id(item_id, page, limit)
        total_count = self.bid_repository.count_by_session_item_id(item_id)

        return {
            'items': [self._bid_to_dict(bid) for bid in bids],
            'total': total_count,
            'page': page,
            'limit': limit
        }

    def place_session_item_bid(self, session_id: str, item_id: str, user_id: str, amount: Decimal) -> Dict[str, Any]:
        """Place a bid on a specific session item"""
        # Verify session exists and is open
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")

        if session.status != SessionStatus.OPEN:
            raise BusinessRuleViolationError("Session is not open for bidding")

        # Verify session item exists
        session_item = self.session_item_repository.get_by_id(item_id)
        if not session_item or session_item.session_id != session_id:
            raise NotFoundError("Session item not found")

        # Check if user is enrolled in session
        enrollment = self.enrollment_repository.get_by_session_and_user(session_id, user_id)
        if not enrollment or enrollment.status != EnrollmentStatus.APPROVED:
            raise BusinessRuleViolationError("User is not enrolled in this session")

        # Validate bid amount
        min_bid = session_item.current_highest_bid or session_item.start_price
        min_bid += session_item.step_price

        if amount < min_bid:
            raise BusinessRuleViolationError(f"Bid must be at least {min_bid}")

        # Create and place bid
        bid = Bid(
            session_id=session_id,
            session_item_id=item_id,
            bidder_id=user_id,
            amount=amount,
            placed_at=datetime.utcnow(),
            status=BidStatus.VALID
        )

        try:
            # Start transaction
            created_bid = self.bid_repository.create(bid)

            # Update session item with new highest bid
            session_item.current_highest_bid = amount
            session_item.current_winner_id = user_id
            session_item.bid_count += 1
            session_item.version += 1  # For optimistic locking

            self.session_item_repository.update(session_item)

            # Mark previous bids as outbid
            previous_bids = self.bid_repository.get_by_session_item_id(item_id)
            for prev_bid in previous_bids:
                if prev_bid.id != created_bid.id and prev_bid.status == BidStatus.WINNING:
                    prev_bid.status = BidStatus.OUTBID
                    self.bid_repository.update(prev_bid)

            # Mark current bid as winning
            created_bid.status = BidStatus.WINNING
            updated_bid = self.bid_repository.update(created_bid)

            # Commit transaction
            self.bid_repository.commit()

            return self._bid_to_dict(updated_bid)

        except Exception as e:
            self.bid_repository.rollback()
            raise e
