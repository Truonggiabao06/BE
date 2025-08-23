"""
Auction Service - Business logic for auction management
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from src.domain.models.auction_session import AuctionSession, SessionStatus
from src.domain.models.auction_item import AuctionItem, ItemStatus
from src.domain.models.bid import Bid, BidStatus
from src.domain.models.user import User, UserRole
from src.domain.repositories.auction_session_repo import IAuctionSessionRepository
from src.domain.repositories.auction_item_repo import IAuctionItemRepository
from src.domain.repositories.bid_repo import IBidRepository
from src.domain.repositories.user_repo import IUserRepository

logger = logging.getLogger(__name__)

class AuctionService:
    """Service for auction business logic"""
    
    def __init__(self, 
                 auction_session_repo: IAuctionSessionRepository,
                 auction_item_repo: IAuctionItemRepository,
                 bid_repo: IBidRepository,
                 user_repo: IUserRepository):
        self.auction_session_repo = auction_session_repo
        self.auction_item_repo = auction_item_repo
        self.bid_repo = bid_repo
        self.user_repo = user_repo
    
    def create_auction_session(self, session_data: Dict[str, Any], creator: User) -> AuctionSession:
        """Create new auction session with business validation"""
        try:
            # Validate creator permissions
            if creator.role != UserRole.ADMIN:
                raise ValueError("Chỉ admin mới có thể tạo phiên đấu giá")
            
            # Validate item exists and is approved
            item = self.auction_item_repo.get(session_data['item_id'])
            if not item:
                raise ValueError("Không tìm thấy sản phẩm")
            
            if item.status != ItemStatus.APPROVED:
                raise ValueError("Chỉ có thể tạo phiên đấu giá cho sản phẩm đã được duyệt")
            
            # Check if item already has active auction
            existing_sessions = self.auction_session_repo.get_by_item_id(item.id)
            active_sessions = [s for s in existing_sessions if s.status in [SessionStatus.SCHEDULED, SessionStatus.ACTIVE]]
            
            if active_sessions:
                raise ValueError("Sản phẩm đã có phiên đấu giá đang hoạt động")
            
            # Validate time logic
            start_time = session_data['start_time']
            end_time = session_data['end_time']
            now = datetime.now(timezone.utc)
            
            if start_time <= now:
                raise ValueError("Thời gian bắt đầu phải sau thời điểm hiện tại")
            
            if end_time <= start_time:
                raise ValueError("Thời gian kết thúc phải sau thời gian bắt đầu")
            
            # Validate duration (minimum 1 hour, maximum 7 days)
            duration = end_time - start_time
            if duration < timedelta(hours=1):
                raise ValueError("Phiên đấu giá phải kéo dài ít nhất 1 giờ")
            
            if duration > timedelta(days=7):
                raise ValueError("Phiên đấu giá không được kéo dài quá 7 ngày")
            
            # Create auction session
            auction_session = AuctionSession(
                title=session_data['title'].strip(),
                description=session_data['description'].strip(),
                item_id=item.id,
                creator_id=creator.id,
                start_time=start_time,
                end_time=end_time,
                status=SessionStatus.SCHEDULED,
                min_bid_increment=session_data.get('min_bid_increment', 100000),  # Default 100k VND
                max_participants=session_data.get('max_participants', 100),
                participants=[]
            )
            
            # Save to database
            created_session = self.auction_session_repo.create(auction_session)
            
            # Update item status to ACTIVE
            item.status = ItemStatus.ACTIVE
            self.auction_item_repo.update(item)
            
            logger.info(f"Created auction session {created_session.id} for item {item.id}")
            return created_session
            
        except Exception as e:
            logger.error(f"Create auction session error: {str(e)}")
            raise
    
    def start_auction_session(self, session_id: int, admin: User) -> AuctionSession:
        """Start auction session manually"""
        try:
            # Validate admin permissions
            if admin.role != UserRole.ADMIN:
                raise ValueError("Chỉ admin mới có thể bắt đầu phiên đấu giá")
            
            session = self.auction_session_repo.get(session_id)
            if not session:
                raise ValueError("Không tìm thấy phiên đấu giá")
            
            if session.status != SessionStatus.SCHEDULED:
                raise ValueError("Chỉ có thể bắt đầu phiên đấu giá đã được lên lịch")
            
            # Start the session
            session.status = SessionStatus.ACTIVE
            session.actual_start_time = datetime.now(timezone.utc)
            
            updated_session = self.auction_session_repo.update(session)
            
            logger.info(f"Started auction session {session_id}")
            return updated_session
            
        except Exception as e:
            logger.error(f"Start auction session error: {str(e)}")
            raise
    
    def end_auction_session(self, session_id: int, admin: User) -> Dict[str, Any]:
        """End auction session and determine winner"""
        try:
            # Validate admin permissions
            if admin.role != UserRole.ADMIN:
                raise ValueError("Chỉ admin mới có thể kết thúc phiên đấu giá")
            
            session = self.auction_session_repo.get(session_id)
            if not session:
                raise ValueError("Không tìm thấy phiên đấu giá")
            
            if session.status != SessionStatus.ACTIVE:
                raise ValueError("Chỉ có thể kết thúc phiên đấu giá đang diễn ra")
            
            # Get all bids for this session
            bids = self.bid_repo.get_by_session(session_id, page=1, limit=1000)
            active_bids = [bid for bid in bids if bid.status == BidStatus.ACTIVE]
            
            # Determine winner
            winner_bid = None
            if active_bids:
                winner_bid = max(active_bids, key=lambda x: x.amount)
            
            # End the session
            session.status = SessionStatus.COMPLETED
            session.actual_end_time = datetime.now(timezone.utc)
            
            if winner_bid:
                session.winner_id = winner_bid.bidder_id
                session.final_price = winner_bid.amount
            
            updated_session = self.auction_session_repo.update(session)
            
            # Update item status
            item = self.auction_item_repo.get(session.item_id)
            if item:
                if winner_bid:
                    item.status = ItemStatus.SOLD
                    item.current_price = winner_bid.amount
                else:
                    item.status = ItemStatus.UNSOLD
                
                self.auction_item_repo.update(item)
            
            result = {
                "session": updated_session,
                "winner_bid": winner_bid,
                "total_bids": len(active_bids),
                "participants": len(set(bid.bidder_id for bid in active_bids))
            }
            
            logger.info(f"Ended auction session {session_id}, winner: {winner_bid.bidder_id if winner_bid else 'None'}")
            return result
            
        except Exception as e:
            logger.error(f"End auction session error: {str(e)}")
            raise
    
    def join_auction_session(self, session_id: int, user: User) -> AuctionSession:
        """Join auction session as participant"""
        try:
            session = self.auction_session_repo.get(session_id)
            if not session:
                raise ValueError("Không tìm thấy phiên đấu giá")
            
            if session.status != SessionStatus.ACTIVE:
                raise ValueError("Chỉ có thể tham gia phiên đấu giá đang diễn ra")
            
            # Check if user is already a participant
            if user.id in session.participants:
                raise ValueError("Bạn đã tham gia phiên đấu giá này")
            
            # Check max participants
            if len(session.participants) >= session.max_participants:
                raise ValueError("Phiên đấu giá đã đầy")
            
            # Check if user is the seller
            item = self.auction_item_repo.get(session.item_id)
            if item and user.id == item.seller_id:
                raise ValueError("Người bán không thể tham gia đấu giá sản phẩm của mình")
            
            # Add user to participants
            session.participants.append(user.id)
            updated_session = self.auction_session_repo.update(session)
            
            logger.info(f"User {user.id} joined auction session {session_id}")
            return updated_session
            
        except Exception as e:
            logger.error(f"Join auction session error: {str(e)}")
            raise
    
    def get_auction_statistics(self, session_id: int) -> Dict[str, Any]:
        """Get comprehensive auction statistics"""
        try:
            session = self.auction_session_repo.get(session_id)
            if not session:
                raise ValueError("Không tìm thấy phiên đấu giá")
            
            # Get all bids
            bids = self.bid_repo.get_by_session(session_id, page=1, limit=1000)
            active_bids = [bid for bid in bids if bid.status == BidStatus.ACTIVE]
            
            if not active_bids:
                return {
                    "session_id": session_id,
                    "status": session.status.value,
                    "total_bids": 0,
                    "unique_bidders": 0,
                    "highest_bid": 0,
                    "starting_price": 0,
                    "average_bid": 0,
                    "bid_frequency": 0,
                    "time_remaining": None
                }
            
            # Calculate statistics
            amounts = [bid.amount for bid in active_bids]
            unique_bidders = len(set(bid.bidder_id for bid in active_bids))
            
            # Time-based statistics
            now = datetime.now(timezone.utc)
            time_remaining = None
            if session.status == SessionStatus.ACTIVE and session.end_time:
                time_remaining = (session.end_time - now).total_seconds()
                if time_remaining < 0:
                    time_remaining = 0
            
            # Bid frequency (bids per hour)
            if session.actual_start_time:
                elapsed_time = (now - session.actual_start_time).total_seconds() / 3600  # hours
                bid_frequency = len(active_bids) / max(elapsed_time, 0.1)
            else:
                bid_frequency = 0
            
            # Get item info
            item = self.auction_item_repo.get(session.item_id)
            starting_price = item.starting_price if item else 0
            
            stats = {
                "session_id": session_id,
                "status": session.status.value,
                "total_bids": len(active_bids),
                "unique_bidders": unique_bidders,
                "highest_bid": max(amounts),
                "lowest_bid": min(amounts),
                "starting_price": starting_price,
                "average_bid": sum(amounts) / len(amounts),
                "bid_frequency": round(bid_frequency, 2),
                "time_remaining": time_remaining,
                "participants": len(session.participants),
                "max_participants": session.max_participants,
                "min_bid_increment": session.min_bid_increment
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Get auction statistics error: {str(e)}")
            raise
    
    def auto_end_expired_sessions(self) -> List[Dict[str, Any]]:
        """Automatically end expired auction sessions"""
        try:
            now = datetime.now(timezone.utc)
            
            # Get all active sessions
            all_sessions = self.auction_session_repo.list(page=1, limit=1000)
            active_sessions = [s for s in all_sessions if s.status == SessionStatus.ACTIVE]
            
            ended_sessions = []
            
            for session in active_sessions:
                if session.end_time and session.end_time <= now:
                    try:
                        # Create a system admin user for auto-ending
                        system_admin = User(id=0, role=UserRole.ADMIN, email="system@auction.com")
                        result = self.end_auction_session(session.id, system_admin)
                        ended_sessions.append(result)
                        
                        logger.info(f"Auto-ended expired session {session.id}")
                    except Exception as e:
                        logger.error(f"Failed to auto-end session {session.id}: {str(e)}")
            
            return ended_sessions
            
        except Exception as e:
            logger.error(f"Auto end expired sessions error: {str(e)}")
            return []
    
    def validate_auction_rules(self, session: AuctionSession, user: User, bid_amount: float) -> Dict[str, Any]:
        """Validate auction business rules before placing bid"""
        try:
            errors = []
            warnings = []
            
            # Check session status
            if session.status != SessionStatus.ACTIVE:
                errors.append("Phiên đấu giá không đang diễn ra")
            
            # Check if user is participant
            if user.id not in session.participants:
                errors.append("Bạn chưa tham gia phiên đấu giá này")
            
            # Check if user is seller
            item = self.auction_item_repo.get(session.item_id)
            if item and user.id == item.seller_id:
                errors.append("Người bán không thể đặt giá cho sản phẩm của mình")
            
            # Check bid amount
            if bid_amount <= 0:
                errors.append("Số tiền đặt giá phải lớn hơn 0")
            
            # Check minimum bid increment
            current_bids = self.bid_repo.get_by_session(session.id, page=1, limit=1000)
            active_bids = [bid for bid in current_bids if bid.status == BidStatus.ACTIVE]
            
            if active_bids:
                highest_bid = max(active_bids, key=lambda x: x.amount)
                minimum_bid = highest_bid.amount + session.min_bid_increment
                
                if bid_amount < minimum_bid:
                    errors.append(f"Số tiền đặt giá phải ít nhất {minimum_bid:,.0f} VND")
                
                # Check if user already has highest bid
                if highest_bid.bidder_id == user.id:
                    errors.append("Bạn đã có giá cao nhất. Hãy chờ người khác đặt giá.")
            else:
                # First bid must be at least starting price
                if item and bid_amount < item.starting_price:
                    errors.append(f"Giá đặt đầu tiên phải ít nhất {item.starting_price:,.0f} VND")
            
            # Check time remaining
            now = datetime.now(timezone.utc)
            if session.end_time and session.end_time <= now:
                errors.append("Phiên đấu giá đã kết thúc")
            elif session.end_time:
                time_remaining = (session.end_time - now).total_seconds()
                if time_remaining < 60:  # Less than 1 minute
                    warnings.append("Phiên đấu giá sắp kết thúc")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"Validate auction rules error: {str(e)}")
            return {
                "valid": False,
                "errors": ["Lỗi hệ thống khi kiểm tra quy tắc đấu giá"],
                "warnings": []
            }
