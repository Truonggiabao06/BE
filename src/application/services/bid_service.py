"""
Bid Service - Business logic for bid management
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from src.domain.models.bid import Bid, BidStatus
from src.domain.models.auction_session import AuctionSession, SessionStatus
from src.domain.models.auction_item import AuctionItem, ItemStatus
from src.domain.models.user import User, UserRole
from src.domain.repositories.bid_repo import IBidRepository
from src.domain.repositories.auction_session_repo import IAuctionSessionRepository
from src.domain.repositories.auction_item_repo import IAuctionItemRepository
from src.domain.repositories.user_repo import IUserRepository

logger = logging.getLogger(__name__)

class BidService:
    """Service for bid business logic"""
    
    def __init__(self, 
                 bid_repo: IBidRepository,
                 auction_session_repo: IAuctionSessionRepository,
                 auction_item_repo: IAuctionItemRepository,
                 user_repo: IUserRepository):
        self.bid_repo = bid_repo
        self.auction_session_repo = auction_session_repo
        self.auction_item_repo = auction_item_repo
        self.user_repo = user_repo
    
    def place_bid(self, session_id: int, bidder: User, amount: float, auto_bid: bool = False) -> Dict[str, Any]:
        """Place a bid with comprehensive business validation"""
        try:
            # Get auction session
            session = self.auction_session_repo.get(session_id)
            if not session:
                raise ValueError("Không tìm thấy phiên đấu giá")
            
            # Validate session status
            if session.status != SessionStatus.ACTIVE:
                raise ValueError("Phiên đấu giá không đang diễn ra")
            
            # Check if session has expired
            now = datetime.now(timezone.utc)
            if session.end_time and session.end_time <= now:
                raise ValueError("Phiên đấu giá đã kết thúc")
            
            # Validate bidder
            if not bidder.is_email_verified:
                raise ValueError("Bạn cần xác thực email trước khi đặt giá")
            
            if bidder.id not in session.participants:
                raise ValueError("Bạn chưa tham gia phiên đấu giá này")
            
            # Get auction item
            item = self.auction_item_repo.get(session.item_id)
            if not item:
                raise ValueError("Không tìm thấy sản phẩm đấu giá")
            
            # Check if bidder is not the seller
            if bidder.id == item.seller_id:
                raise ValueError("Người bán không thể đặt giá cho sản phẩm của mình")
            
            # Validate bid amount
            if amount <= 0:
                raise ValueError("Số tiền đặt giá phải lớn hơn 0")
            
            # Get current highest bid
            current_bids = self.bid_repo.get_by_session(session_id, page=1, limit=1000)
            active_bids = [bid for bid in current_bids if bid.status == BidStatus.ACTIVE]
            
            current_highest_bid = None
            current_highest_amount = 0
            
            if active_bids:
                current_highest_bid = max(active_bids, key=lambda x: x.amount)
                current_highest_amount = current_highest_bid.amount
                
                # Check if bidder already has the highest bid
                if current_highest_bid.bidder_id == bidder.id and not auto_bid:
                    raise ValueError("Bạn đã có giá cao nhất. Hãy chờ người khác đặt giá.")
                
                # Validate minimum bid increment
                minimum_bid = current_highest_amount + session.min_bid_increment
                if amount < minimum_bid:
                    raise ValueError(f"Số tiền đặt giá phải ít nhất {minimum_bid:,.0f} VND")
            else:
                # First bid must be at least starting price
                if amount < item.starting_price:
                    raise ValueError(f"Giá đặt đầu tiên phải ít nhất {item.starting_price:,.0f} VND")
            
            # Check bid frequency (anti-spam)
            recent_bids = [bid for bid in active_bids 
                          if bid.bidder_id == bidder.id and 
                          bid.bid_time and 
                          (now - bid.bid_time).total_seconds() < 60]  # Last 1 minute
            
            if len(recent_bids) >= 3 and not auto_bid:
                raise ValueError("Bạn đã đặt giá quá nhiều lần trong 1 phút. Vui lòng chờ.")
            
            # Create new bid
            new_bid = Bid(
                session_id=session_id,
                bidder_id=bidder.id,
                amount=amount,
                status=BidStatus.ACTIVE,
                bid_time=now,
                is_auto_bid=auto_bid
            )
            
            # Save bid to database
            created_bid = self.bid_repo.create(new_bid)
            
            # Update item current price
            item.current_price = amount
            self.auction_item_repo.update(item)
            
            # Check if this extends auction time (anti-snipe rule)
            time_remaining = (session.end_time - now).total_seconds() if session.end_time else 0
            extended = False
            
            if time_remaining < 300:  # Less than 5 minutes remaining
                # Extend auction by 5 minutes
                session.end_time = now + timedelta(minutes=5)
                self.auction_session_repo.update(session)
                extended = True
                logger.info(f"Extended auction {session_id} due to late bid")
            
            # Calculate next minimum bid
            next_minimum_bid = amount + session.min_bid_increment
            
            result = {
                "bid": created_bid,
                "new_highest_bid": amount,
                "next_minimum_bid": next_minimum_bid,
                "previous_highest_bid": current_highest_amount,
                "total_bids": len(active_bids) + 1,
                "time_extended": extended,
                "time_remaining": (session.end_time - now).total_seconds() if session.end_time else None
            }
            
            logger.info(f"Placed bid {created_bid.id} for {amount:,.0f} VND in session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Place bid error: {str(e)}")
            raise
    
    def cancel_bid(self, bid_id: int, user: User) -> Bid:
        """Cancel a bid (only if not highest bid)"""
        try:
            bid = self.bid_repo.get(bid_id)
            if not bid:
                raise ValueError("Không tìm thấy lượt đặt giá")
            
            # Check ownership
            if bid.bidder_id != user.id and user.role != UserRole.ADMIN:
                raise ValueError("Bạn chỉ có thể hủy lượt đặt giá của mình")
            
            # Check if bid can be cancelled
            if bid.status != BidStatus.ACTIVE:
                raise ValueError("Chỉ có thể hủy lượt đặt giá đang hoạt động")
            
            # Check if this is the highest bid
            session_bids = self.bid_repo.get_by_session(bid.session_id, page=1, limit=1000)
            active_bids = [b for b in session_bids if b.status == BidStatus.ACTIVE]
            
            if active_bids:
                highest_bid = max(active_bids, key=lambda x: x.amount)
                if highest_bid.id == bid.id:
                    raise ValueError("Không thể hủy lượt đặt giá cao nhất")
            
            # Check if session is still active
            session = self.auction_session_repo.get(bid.session_id)
            if session and session.status != SessionStatus.ACTIVE:
                raise ValueError("Không thể hủy lượt đặt giá khi phiên đấu giá đã kết thúc")
            
            # Cancel the bid
            bid.status = BidStatus.CANCELLED
            updated_bid = self.bid_repo.update(bid)
            
            logger.info(f"Cancelled bid {bid_id}")
            return updated_bid
            
        except Exception as e:
            logger.error(f"Cancel bid error: {str(e)}")
            raise
    
    def get_bid_history(self, session_id: int, include_cancelled: bool = False) -> List[Dict[str, Any]]:
        """Get comprehensive bid history for a session"""
        try:
            # Get all bids for session
            bids = self.bid_repo.get_by_session(session_id, page=1, limit=1000)
            
            if not include_cancelled:
                bids = [bid for bid in bids if bid.status == BidStatus.ACTIVE]
            
            # Sort by bid time (newest first)
            bids.sort(key=lambda x: x.bid_time, reverse=True)
            
            # Enrich with additional information
            enriched_bids = []
            for i, bid in enumerate(bids):
                # Get bidder info
                bidder = self.user_repo.get(bid.bidder_id)
                
                # Calculate position
                active_bids = [b for b in bids if b.status == BidStatus.ACTIVE]
                if bid.status == BidStatus.ACTIVE:
                    sorted_active = sorted(active_bids, key=lambda x: x.amount, reverse=True)
                    position = next((i+1 for i, b in enumerate(sorted_active) if b.id == bid.id), None)
                else:
                    position = None
                
                enriched_bid = {
                    "id": bid.id,
                    "amount": bid.amount,
                    "status": bid.status.value,
                    "bid_time": bid.bid_time.isoformat() if bid.bid_time else None,
                    "is_auto_bid": getattr(bid, 'is_auto_bid', False),
                    "position": position,
                    "bidder": {
                        "id": bidder.id if bidder else bid.bidder_id,
                        "name": bidder.full_name if bidder else f"Người đấu giá #{bid.bidder_id}",
                        "is_verified": bidder.is_email_verified if bidder else False
                    } if bidder else None
                }
                
                enriched_bids.append(enriched_bid)
            
            return enriched_bids
            
        except Exception as e:
            logger.error(f"Get bid history error: {str(e)}")
            raise
    
    def get_user_bid_summary(self, user_id: int) -> Dict[str, Any]:
        """Get comprehensive bid summary for a user"""
        try:
            # Get all user bids
            user_bids = self.bid_repo.get_by_bidder(user_id, page=1, limit=1000)
            
            if not user_bids:
                return {
                    "total_bids": 0,
                    "active_bids": 0,
                    "won_auctions": 0,
                    "total_spent": 0,
                    "average_bid": 0,
                    "highest_bid": 0,
                    "success_rate": 0
                }
            
            # Categorize bids
            active_bids = [bid for bid in user_bids if bid.status == BidStatus.ACTIVE]
            cancelled_bids = [bid for bid in user_bids if bid.status == BidStatus.CANCELLED]
            
            # Calculate statistics
            amounts = [bid.amount for bid in active_bids]
            total_spent = 0
            won_auctions = 0
            
            # Check for won auctions
            for bid in active_bids:
                session = self.auction_session_repo.get(bid.session_id)
                if session and session.status == SessionStatus.COMPLETED and session.winner_id == user_id:
                    won_auctions += 1
                    total_spent += bid.amount
            
            summary = {
                "total_bids": len(user_bids),
                "active_bids": len(active_bids),
                "cancelled_bids": len(cancelled_bids),
                "won_auctions": won_auctions,
                "total_spent": total_spent,
                "average_bid": sum(amounts) / len(amounts) if amounts else 0,
                "highest_bid": max(amounts) if amounts else 0,
                "lowest_bid": min(amounts) if amounts else 0,
                "success_rate": (won_auctions / len(active_bids) * 100) if active_bids else 0
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Get user bid summary error: {str(e)}")
            raise
    
    def detect_suspicious_bidding(self, session_id: int) -> Dict[str, Any]:
        """Detect suspicious bidding patterns"""
        try:
            bids = self.bid_repo.get_by_session(session_id, page=1, limit=1000)
            active_bids = [bid for bid in bids if bid.status == BidStatus.ACTIVE]
            
            if len(active_bids) < 2:
                return {"suspicious": False, "patterns": []}
            
            suspicious_patterns = []
            
            # Pattern 1: Rapid bidding between same users
            bidder_times = {}
            for bid in active_bids:
                if bid.bidder_id not in bidder_times:
                    bidder_times[bid.bidder_id] = []
                bidder_times[bid.bidder_id].append(bid.bid_time)
            
            for bidder_id, times in bidder_times.items():
                if len(times) >= 5:  # 5 or more bids
                    times.sort()
                    rapid_bids = 0
                    for i in range(1, len(times)):
                        if (times[i] - times[i-1]).total_seconds() < 30:  # Less than 30 seconds apart
                            rapid_bids += 1
                    
                    if rapid_bids >= 3:
                        suspicious_patterns.append({
                            "type": "rapid_bidding",
                            "bidder_id": bidder_id,
                            "rapid_bids": rapid_bids,
                            "description": "Đặt giá liên tục trong thời gian ngắn"
                        })
            
            # Pattern 2: Alternating bids between two users
            if len(active_bids) >= 6:
                sorted_bids = sorted(active_bids, key=lambda x: x.bid_time)
                alternating_count = 0
                
                for i in range(2, len(sorted_bids)):
                    if (sorted_bids[i].bidder_id == sorted_bids[i-2].bidder_id and
                        sorted_bids[i].bidder_id != sorted_bids[i-1].bidder_id):
                        alternating_count += 1
                
                if alternating_count >= 4:
                    suspicious_patterns.append({
                        "type": "alternating_bids",
                        "count": alternating_count,
                        "description": "Hai người dùng đặt giá xen kẽ nhiều lần"
                    })
            
            # Pattern 3: Unusual bid increments
            sorted_bids = sorted(active_bids, key=lambda x: x.amount)
            small_increments = 0
            
            for i in range(1, len(sorted_bids)):
                increment = sorted_bids[i].amount - sorted_bids[i-1].amount
                session = self.auction_session_repo.get(session_id)
                min_increment = session.min_bid_increment if session else 100000
                
                if increment < min_increment * 1.1:  # Very close to minimum
                    small_increments += 1
            
            if small_increments >= len(sorted_bids) * 0.7:  # 70% of bids are minimal increments
                suspicious_patterns.append({
                    "type": "minimal_increments",
                    "percentage": (small_increments / len(sorted_bids)) * 100,
                    "description": "Phần lớn các lượt đặt giá chỉ tăng mức tối thiểu"
                })
            
            return {
                "suspicious": len(suspicious_patterns) > 0,
                "patterns": suspicious_patterns,
                "total_bids": len(active_bids),
                "unique_bidders": len(set(bid.bidder_id for bid in active_bids))
            }
            
        except Exception as e:
            logger.error(f"Detect suspicious bidding error: {str(e)}")
            return {"suspicious": False, "patterns": [], "error": str(e)}
    
    def auto_extend_auction(self, session_id: int) -> bool:
        """Auto-extend auction if there are bids in the last few minutes"""
        try:
            session = self.auction_session_repo.get(session_id)
            if not session or session.status != SessionStatus.ACTIVE:
                return False
            
            now = datetime.now(timezone.utc)
            if not session.end_time or session.end_time <= now:
                return False
            
            time_remaining = (session.end_time - now).total_seconds()
            
            # Only extend if less than 5 minutes remaining
            if time_remaining >= 300:
                return False
            
            # Check for recent bids
            recent_bids = self.bid_repo.get_by_session(session_id, page=1, limit=10)
            recent_active_bids = [
                bid for bid in recent_bids 
                if bid.status == BidStatus.ACTIVE and 
                bid.bid_time and 
                (now - bid.bid_time).total_seconds() < 300  # Last 5 minutes
            ]
            
            if recent_active_bids:
                # Extend by 5 minutes
                session.end_time = now + timedelta(minutes=5)
                self.auction_session_repo.update(session)
                
                logger.info(f"Auto-extended auction {session_id} by 5 minutes")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Auto extend auction error: {str(e)}")
            return False
