from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.models.auction_item import AuctionItem, ItemStatus

class IAuctionItemRepository(ABC):
    @abstractmethod
    def get(self, item_id:int) -> Optional[AuctionItem]: ...

    @abstractmethod
    def get_by_id(self, item_id: int) -> Optional[AuctionItem]: ...

    @abstractmethod
    def list(self, page:int=1, limit:int=20) -> List[AuctionItem]: ...

    @abstractmethod
    def get_by_status(self, status: ItemStatus, page: int = 1, limit: int = 20) -> List[AuctionItem]: ...

    @abstractmethod
    def get_by_seller(self, seller_id: int, page: int = 1, limit: int = 20) -> List[AuctionItem]: ...

    @abstractmethod
    def get_by_staff_assignment(self, staff_id: int, page: int = 1, limit: int = 20) -> List[AuctionItem]: ...

    @abstractmethod
    def count_by_status(self, status: ItemStatus) -> int: ...

    @abstractmethod
    def count_by_staff_assignment(self, staff_id: int) -> int: ...

    @abstractmethod
    def create(self, item:AuctionItem) -> AuctionItem: ...

    @abstractmethod
    def update(self, item:AuctionItem) -> AuctionItem: ...

    @abstractmethod
    def delete(self, item_id:int) -> None: ...
