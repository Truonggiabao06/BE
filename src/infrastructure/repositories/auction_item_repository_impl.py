from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.domain.models.auction_item import AuctionItem, ItemCategory, ItemCondition, ItemStatus
from src.domain.repositories.auction_item_repo import IAuctionItemRepository
from src.infrastructure.models.auction_item_model import AuctionItemModel
from datetime import datetime
from decimal import Decimal

class AuctionItemRepository(IAuctionItemRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, item_id: int) -> Optional[AuctionItem]:
        """Get auction item by ID"""
        try:
            item_model = self.session.query(AuctionItemModel).filter(AuctionItemModel.id == item_id).first()
            if item_model:
                return self._model_to_domain(item_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting auction item by ID: {str(e)}")

    def get_by_id(self, item_id: int) -> Optional[AuctionItem]:
        """Get auction item by ID (alias for get method)"""
        return self.get(item_id)

    def list(self, page: int = 1, limit: int = 20) -> List[AuctionItem]:
        """Get paginated list of auction items"""
        try:
            offset = (page - 1) * limit
            item_models = self.session.query(AuctionItemModel).order_by(AuctionItemModel.id).offset(offset).limit(limit).all()
            return [self._model_to_domain(model) for model in item_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error listing auction items: {str(e)}")

    def create(self, item: AuctionItem) -> AuctionItem:
        """Create new auction item"""
        try:
            item_model = self._domain_to_model(item)
            self.session.add(item_model)
            self.session.commit()
            self.session.refresh(item_model)
            return self._model_to_domain(item_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error creating auction item: {str(e)}")

    def update(self, item: AuctionItem) -> AuctionItem:
        """Update existing auction item"""
        try:
            item_model = self.session.query(AuctionItemModel).filter(AuctionItemModel.id == item.id).first()
            if not item_model:
                raise Exception(f"Auction item with ID {item.id} not found")

            # Update fields
            item_model.seller_id = item.seller_id
            item_model.title = item.title
            item_model.description = item.description
            item_model.category = item.category.value
            item_model.condition = item.condition.value
            item_model.material = item.material
            item_model.weight = item.weight
            item_model.dimensions = item.dimensions
            item_model.brand = item.brand
            item_model.year_made = item.year_made
            item_model.certificate_number = item.certificate_number
            item_model.images = item.images
            item_model.starting_price = item.starting_price
            item_model.reserve_price = item.reserve_price
            item_model.estimated_value = item.estimated_value
            item_model.status = item.status.value
            item_model.staff_notes = item.staff_notes
            item_model.rejection_reason = item.rejection_reason
            # New fields
            item_model.preliminary_price = item.preliminary_price
            item_model.final_price = item.final_price
            item_model.preliminary_valued_by = item.preliminary_valued_by
            item_model.preliminary_valued_at = item.preliminary_valued_at
            item_model.final_valued_by = item.final_valued_by
            item_model.final_valued_at = item.final_valued_at
            item_model.item_received_by = item.item_received_by
            item_model.item_received_at = item.item_received_at
            item_model.manager_notes = item.manager_notes
            item_model.approved_at = item.approved_at
            item_model.approved_by = item.approved_by
            item_model.updated_at = datetime.utcnow()

            self.session.commit()
            self.session.refresh(item_model)
            return self._model_to_domain(item_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error updating auction item: {str(e)}")

    def delete(self, item_id: int) -> None:
        """Delete auction item by ID"""
        try:
            item_model = self.session.query(AuctionItemModel).filter(AuctionItemModel.id == item_id).first()
            if not item_model:
                raise Exception(f"Auction item with ID {item_id} not found")

            self.session.delete(item_model)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error deleting auction item: {str(e)}")

    def get_by_seller(self, seller_id: int, page: int = 1, limit: int = 20) -> List[AuctionItem]:
        """Get auction items by seller ID"""
        try:
            offset = (page - 1) * limit
            item_models = (self.session.query(AuctionItemModel)
                          .filter(AuctionItemModel.seller_id == seller_id)
                          .order_by(AuctionItemModel.id)
                          .offset(offset).limit(limit).all())
            return [self._model_to_domain(model) for model in item_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting items by seller: {str(e)}")

    def get_by_status(self, status: ItemStatus, page: int = 1, limit: int = 20) -> List[AuctionItem]:
        """Get auction items by status"""
        try:
            offset = (page - 1) * limit
            item_models = (self.session.query(AuctionItemModel)
                          .filter(AuctionItemModel.status == status.value)
                          .order_by(AuctionItemModel.id)
                          .offset(offset).limit(limit).all())
            return [self._model_to_domain(model) for model in item_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting items by status: {str(e)}")

    def get_by_staff_assignment(self, staff_id: int, page: int = 1, limit: int = 20) -> List[AuctionItem]:
        """Get auction items assigned to a staff member"""
        try:
            offset = (page - 1) * limit
            item_models = self.session.query(AuctionItemModel).filter(
                (AuctionItemModel.preliminary_valued_by == staff_id) |
                (AuctionItemModel.final_valued_by == staff_id) |
                (AuctionItemModel.item_received_by == staff_id)
            ).order_by(AuctionItemModel.updated_at.desc()).offset(offset).limit(limit).all()
            return [self._model_to_domain(model) for model in item_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting auction items by staff assignment: {str(e)}")

    def count_by_status(self, status: ItemStatus) -> int:
        """Count auction items by status"""
        try:
            return self.session.query(AuctionItemModel).filter(
                AuctionItemModel.status == status.value
            ).count()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error counting auction items by status: {str(e)}")

    def count_by_staff_assignment(self, staff_id: int) -> int:
        """Count auction items assigned to a staff member"""
        try:
            return self.session.query(AuctionItemModel).filter(
                (AuctionItemModel.preliminary_valued_by == staff_id) |
                (AuctionItemModel.final_valued_by == staff_id) |
                (AuctionItemModel.item_received_by == staff_id)
            ).count()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error counting auction items by staff assignment: {str(e)}")

    def _model_to_domain(self, model: AuctionItemModel) -> AuctionItem:
        """Convert AuctionItemModel to AuctionItem domain object"""
        return AuctionItem(
            id=model.id,
            seller_id=model.seller_id,
            title=model.title,
            description=model.description,
            category=ItemCategory(model.category),
            condition=ItemCondition(model.condition),
            material=model.material,
            weight=model.weight,
            dimensions=model.dimensions,
            brand=model.brand,
            year_made=model.year_made,
            certificate_number=model.certificate_number,
            images=model.images or [],
            starting_price=model.starting_price,
            reserve_price=model.reserve_price,
            estimated_value=model.estimated_value,
            status=ItemStatus(model.status),
            staff_notes=model.staff_notes,
            rejection_reason=model.rejection_reason,
            # New fields
            preliminary_price=model.preliminary_price,
            final_price=model.final_price,
            preliminary_valued_by=model.preliminary_valued_by,
            preliminary_valued_at=model.preliminary_valued_at,
            final_valued_by=model.final_valued_by,
            final_valued_at=model.final_valued_at,
            item_received_by=model.item_received_by,
            item_received_at=model.item_received_at,
            manager_notes=model.manager_notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            approved_at=model.approved_at,
            approved_by=model.approved_by
        )

    def _domain_to_model(self, domain: AuctionItem) -> AuctionItemModel:
        """Convert AuctionItem domain object to AuctionItemModel"""
        return AuctionItemModel(
            id=domain.id,
            seller_id=domain.seller_id,
            title=domain.title,
            description=domain.description,
            category=domain.category.value,
            condition=domain.condition.value,
            material=domain.material,
            weight=domain.weight,
            dimensions=domain.dimensions,
            brand=domain.brand,
            year_made=domain.year_made,
            certificate_number=domain.certificate_number,
            images=domain.images,
            starting_price=domain.starting_price,
            reserve_price=domain.reserve_price,
            estimated_value=domain.estimated_value,
            status=domain.status.value,
            staff_notes=domain.staff_notes,
            rejection_reason=domain.rejection_reason,
            # New fields
            preliminary_price=domain.preliminary_price,
            final_price=domain.final_price,
            preliminary_valued_by=domain.preliminary_valued_by,
            preliminary_valued_at=domain.preliminary_valued_at,
            final_valued_by=domain.final_valued_by,
            final_valued_at=domain.final_valued_at,
            item_received_by=domain.item_received_by,
            item_received_at=domain.item_received_at,
            manager_notes=domain.manager_notes,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            approved_at=domain.approved_at,
            approved_by=domain.approved_by
        )
