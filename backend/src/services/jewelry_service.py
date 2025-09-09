"""
Jewelry service for the Jewelry Auction System
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from domain.entities.jewelry_item import JewelryItem
from domain.entities.sell_request import SellRequest
from domain.enums import JewelryStatus, SellRequestStatus, UserRole
from domain.exceptions import (
    ValidationError, 
    NotFoundError, 
    BusinessRuleViolationError,
    AuthorizationError
)
from domain.business_rules import SellRequestRules, JewelryRules
from domain.repositories.base_repository import IJewelryItemRepository, ISellRequestRepository
from domain.constants import JEWELRY_CODE_PREFIX, JEWELRY_CODE_LENGTH
import uuid
import random
import string


class JewelryService:
    """Jewelry management service"""
    
    def __init__(self, jewelry_repository: IJewelryItemRepository, sell_request_repository: ISellRequestRepository):
        self.jewelry_repository = jewelry_repository
        self.sell_request_repository = sell_request_repository
    
    def submit_sell_request(self, seller_id: str, seller_role: UserRole, jewelry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit a new sell request"""
        # Validate business rules
        is_valid, error_message = SellRequestRules.can_submit_sell_request(
            seller_role=seller_role,
            jewelry_title=jewelry_data.get('title', ''),
            jewelry_description=jewelry_data.get('description', ''),
            photos=jewelry_data.get('photos', [])
        )
        
        if not is_valid:
            raise BusinessRuleViolationError(error_message)
        
        # Generate jewelry code
        jewelry_code = self._generate_jewelry_code()
        
        # Create jewelry item
        jewelry_item = JewelryItem(
            code=jewelry_code,
            title=jewelry_data['title'].strip(),
            description=jewelry_data['description'].strip(),
            attributes=jewelry_data.get('attributes', {}),
            weight=jewelry_data.get('weight'),
            photos=jewelry_data.get('photos', []),
            owner_user_id=seller_id,
            status=JewelryStatus.PENDING_APPRAISAL
        )
        
        # Save jewelry item
        created_jewelry = self.jewelry_repository.create(jewelry_item)
        
        # Create sell request
        sell_request = SellRequest(
            seller_id=seller_id,
            jewelry_item_id=created_jewelry.id,
            status=SellRequestStatus.SUBMITTED,
            seller_notes=jewelry_data.get('seller_notes', ''),
            submitted_at=datetime.utcnow()
        )
        
        # Save sell request
        created_request = self.sell_request_repository.create(sell_request)
        
        # Commit transaction
        self.jewelry_repository.commit()
        
        return {
            'sell_request_id': created_request.id,
            'jewelry_item_id': created_jewelry.id,
            'jewelry_code': created_jewelry.code,
            'status': created_request.status.value,
            'submitted_at': created_request.submitted_at.isoformat()
        }
    
    def get_jewelry_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get jewelry item by ID"""
        jewelry_item = self.jewelry_repository.get_by_id(item_id)
        if not jewelry_item:
            return None
        
        return self._jewelry_to_dict(jewelry_item)
    
    def get_jewelry_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get jewelry item by code"""
        jewelry_item = self.jewelry_repository.get_by_code(code)
        if not jewelry_item:
            return None
        
        return self._jewelry_to_dict(jewelry_item)
    
    def list_jewelry_items(self, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """List jewelry items with pagination"""
        jewelry_items = self.jewelry_repository.list(filters, page, page_size)
        total_count = self.jewelry_repository.count(filters)
        
        return {
            'items': [self._jewelry_to_dict(item) for item in jewelry_items],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
    
    def get_user_jewelry_items(self, user_id: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get jewelry items owned by a user"""
        filters = {'owner_user_id': user_id}
        return self.list_jewelry_items(filters, page, page_size)
    
    def update_jewelry_item(self, item_id: str, user_id: str, user_role: UserRole, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update jewelry item"""
        jewelry_item = self.jewelry_repository.get_by_id(item_id)
        if not jewelry_item:
            raise NotFoundError("Jewelry item not found")
        
        # Check permissions
        if jewelry_item.owner_user_id != user_id and user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to update this item")
        
        # Update allowed fields
        if 'title' in updates:
            jewelry_item.update_details(title=updates['title'])
        
        if 'description' in updates:
            jewelry_item.update_details(description=updates['description'])
        
        if 'attributes' in updates:
            jewelry_item.update_attributes(updates['attributes'])
        
        if 'photos' in updates and isinstance(updates['photos'], list):
            jewelry_item.photos = updates['photos']
            jewelry_item.updated_at = datetime.utcnow()
        
        # Staff can update pricing
        if user_role in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            if 'estimated_price' in updates:
                jewelry_item.set_estimated_price(Decimal(str(updates['estimated_price'])))
            
            if 'reserve_price' in updates:
                jewelry_item.set_reserve_price(Decimal(str(updates['reserve_price'])))
        
        # Save changes
        updated_item = self.jewelry_repository.update(jewelry_item)
        self.jewelry_repository.commit()
        
        return self._jewelry_to_dict(updated_item)
    
    def update_jewelry_status(self, item_id: str, new_status: JewelryStatus, user_role: UserRole) -> Dict[str, Any]:
        """Update jewelry item status"""
        # Only staff and above can change status
        if user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to change item status")
        
        jewelry_item = self.jewelry_repository.get_by_id(item_id)
        if not jewelry_item:
            raise NotFoundError("Jewelry item not found")
        
        # Update status (this will validate the transition)
        jewelry_item.update_status(new_status)
        
        # Save changes
        updated_item = self.jewelry_repository.update(jewelry_item)
        self.jewelry_repository.commit()
        
        return self._jewelry_to_dict(updated_item)
    
    def add_jewelry_photo(self, item_id: str, photo_url: str, user_id: str, user_role: UserRole) -> Dict[str, Any]:
        """Add photo to jewelry item"""
        jewelry_item = self.jewelry_repository.get_by_id(item_id)
        if not jewelry_item:
            raise NotFoundError("Jewelry item not found")
        
        # Check permissions
        if jewelry_item.owner_user_id != user_id and user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to modify this item")
        
        # Add photo
        jewelry_item.add_photo(photo_url)
        
        # Save changes
        updated_item = self.jewelry_repository.update(jewelry_item)
        self.jewelry_repository.commit()
        
        return self._jewelry_to_dict(updated_item)
    
    def remove_jewelry_photo(self, item_id: str, photo_url: str, user_id: str, user_role: UserRole) -> Dict[str, Any]:
        """Remove photo from jewelry item"""
        jewelry_item = self.jewelry_repository.get_by_id(item_id)
        if not jewelry_item:
            raise NotFoundError("Jewelry item not found")
        
        # Check permissions
        if jewelry_item.owner_user_id != user_id and user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to modify this item")
        
        # Remove photo
        jewelry_item.remove_photo(photo_url)
        
        # Save changes
        updated_item = self.jewelry_repository.update(jewelry_item)
        self.jewelry_repository.commit()
        
        return self._jewelry_to_dict(updated_item)
    
    def get_sell_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get sell request by ID"""
        sell_request = self.sell_request_repository.get_by_id(request_id)
        if not sell_request:
            return None
        
        return self._sell_request_to_dict(sell_request)
    
    def list_sell_requests(self, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """List sell requests with pagination"""
        sell_requests = self.sell_request_repository.list(filters, page, page_size)
        total_count = self.sell_request_repository.count(filters)
        
        return {
            'items': [self._sell_request_to_dict(request) for request in sell_requests],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
    
    def _generate_jewelry_code(self) -> str:
        """Generate unique jewelry code"""
        while True:
            # Generate random code
            random_part = ''.join(random.choices(string.digits, k=JEWELRY_CODE_LENGTH - len(JEWELRY_CODE_PREFIX)))
            code = f"{JEWELRY_CODE_PREFIX}{random_part}"
            
            # Check if code already exists
            existing = self.jewelry_repository.get_by_code(code)
            if not existing:
                return code
    
    def _jewelry_to_dict(self, jewelry_item: JewelryItem) -> Dict[str, Any]:
        """Convert jewelry item to dictionary"""
        return {
            'id': jewelry_item.id,
            'code': jewelry_item.code,
            'title': jewelry_item.title,
            'description': jewelry_item.description,
            'attributes': jewelry_item.attributes,
            'weight': float(jewelry_item.weight) if jewelry_item.weight else None,
            'photos': jewelry_item.photos,
            'owner_user_id': jewelry_item.owner_user_id,
            'status': jewelry_item.status.value,
            'estimated_price': float(jewelry_item.estimated_price) if jewelry_item.estimated_price else None,
            'reserve_price': float(jewelry_item.reserve_price) if jewelry_item.reserve_price else None,
            'created_at': jewelry_item.created_at.isoformat() if jewelry_item.created_at else None,
            'updated_at': jewelry_item.updated_at.isoformat() if jewelry_item.updated_at else None
        }
    
    def _sell_request_to_dict(self, sell_request: SellRequest) -> Dict[str, Any]:
        """Convert sell request to dictionary"""
        return {
            'id': sell_request.id,
            'seller_id': sell_request.seller_id,
            'jewelry_item_id': sell_request.jewelry_item_id,
            'status': sell_request.status.value,
            'notes': sell_request.notes,
            'seller_notes': sell_request.seller_notes,
            'staff_notes': sell_request.staff_notes,
            'manager_notes': sell_request.manager_notes,
            'created_at': sell_request.created_at.isoformat() if sell_request.created_at else None,
            'updated_at': sell_request.updated_at.isoformat() if sell_request.updated_at else None,
            'submitted_at': sell_request.submitted_at.isoformat() if sell_request.submitted_at else None,
            'appraised_at': sell_request.appraised_at.isoformat() if sell_request.appraised_at else None,
            'approved_at': sell_request.approved_at.isoformat() if sell_request.approved_at else None,
            'accepted_at': sell_request.accepted_at.isoformat() if sell_request.accepted_at else None
        }

    def create_jewelry_item(self, user_id: str, user_role: UserRole, jewelry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new jewelry item (STAFF/MANAGER/ADMIN only)"""
        # Check authorization
        if user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to create jewelry items")

        # Validate required fields
        if not jewelry_data.get('title') or not jewelry_data.get('description'):
            raise ValidationError("Title and description are required")

        # Generate jewelry code
        jewelry_code = self._generate_jewelry_code()

        # Create jewelry item
        jewelry_item = JewelryItem(
            code=jewelry_code,
            title=jewelry_data['title'].strip(),
            description=jewelry_data['description'].strip(),
            attributes=jewelry_data.get('attributes', {}),
            weight=Decimal(str(jewelry_data['weight'])) if jewelry_data.get('weight') else None,
            photos=jewelry_data.get('photos', []),
            owner_user_id=user_id,
            status=JewelryStatus.APPRAISED,  # Staff-created items start as appraised
            estimated_price=Decimal(str(jewelry_data['estimated_price'])) if jewelry_data.get('estimated_price') else None,
            reserve_price=Decimal(str(jewelry_data['reserve_price'])) if jewelry_data.get('reserve_price') else None
        )

        # Save to database
        created_jewelry = self.jewelry_repository.create(jewelry_item)
        self.jewelry_repository.commit()

        return self._jewelry_to_dict(created_jewelry)

    def final_approve_sell_request(self, request_id: str, manager_id: str, manager_notes: str = '') -> Dict[str, Any]:
        """Final approve a sell request (MANAGER only)"""
        sell_request = self.sell_request_repository.get_by_id(request_id)
        if not sell_request:
            raise NotFoundError("Sell request not found")

        # Check if request can be approved
        if sell_request.status != SellRequestStatus.SUBMITTED:
            raise BusinessRuleViolationError(f"Cannot approve request with status {sell_request.status.value}")

        # Update sell request
        sell_request.status = SellRequestStatus.MANAGER_APPROVED
        sell_request.manager_notes = manager_notes
        sell_request.approved_at = datetime.utcnow()

        # Update jewelry item status
        jewelry_item = self.jewelry_repository.get_by_id(sell_request.jewelry_item_id)
        if jewelry_item:
            jewelry_item.status = JewelryStatus.APPROVED
            self.jewelry_repository.update(jewelry_item)

        # Save changes
        updated_request = self.sell_request_repository.update(sell_request)
        self.sell_request_repository.commit()

        return self._sell_request_to_dict(updated_request)
