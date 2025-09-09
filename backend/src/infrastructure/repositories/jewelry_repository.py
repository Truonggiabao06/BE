"""
Jewelry repository implementation for the Jewelry Auction System
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from domain.repositories.base_repository import IJewelryItemRepository
from domain.entities.jewelry_item import JewelryItem
from domain.enums import JewelryStatus
from infrastructure.models.jewelry_model import JewelryItemModel
from domain.exceptions import NotFoundError, ConflictError


class JewelryItemRepository(IJewelryItemRepository[JewelryItem]):
    """Jewelry item repository implementation"""
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def create(self, entity: JewelryItem) -> JewelryItem:
        """Create a new jewelry item"""
        # Check if code already exists
        if entity.code:
            existing = self.session.query(JewelryItemModel).filter_by(code=entity.code).first()
            if existing:
                raise ConflictError("Jewelry code already exists")
        
        jewelry_model = JewelryItemModel(
            code=entity.code,
            title=entity.title,
            description=entity.description,
            attributes=entity.attributes,
            weight=entity.weight,
            photos=entity.photos,
            owner_user_id=entity.owner_user_id,
            status=entity.status,
            estimated_price=entity.estimated_price,
            reserve_price=entity.reserve_price
        )
        
        self.session.add(jewelry_model)
        self.session.flush()
        
        return self._to_domain_entity(jewelry_model)
    
    def get_by_id(self, entity_id: str) -> Optional[JewelryItem]:
        """Get jewelry item by ID"""
        jewelry_model = self.session.query(JewelryItemModel).filter_by(id=entity_id).first()
        if not jewelry_model:
            return None
        return self._to_domain_entity(jewelry_model)
    
    def get_by_code(self, code: str) -> Optional[JewelryItem]:
        """Get jewelry item by code"""
        jewelry_model = self.session.query(JewelryItemModel).filter_by(code=code).first()
        if not jewelry_model:
            return None
        return self._to_domain_entity(jewelry_model)
    
    def get_by_owner(self, owner_id: str) -> List[JewelryItem]:
        """Get jewelry items by owner"""
        jewelry_models = self.session.query(JewelryItemModel).filter_by(owner_user_id=owner_id).all()
        return [self._to_domain_entity(model) for model in jewelry_models]
    
    def get_by_status(self, status: JewelryStatus) -> List[JewelryItem]:
        """Get jewelry items by status"""
        jewelry_models = self.session.query(JewelryItemModel).filter_by(status=status).all()
        return [self._to_domain_entity(model) for model in jewelry_models]
    
    def update(self, entity: JewelryItem) -> JewelryItem:
        """Update a jewelry item"""
        jewelry_model = self.session.query(JewelryItemModel).filter_by(id=entity.id).first()
        if not jewelry_model:
            raise NotFoundError("Jewelry item not found")
        
        # Update fields
        jewelry_model.code = entity.code
        jewelry_model.title = entity.title
        jewelry_model.description = entity.description
        jewelry_model.attributes = entity.attributes
        jewelry_model.weight = entity.weight
        jewelry_model.photos = entity.photos
        jewelry_model.status = entity.status
        jewelry_model.estimated_price = entity.estimated_price
        jewelry_model.reserve_price = entity.reserve_price
        jewelry_model.updated_at = entity.updated_at
        
        self.session.flush()
        return self._to_domain_entity(jewelry_model)
    
    def delete(self, entity_id: str) -> bool:
        """Delete a jewelry item"""
        jewelry_model = self.session.query(JewelryItemModel).filter_by(id=entity_id).first()
        if not jewelry_model:
            return False
        
        self.session.delete(jewelry_model)
        self.session.flush()
        return True
    
    def list(self, filters: Optional[Dict[str, Any]] = None, 
             page: int = 1, page_size: int = 20) -> List[JewelryItem]:
        """List jewelry items with optional filters and pagination"""
        query = self.session.query(JewelryItemModel)
        
        if filters:
            if 'status' in filters:
                query = query.filter(JewelryItemModel.status == filters['status'])
            if 'owner_user_id' in filters:
                query = query.filter(JewelryItemModel.owner_user_id == filters['owner_user_id'])
            if 'search' in filters:
                search_term = f"%{filters['search']}%"
                query = query.filter(or_(
                    JewelryItemModel.title.ilike(search_term),
                    JewelryItemModel.description.ilike(search_term),
                    JewelryItemModel.code.ilike(search_term)
                ))
            if 'min_price' in filters:
                query = query.filter(JewelryItemModel.estimated_price >= filters['min_price'])
            if 'max_price' in filters:
                query = query.filter(JewelryItemModel.estimated_price <= filters['max_price'])
        
        # Apply pagination with required ORDER BY for MSSQL
        offset = (page - 1) * page_size
        jewelry_models = query.order_by(JewelryItemModel.created_at.desc()).offset(offset).limit(page_size).all()
        
        return [self._to_domain_entity(model) for model in jewelry_models]
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count jewelry items with optional filters"""
        query = self.session.query(JewelryItemModel)
        
        if filters:
            if 'status' in filters:
                query = query.filter(JewelryItemModel.status == filters['status'])
            if 'owner_user_id' in filters:
                query = query.filter(JewelryItemModel.owner_user_id == filters['owner_user_id'])
            if 'search' in filters:
                search_term = f"%{filters['search']}%"
                query = query.filter(or_(
                    JewelryItemModel.title.ilike(search_term),
                    JewelryItemModel.description.ilike(search_term),
                    JewelryItemModel.code.ilike(search_term)
                ))
            if 'min_price' in filters:
                query = query.filter(JewelryItemModel.estimated_price >= filters['min_price'])
            if 'max_price' in filters:
                query = query.filter(JewelryItemModel.estimated_price <= filters['max_price'])
        
        return query.count()
    
    def _to_domain_entity(self, model: JewelryItemModel) -> JewelryItem:
        """Convert database model to domain entity"""
        return JewelryItem(
            id=model.id,
            code=model.code,
            title=model.title,
            description=model.description,
            attributes=model.attributes or {},
            weight=model.weight,
            photos=model.photos or [],
            owner_user_id=model.owner_user_id,
            status=model.status,
            estimated_price=model.estimated_price,
            reserve_price=model.reserve_price,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
