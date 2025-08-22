from typing import Optional, List
from src.domain.models.auction_session import AuctionSession
from src.domain.repositories.auction_session_repo import IAuctionSessionRepository

class AuctionSessionRepository(IAuctionSessionRepository):
    def get(self, auction_id:int) -> Optional[AuctionSession]: raise NotImplementedError
    def list(self, page:int=1, limit:int=20) -> List[AuctionSession]: raise NotImplementedError
    def create(self, auction:AuctionSession) -> AuctionSession: raise NotImplementedError
    def update(self, auction:AuctionSession) -> AuctionSession: raise NotImplementedError
    def delete(self, auction_id:int) -> None: raise NotImplementedError
