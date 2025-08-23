from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.models.fee_config import FeeConfig, FeeType

class IFeeConfigRepository(ABC):
    """Interface for fee configuration repository"""

    @abstractmethod
    def create(self, fee_config: FeeConfig) -> FeeConfig:
        """Create a new fee configuration"""
        pass

    @abstractmethod
    def get(self, fee_config_id: int) -> Optional[FeeConfig]:
        """Get fee configuration by ID"""
        pass

    @abstractmethod
    def get_by_type(self, fee_type: FeeType) -> List[FeeConfig]:
        """Get fee configurations by type"""
        pass

    @abstractmethod
    def get_active_configs(self) -> List[FeeConfig]:
        """Get all active fee configurations"""
        pass

    @abstractmethod
    def list(self, page: int = 1, limit: int = 20) -> List[FeeConfig]:
        """List fee configurations with pagination"""
        pass

    @abstractmethod
    def update(self, fee_config: FeeConfig) -> FeeConfig:
        """Update fee configuration"""
        pass

    @abstractmethod
    def delete(self, fee_config_id: int) -> bool:
        """Delete fee configuration"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total fee configurations"""
        pass
