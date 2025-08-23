from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from src.domain.models.bid import Bid, BidStatus
from src.domain.repositories.bid_repo import IBidRepository
from src.infrastructure.models.bid_model import BidModel
from datetime import datetime

class BidRepository(IBidRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, bid_id: int) -> Optional[Bid]:
        """Get bid by ID"""
        try:
            bid_model = self.session.query(BidModel).filter(BidModel.id == bid_id).first()
            if bid_model:
                return self._model_to_domain(bid_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting bid by ID: {str(e)}")

    def list_by_auction(self, auction_id: int, page: int = 1, limit: int = 50) -> List[Bid]:
        """Get bids by auction session ID, ordered by amount descending"""
        try:
            offset = (page - 1) * limit
            bid_models = (self.session.query(BidModel)
                         .filter(BidModel.auction_session_id == auction_id)
                         .order_by(desc(BidModel.amount), desc(BidModel.bid_time))
                         .offset(offset).limit(limit).all())
            return [self._model_to_domain(model) for model in bid_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error listing bids by auction: {str(e)}")

    def create(self, bid: Bid) -> Bid:
        """Create new bid"""
        try:
            bid_model = self._domain_to_model(bid)
            self.session.add(bid_model)
            self.session.commit()
            self.session.refresh(bid_model)
            return self._model_to_domain(bid_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error creating bid: {str(e)}")

    def update(self, bid: Bid) -> Bid:
        """Update existing bid"""
        try:
            bid_model = self.session.query(BidModel).filter(BidModel.id == bid.id).first()
            if not bid_model:
                raise Exception(f"Bid with ID {bid.id} not found")

            # Update fields
            bid_model.auction_session_id = bid.auction_session_id
            bid_model.auction_item_id = bid.auction_item_id
            bid_model.bidder_id = bid.bidder_id
            bid_model.amount = bid.amount
            bid_model.status = bid.status
            bid_model.bid_time = bid.bid_time
            bid_model.is_auto_bid = bid.is_auto_bid
            bid_model.max_auto_bid = bid.max_auto_bid
            bid_model.updated_at = datetime.utcnow()

            self.session.commit()
            self.session.refresh(bid_model)
            return self._model_to_domain(bid_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error updating bid: {str(e)}")

    def get_highest_bid_for_item(self, auction_item_id: int) -> Optional[Bid]:
        """Get the highest active bid for an auction item"""
        try:
            bid_model = (self.session.query(BidModel)
                        .filter(BidModel.auction_item_id == auction_item_id)
                        .filter(BidModel.status == BidStatus.ACTIVE)
                        .order_by(desc(BidModel.amount), desc(BidModel.bid_time))
                        .first())
            if bid_model:
                return self._model_to_domain(bid_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting highest bid: {str(e)}")

    def get_bids_by_bidder(self, bidder_id: int, page: int = 1, limit: int = 20) -> List[Bid]:
        """Get bids by bidder ID"""
        try:
            offset = (page - 1) * limit
            bid_models = (self.session.query(BidModel)
                         .filter(BidModel.bidder_id == bidder_id)
                         .order_by(desc(BidModel.bid_time))
                         .offset(offset).limit(limit).all())
            return [self._model_to_domain(model) for model in bid_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting bids by bidder: {str(e)}")

    def _model_to_domain(self, model: BidModel) -> Bid:
        """Convert BidModel to Bid domain object"""
        return Bid(
            id=model.id,
            auction_session_id=model.auction_session_id,
            auction_item_id=model.auction_item_id,
            bidder_id=model.bidder_id,
            amount=model.amount,
            status=model.status,
            bid_time=model.bid_time,
            is_auto_bid=model.is_auto_bid,
            max_auto_bid=model.max_auto_bid,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _domain_to_model(self, domain: Bid) -> BidModel:
        """Convert Bid domain object to BidModel"""
        return BidModel(
            id=domain.id,
            auction_session_id=domain.auction_session_id,
            auction_item_id=domain.auction_item_id,
            bidder_id=domain.bidder_id,
            amount=domain.amount,
            status=domain.status,
            bid_time=domain.bid_time,
            is_auto_bid=domain.is_auto_bid,
            max_auto_bid=domain.max_auto_bid,
            created_at=domain.created_at,
            updated_at=domain.updated_at
        )
