from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.models.bid import Bid

class IBidRepository(ABC):
    @abstractmethod
    def get(self, bid_id:int) -> Optional[Bid]: ...
    @abstractmethod
    def list_by_auction(self, auction_id:int, page:int=1, limit:int=50) -> List[Bid]: ...
    @abstractmethod
    def create(self, bid:Bid) -> Bid: ...
