"""
Bid domain entity
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from domain.enums import BidStatus


class Bid:
    """Bid domain entity"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        session_id: str = "",
        session_item_id: str = "",
        bidder_id: str = "",
        amount: Decimal = Decimal('0'),
        placed_at: Optional[datetime] = None,
        is_auto: bool = False,
        status: BidStatus = BidStatus.VALID,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.session_id = session_id
        self.session_item_id = session_item_id
        self.bidder_id = bidder_id
        self.amount = amount
        self.placed_at = placed_at or datetime.utcnow()
        self.is_auto = is_auto
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def update_status(self, new_status: BidStatus):
        """Update bid status"""
        if self.can_transition_to(new_status):
            self.status = new_status
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError(f"Cannot transition from {self.status.value} to {new_status.value}")
    
    def can_transition_to(self, new_status: BidStatus) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            BidStatus.VALID: [
                BidStatus.OUTBID,
                BidStatus.WINNING,
                BidStatus.INVALID
            ],
            BidStatus.OUTBID: [
                BidStatus.INVALID  # Can be invalidated later
            ],
            BidStatus.WINNING: [
                BidStatus.OUTBID,
                BidStatus.INVALID
            ],
            BidStatus.INVALID: []  # Final state
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
    def mark_as_outbid(self):
        """Mark bid as outbid by a higher bid"""
        self.update_status(BidStatus.OUTBID)
    
    def mark_as_winning(self):
        """Mark bid as currently winning"""
        self.update_status(BidStatus.WINNING)
    
    def invalidate(self):
        """Invalidate the bid"""
        self.update_status(BidStatus.INVALID)
    
    def is_valid(self) -> bool:
        """Check if bid is valid"""
        return self.status in [BidStatus.VALID, BidStatus.OUTBID, BidStatus.WINNING]
    
    def is_winning(self) -> bool:
        """Check if bid is currently winning"""
        return self.status == BidStatus.WINNING
    
    def is_outbid(self) -> bool:
        """Check if bid has been outbid"""
        return self.status == BidStatus.OUTBID
    
    def is_invalid(self) -> bool:
        """Check if bid is invalid"""
        return self.status == BidStatus.INVALID
    
    def validate_amount(self, current_highest: Decimal, minimum_increment: Decimal, reserve_price: Optional[Decimal] = None) -> bool:
        """Validate bid amount against current highest and minimum increment"""
        # Must be higher than current highest + minimum increment
        if self.amount < current_highest + minimum_increment:
            return False
        
        # Must meet reserve price if set
        if reserve_price and self.amount < reserve_price:
            return False
        
        return True
    
    def get_age_seconds(self) -> int:
        """Get age of bid in seconds"""
        return int((datetime.utcnow() - self.placed_at).total_seconds())
    
    def __str__(self):
        return f"Bid(id={self.id}, bidder_id={self.bidder_id}, amount={self.amount}, status={self.status.value})"
    
    def __repr__(self):
        return self.__str__()


class SessionItem:
    """Session Item domain entity (jewelry item in an auction session)"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        session_id: str = "",
        jewelry_item_id: str = "",
        reserve_price: Optional[Decimal] = None,
        start_price: Decimal = Decimal('0'),
        step_price: Decimal = Decimal('1'),
        lot_number: int = 0,
        current_highest_bid: Optional[Decimal] = None,
        current_winner_id: Optional[str] = None,
        bid_count: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.session_id = session_id
        self.jewelry_item_id = jewelry_item_id
        self.reserve_price = reserve_price
        self.start_price = start_price
        self.step_price = step_price
        self.lot_number = lot_number
        self.current_highest_bid = current_highest_bid or start_price
        self.current_winner_id = current_winner_id
        self.bid_count = bid_count
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def update_highest_bid(self, bid_amount: Decimal, bidder_id: str):
        """Update the highest bid for this item"""
        if bid_amount > self.current_highest_bid:
            self.current_highest_bid = bid_amount
            self.current_winner_id = bidder_id
            self.bid_count += 1
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError("New bid must be higher than current highest bid")
    
    def get_minimum_next_bid(self) -> Decimal:
        """Get minimum amount for next bid"""
        return self.current_highest_bid + self.step_price
    
    def has_reserve_met(self) -> bool:
        """Check if reserve price has been met"""
        if not self.reserve_price:
            return True
        return self.current_highest_bid >= self.reserve_price
    
    def has_bids(self) -> bool:
        """Check if item has received any bids"""
        return self.bid_count > 0
    
    def is_sold(self) -> bool:
        """Check if item is sold (has bids and reserve met)"""
        return self.has_bids() and self.has_reserve_met()
    
    def __str__(self):
        return f"SessionItem(id={self.id}, lot_number={self.lot_number}, current_highest_bid={self.current_highest_bid})"
    
    def __repr__(self):
        return self.__str__()
