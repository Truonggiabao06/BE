from datetime import datetime
from typing import Optional
from enum import Enum
from decimal import Decimal

class BidStatus(Enum):
    """Status of bids"""
    ACTIVE = "active"           # Đang là giá cao nhất
    OUTBID = "outbid"          # Đã bị đấu giá cao hơn
    WINNING = "winning"        # Thắng cuộc (phiên kết thúc)
    CANCELLED = "cancelled"    # Đã hủy

class Bid:
    """Domain model for auction bids"""

    def __init__(
        self,
        id: Optional[int] = None,
        auction_session_id: int = None,
        auction_item_id: int = None,
        bidder_id: int = None,  # User ID of the bidder
        amount: Decimal = Decimal('0.00'),
        status: BidStatus = BidStatus.ACTIVE,
        bid_time: Optional[datetime] = None,
        is_auto_bid: bool = False,  # For future auto-bidding feature
        max_auto_bid: Optional[Decimal] = None,  # Maximum amount for auto-bidding
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.auction_session_id = auction_session_id
        self.auction_item_id = auction_item_id
        self.bidder_id = bidder_id
        self.amount = amount
        self.status = status
        self.bid_time = bid_time or datetime.utcnow()
        self.is_auto_bid = is_auto_bid
        self.max_auto_bid = max_auto_bid
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def is_active(self) -> bool:
        """Check if bid is currently the highest"""
        return self.status == BidStatus.ACTIVE

    @property
    def is_winning(self) -> bool:
        """Check if bid is the winning bid"""
        return self.status == BidStatus.WINNING

    @property
    def is_outbid(self) -> bool:
        """Check if bid has been outbid"""
        return self.status == BidStatus.OUTBID

    @property
    def is_cancelled(self) -> bool:
        """Check if bid has been cancelled"""
        return self.status == BidStatus.CANCELLED

    def outbid(self):
        """Mark this bid as outbid by a higher bid"""
        if self.status == BidStatus.ACTIVE:
            self.status = BidStatus.OUTBID
            self.updated_at = datetime.utcnow()

    def mark_winning(self):
        """Mark this bid as the winning bid"""
        if self.status == BidStatus.ACTIVE:
            self.status = BidStatus.WINNING
            self.updated_at = datetime.utcnow()

    def cancel(self):
        """Cancel this bid (only if not winning)"""
        if self.status == BidStatus.WINNING:
            raise ValueError("Cannot cancel winning bid")
        self.status = BidStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def validate_bid_amount(self, current_highest_bid: Optional['Bid'], min_increment: Decimal) -> bool:
        """Validate if this bid amount is valid"""
        if current_highest_bid is None:
            return self.amount > 0

        required_minimum = current_highest_bid.amount + min_increment
        return self.amount >= required_minimum

    def __repr__(self):
        return f"<Bid(id={self.id}, amount={self.amount}, bidder_id={self.bidder_id}, status='{self.status.value}')>"

    def __lt__(self, other):
        """Compare bids by amount (for sorting)"""
        if not isinstance(other, Bid):
            return NotImplemented
        return self.amount < other.amount

    def __le__(self, other):
        """Compare bids by amount (for sorting)"""
        if not isinstance(other, Bid):
            return NotImplemented
        return self.amount <= other.amount

    def __gt__(self, other):
        """Compare bids by amount (for sorting)"""
        if not isinstance(other, Bid):
            return NotImplemented
        return self.amount > other.amount

    def __ge__(self, other):
        """Compare bids by amount (for sorting)"""
        if not isinstance(other, Bid):
            return NotImplemented
        return self.amount >= other.amount

    def __eq__(self, other):
        """Compare bids by amount and time"""
        if not isinstance(other, Bid):
            return NotImplemented
        return self.amount == other.amount and self.bid_time == other.bid_time