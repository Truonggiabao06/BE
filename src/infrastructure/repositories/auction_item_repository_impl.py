from typing import Optional, List
from src.domain.models.auction_item import AuctionItem
from src.domain.repositories.auction_item_repo import IAuctionItemRepository

class AuctionItemRepository(IAuctionItemRepository):
    def get(self, item_id:int) -> Optional[AuctionItem]: raise NotImplementedError
    def list(self, page:int=1, limit:int=20) -> List[AuctionItem]: raise NotImplementedError
    def create(self, item:AuctionItem) -> AuctionItem: raise NotImplementedError
    def update(self, item:AuctionItem) -> AuctionItem: raise NotImplementedError
    def delete(self, item_id:int) -> None: raise NotImplementedError
