from typing import Optional, List
from src.domain.models.bid import Bid
from src.domain.repositories.bid_repo import IBidRepository

class BidRepository(IBidRepository):
    def get(self, bid_id:int) -> Optional[Bid]: raise NotImplementedError
    def list_by_auction(self, auction_id:int, page:int=1, limit:int=50) -> List[Bid]: raise NotImplementedError
    def create(self, bid:Bid) -> Bid: raise NotImplementedError
