"""
Sell Request repository implementation for the Jewelry Auction System
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from domain.repositories.base_repository import ISellRequestRepository
from domain.entities.sell_request import SellRequest
from domain.enums import SellRequestStatus
from infrastructure.models.jewelry_model import SellRequestModel
from domain.exceptions import NotFoundError


class SellRequestRepository(ISellRequestRepository[SellRequest]):
    """Sell request repository implementation"""
    
    def __init__(self, session: Session):
        super().__init__(session)
    
    def create(self, entity: SellRequest) -> SellRequest:
        """Create a new sell request"""
        sell_request_model = SellRequestModel(
            seller_id=entity.seller_id,
            jewelry_item_id=entity.jewelry_item_id,
            status=entity.status,
            notes=entity.notes,
            seller_notes=entity.seller_notes,
            staff_notes=entity.staff_notes,
            manager_notes=entity.manager_notes,
            submitted_at=entity.submitted_at,
            appraised_at=entity.appraised_at,
            approved_at=entity.approved_at,
            accepted_at=entity.accepted_at
        )
        
        self.session.add(sell_request_model)
        self.session.flush()
        
        return self._to_domain_entity(sell_request_model)
    
    def get_by_id(self, entity_id: str) -> Optional[SellRequest]:
        """Get sell request by ID"""
        sell_request_model = self.session.query(SellRequestModel).filter_by(id=entity_id).first()
        if not sell_request_model:
            return None
        return self._to_domain_entity(sell_request_model)
    
    def get_by_seller(self, seller_id: str) -> List[SellRequest]:
        """Get sell requests by seller"""
        sell_request_models = self.session.query(SellRequestModel).filter_by(seller_id=seller_id).all()
        return [self._to_domain_entity(model) for model in sell_request_models]
    
    def get_by_status(self, status: SellRequestStatus) -> List[SellRequest]:
        """Get sell requests by status"""
        sell_request_models = self.session.query(SellRequestModel).filter_by(status=status).all()
        return [self._to_domain_entity(model) for model in sell_request_models]
    
    def update(self, entity: SellRequest) -> SellRequest:
        """Update a sell request"""
        sell_request_model = self.session.query(SellRequestModel).filter_by(id=entity.id).first()
        if not sell_request_model:
            raise NotFoundError("Sell request not found")
        
        # Update fields
        sell_request_model.status = entity.status
        sell_request_model.notes = entity.notes
        sell_request_model.seller_notes = entity.seller_notes
        sell_request_model.staff_notes = entity.staff_notes
        sell_request_model.manager_notes = entity.manager_notes
        sell_request_model.updated_at = entity.updated_at
        sell_request_model.submitted_at = entity.submitted_at
        sell_request_model.appraised_at = entity.appraised_at
        sell_request_model.approved_at = entity.approved_at
        sell_request_model.accepted_at = entity.accepted_at
        
        self.session.flush()
        return self._to_domain_entity(sell_request_model)
    
    def delete(self, entity_id: str) -> bool:
        """Delete a sell request"""
        sell_request_model = self.session.query(SellRequestModel).filter_by(id=entity_id).first()
        if not sell_request_model:
            return False
        
        self.session.delete(sell_request_model)
        self.session.flush()
        return True
    
    def list(self, filters: Optional[Dict[str, Any]] = None, 
             page: int = 1, page_size: int = 20) -> List[SellRequest]:
        """List sell requests with optional filters and pagination"""
        query = self.session.query(SellRequestModel)
        
        if filters:
            if 'status' in filters:
                query = query.filter(SellRequestModel.status == filters['status'])
            if 'seller_id' in filters:
                query = query.filter(SellRequestModel.seller_id == filters['seller_id'])
            if 'jewelry_item_id' in filters:
                query = query.filter(SellRequestModel.jewelry_item_id == filters['jewelry_item_id'])
        
        # Apply pagination with required ORDER BY for MSSQL
        offset = (page - 1) * page_size
        sell_request_models = query.order_by(SellRequestModel.created_at.desc()).offset(offset).limit(page_size).all()
        
        return [self._to_domain_entity(model) for model in sell_request_models]
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count sell requests with optional filters"""
        query = self.session.query(SellRequestModel)
        
        if filters:
            if 'status' in filters:
                query = query.filter(SellRequestModel.status == filters['status'])
            if 'seller_id' in filters:
                query = query.filter(SellRequestModel.seller_id == filters['seller_id'])
            if 'jewelry_item_id' in filters:
                query = query.filter(SellRequestModel.jewelry_item_id == filters['jewelry_item_id'])
        
        return query.count()
    
    def _to_domain_entity(self, model: SellRequestModel) -> SellRequest:
        """Convert database model to domain entity"""
        return SellRequest(
            id=model.id,
            seller_id=model.seller_id,
            jewelry_item_id=model.jewelry_item_id,
            status=model.status,
            notes=model.notes,
            seller_notes=model.seller_notes,
            staff_notes=model.staff_notes,
            manager_notes=model.manager_notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            submitted_at=model.submitted_at,
            appraised_at=model.appraised_at,
            approved_at=model.approved_at,
            accepted_at=model.accepted_at
        )
