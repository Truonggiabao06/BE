"""
Jewelry Item domain entity
"""
from datetime import datetime
from typing import Optional, Dict, List, Any
from decimal import Decimal
from domain.enums import JewelryStatus


class JewelryItem:
    """Jewelry Item domain entity"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        code: str = "",
        title: str = "",
        description: str = "",
        attributes: Optional[Dict[str, Any]] = None,
        weight: Optional[Decimal] = None,
        photos: Optional[List[str]] = None,
        owner_user_id: str = "",
        status: JewelryStatus = JewelryStatus.PENDING_APPRAISAL,
        estimated_price: Optional[Decimal] = None,
        reserve_price: Optional[Decimal] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.code = code
        self.title = title
        self.description = description
        self.attributes = attributes or {}
        self.weight = weight
        self.photos = photos or []
        self.owner_user_id = owner_user_id
        self.status = status
        self.estimated_price = estimated_price
        self.reserve_price = reserve_price
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def add_photo(self, photo_url: str):
        """Add a photo to the jewelry item"""
        if photo_url not in self.photos:
            self.photos.append(photo_url)
            self.updated_at = datetime.utcnow()
    
    def remove_photo(self, photo_url: str):
        """Remove a photo from the jewelry item"""
        if photo_url in self.photos:
            self.photos.remove(photo_url)
            self.updated_at = datetime.utcnow()
    
    def update_attributes(self, attributes: Dict[str, Any]):
        """Update jewelry attributes"""
        self.attributes.update(attributes)
        self.updated_at = datetime.utcnow()
    
    def set_attribute(self, key: str, value: Any):
        """Set a specific attribute"""
        self.attributes[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get a specific attribute"""
        return self.attributes.get(key, default)
    
    def update_status(self, new_status: JewelryStatus):
        """Update jewelry status"""
        if self.can_transition_to(new_status):
            self.status = new_status
            self.updated_at = datetime.utcnow()
        else:
            raise ValueError(f"Cannot transition from {self.status.value} to {new_status.value}")
    
    def can_transition_to(self, new_status: JewelryStatus) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            JewelryStatus.PENDING_APPRAISAL: [
                JewelryStatus.APPRAISED,
                JewelryStatus.WITHDRAWN
            ],
            JewelryStatus.APPRAISED: [
                JewelryStatus.APPROVED,
                JewelryStatus.WITHDRAWN
            ],
            JewelryStatus.APPROVED: [
                JewelryStatus.IN_AUCTION,
                JewelryStatus.WITHDRAWN
            ],
            JewelryStatus.IN_AUCTION: [
                JewelryStatus.SOLD,
                JewelryStatus.UNSOLD
            ],
            JewelryStatus.UNSOLD: [
                JewelryStatus.APPROVED,  # Can be re-listed
                JewelryStatus.RETURNED
            ],
            JewelryStatus.SOLD: [],  # Final state
            JewelryStatus.RETURNED: [],  # Final state
            JewelryStatus.WITHDRAWN: []  # Final state
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
    def is_available_for_auction(self) -> bool:
        """Check if item is available for auction"""
        return self.status == JewelryStatus.APPROVED
    
    def is_in_auction(self) -> bool:
        """Check if item is currently in auction"""
        return self.status == JewelryStatus.IN_AUCTION
    
    def is_sold(self) -> bool:
        """Check if item is sold"""
        return self.status == JewelryStatus.SOLD
    
    def set_estimated_price(self, price: Decimal):
        """Set estimated price from appraisal"""
        self.estimated_price = price
        self.updated_at = datetime.utcnow()
    
    def set_reserve_price(self, price: Decimal):
        """Set reserve price for auction"""
        self.reserve_price = price
        self.updated_at = datetime.utcnow()
    
    def update_details(self, title: str = None, description: str = None):
        """Update item details"""
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self.updated_at = datetime.utcnow()
    
    def __str__(self):
        return f"JewelryItem(id={self.id}, code={self.code}, title={self.title}, status={self.status.value})"
    
    def __repr__(self):
        return self.__str__()
