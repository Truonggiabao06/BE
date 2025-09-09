"""
Session Item entity for the Jewelry Auction System
"""
from dataclasses import dataclass
from typing import Optional
from decimal import Decimal
from datetime import datetime
from domain.enums import SessionItemStatus


@dataclass
class SessionItem:
    """Session Item entity representing a jewelry item in an auction session"""
    
    id: Optional[int] = None
    session_id: int = None
    jewelry_item_id: int = None
    starting_price: Decimal = None
    current_price: Decimal = None
    reserve_price: Optional[Decimal] = None
    bid_increment: Decimal = None
    lot_number: int = None
    estimated_value_min: Optional[Decimal] = None
    estimated_value_max: Optional[Decimal] = None
    status: SessionItemStatus = SessionItemStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    winner_id: Optional[int] = None
    total_bids: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Post initialization validation"""
        if self.starting_price and self.starting_price <= 0:
            raise ValueError("Starting price must be positive")
        
        if self.reserve_price and self.reserve_price <= 0:
            raise ValueError("Reserve price must be positive")
        
        if self.bid_increment and self.bid_increment <= 0:
            raise ValueError("Bid increment must be positive")
    
    def is_active(self) -> bool:
        """Check if the session item is currently active for bidding"""
        return self.status == SessionItemStatus.ACTIVE
    
    def is_sold(self) -> bool:
        """Check if the session item has been sold"""
        return self.status == SessionItemStatus.SOLD
    
    def is_unsold(self) -> bool:
        """Check if the session item was not sold"""
        return self.status == SessionItemStatus.UNSOLD
    
    def has_reserve_met(self) -> bool:
        """Check if the reserve price has been met"""
        if not self.reserve_price:
            return True
        return self.current_price >= self.reserve_price
    
    def get_next_minimum_bid(self) -> Decimal:
        """Get the minimum amount for the next bid"""
        return self.current_price + self.bid_increment
    
    def update_current_price(self, new_price: Decimal) -> None:
        """Update the current price and increment bid count"""
        if new_price <= self.current_price:
            raise ValueError("New price must be higher than current price")
        
        self.current_price = new_price
        self.total_bids += 1
        self.updated_at = datetime.utcnow()
    
    def close_bidding(self, winner_id: Optional[int] = None) -> None:
        """Close bidding for this session item"""
        if winner_id and self.has_reserve_met():
            self.status = SessionItemStatus.SOLD
            self.winner_id = winner_id
        else:
            self.status = SessionItemStatus.UNSOLD
        
        self.end_time = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'jewelry_item_id': self.jewelry_item_id,
            'starting_price': float(self.starting_price) if self.starting_price else None,
            'current_price': float(self.current_price) if self.current_price else None,
            'reserve_price': float(self.reserve_price) if self.reserve_price else None,
            'bid_increment': float(self.bid_increment) if self.bid_increment else None,
            'lot_number': self.lot_number,
            'estimated_value_min': float(self.estimated_value_min) if self.estimated_value_min else None,
            'estimated_value_max': float(self.estimated_value_max) if self.estimated_value_max else None,
            'status': self.status.value if self.status else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'winner_id': self.winner_id,
            'total_bids': self.total_bids,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
