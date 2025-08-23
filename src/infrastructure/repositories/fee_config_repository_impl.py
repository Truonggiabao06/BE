import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from decimal import Decimal

from src.domain.models.fee_config import FeeConfig, FeeType
from src.domain.repositories.fee_config_repo import IFeeConfigRepository
from src.infrastructure.models.fee_config_model import FeeConfigModel

logger = logging.getLogger(__name__)

class FeeConfigRepository(IFeeConfigRepository):
    """Implementation of fee configuration repository using SQLAlchemy"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, fee_config: FeeConfig) -> FeeConfig:
        """Create a new fee configuration"""
        try:
            # Convert domain model to SQLAlchemy model
            fee_config_model = FeeConfigModel(
                fee_type=fee_config.fee_type,
                name=fee_config.name,
                description=fee_config.description,
                rate=fee_config.rate,
                fixed_amount=fee_config.fixed_amount,
                min_amount=fee_config.min_amount,
                max_amount=fee_config.max_amount,
                applied_to=fee_config.applied_to,
                is_active=fee_config.is_active,
                created_by=fee_config.created_by
            )

            self.session.add(fee_config_model)
            self.session.commit()
            self.session.refresh(fee_config_model)

            # Convert back to domain model
            return self._to_domain_model(fee_config_model)

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating fee config: {str(e)}")
            raise

    def get(self, fee_config_id: int) -> Optional[FeeConfig]:
        """Get fee configuration by ID"""
        try:
            fee_config_model = self.session.query(FeeConfigModel).filter(
                FeeConfigModel.id == fee_config_id
            ).first()

            if fee_config_model:
                return self._to_domain_model(fee_config_model)
            return None

        except Exception as e:
            logger.error(f"Error getting fee config {fee_config_id}: {str(e)}")
            raise

    def get_by_type(self, fee_type: FeeType) -> List[FeeConfig]:
        """Get fee configurations by type"""
        try:
            fee_config_models = self.session.query(FeeConfigModel).filter(
                FeeConfigModel.fee_type == fee_type
            ).all()

            return [self._to_domain_model(model) for model in fee_config_models]

        except Exception as e:
            logger.error(f"Error getting fee configs by type {fee_type}: {str(e)}")
            raise

    def get_active_configs(self) -> List[FeeConfig]:
        """Get all active fee configurations"""
        try:
            fee_config_models = self.session.query(FeeConfigModel).filter(
                FeeConfigModel.is_active == True
            ).all()

            return [self._to_domain_model(model) for model in fee_config_models]

        except Exception as e:
            logger.error(f"Error getting active fee configs: {str(e)}")
            raise

    def list(self, page: int = 1, limit: int = 20) -> List[FeeConfig]:
        """List fee configurations with pagination"""
        try:
            offset = (page - 1) * limit
            fee_config_models = self.session.query(FeeConfigModel).offset(offset).limit(limit).all()

            return [self._to_domain_model(model) for model in fee_config_models]

        except Exception as e:
            logger.error(f"Error listing fee configs: {str(e)}")
            raise

    def update(self, fee_config: FeeConfig) -> FeeConfig:
        """Update fee configuration"""
        try:
            fee_config_model = self.session.query(FeeConfigModel).filter(
                FeeConfigModel.id == fee_config.id
            ).first()

            if not fee_config_model:
                raise ValueError(f"Fee config with id {fee_config.id} not found")

            # Update fields
            fee_config_model.fee_type = fee_config.fee_type
            fee_config_model.name = fee_config.name
            fee_config_model.description = fee_config.description
            fee_config_model.rate = fee_config.rate
            fee_config_model.fixed_amount = fee_config.fixed_amount
            fee_config_model.min_amount = fee_config.min_amount
            fee_config_model.max_amount = fee_config.max_amount
            fee_config_model.applied_to = fee_config.applied_to
            fee_config_model.is_active = fee_config.is_active

            self.session.commit()
            self.session.refresh(fee_config_model)

            return self._to_domain_model(fee_config_model)

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating fee config {fee_config.id}: {str(e)}")
            raise

    def delete(self, fee_config_id: int) -> bool:
        """Delete fee configuration"""
        try:
            fee_config_model = self.session.query(FeeConfigModel).filter(
                FeeConfigModel.id == fee_config_id
            ).first()

            if not fee_config_model:
                return False

            self.session.delete(fee_config_model)
            self.session.commit()
            return True

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error deleting fee config {fee_config_id}: {str(e)}")
            raise

    def count(self) -> int:
        """Count total fee configurations"""
        try:
            return self.session.query(FeeConfigModel).count()
        except Exception as e:
            logger.error(f"Error counting fee configs: {str(e)}")
            raise

    def _to_domain_model(self, fee_config_model: FeeConfigModel) -> FeeConfig:
        """Convert SQLAlchemy model to domain model"""
        return FeeConfig(
            id=fee_config_model.id,
            fee_type=fee_config_model.fee_type,
            name=fee_config_model.name,
            description=fee_config_model.description,
            rate=Decimal(str(fee_config_model.rate)) if fee_config_model.rate else Decimal('0.00'),
            fixed_amount=Decimal(str(fee_config_model.fixed_amount)) if fee_config_model.fixed_amount else None,
            min_amount=Decimal(str(fee_config_model.min_amount)) if fee_config_model.min_amount else None,
            max_amount=Decimal(str(fee_config_model.max_amount)) if fee_config_model.max_amount else None,
            applied_to=fee_config_model.applied_to,
            is_active=fee_config_model.is_active,
            created_by=fee_config_model.created_by,
            created_at=fee_config_model.created_at,
            updated_at=fee_config_model.updated_at
        )
