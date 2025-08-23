from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc
from src.domain.models.auction_session import AuctionSession, SessionStatus
from src.domain.repositories.auction_session_repo import IAuctionSessionRepository
from src.infrastructure.models.auction_session_model import AuctionSessionModel
from datetime import datetime

class AuctionSessionRepository(IAuctionSessionRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, auction_id: int) -> Optional[AuctionSession]:
        """Get auction session by ID"""
        try:
            session_model = self.session.query(AuctionSessionModel).filter(AuctionSessionModel.id == auction_id).first()
            if session_model:
                return self._model_to_domain(session_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting auction session by ID: {str(e)}")

    def list(self, page: int = 1, limit: int = 20) -> List[AuctionSession]:
        """Get paginated list of auction sessions"""
        try:
            offset = (page - 1) * limit
            session_models = (self.session.query(AuctionSessionModel)
                             .order_by(desc(AuctionSessionModel.start_time))
                             .offset(offset).limit(limit).all())
            return [self._model_to_domain(model) for model in session_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error listing auction sessions: {str(e)}")

    def create(self, auction: AuctionSession) -> AuctionSession:
        """Create new auction session"""
        try:
            session_model = self._domain_to_model(auction)
            self.session.add(session_model)
            self.session.commit()
            self.session.refresh(session_model)
            return self._model_to_domain(session_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error creating auction session: {str(e)}")

    def update(self, auction: AuctionSession) -> AuctionSession:
        """Update existing auction session"""
        try:
            session_model = self.session.query(AuctionSessionModel).filter(AuctionSessionModel.id == auction.id).first()
            if not session_model:
                raise Exception(f"Auction session with ID {auction.id} not found")

            # Update fields
            session_model.created_by = auction.created_by
            session_model.title = auction.title
            session_model.description = auction.description
            session_model.start_time = auction.start_time
            session_model.end_time = auction.end_time
            session_model.started_at = auction.started_at
            session_model.ended_at = auction.ended_at
            session_model.min_bid_increment = auction.min_bid_increment
            session_model.registration_required = auction.registration_required
            session_model.max_participants = auction.max_participants
            session_model.item_ids = auction.item_ids
            session_model.status = auction.status
            session_model.updated_at = datetime.utcnow()

            self.session.commit()
            self.session.refresh(session_model)
            return self._model_to_domain(session_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error updating auction session: {str(e)}")

    def delete(self, auction_id: int) -> None:
        """Delete auction session by ID"""
        try:
            session_model = self.session.query(AuctionSessionModel).filter(AuctionSessionModel.id == auction_id).first()
            if not session_model:
                raise Exception(f"Auction session with ID {auction_id} not found")

            self.session.delete(session_model)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error deleting auction session: {str(e)}")

    def get_active_sessions(self) -> List[AuctionSession]:
        """Get all active auction sessions"""
        try:
            session_models = (self.session.query(AuctionSessionModel)
                             .filter(AuctionSessionModel.status == SessionStatus.ACTIVE)
                             .order_by(AuctionSessionModel.start_time).all())
            return [self._model_to_domain(model) for model in session_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting active sessions: {str(e)}")

    def get_scheduled_sessions(self) -> List[AuctionSession]:
        """Get all scheduled auction sessions"""
        try:
            session_models = (self.session.query(AuctionSessionModel)
                             .filter(AuctionSessionModel.status == SessionStatus.SCHEDULED)
                             .order_by(AuctionSessionModel.start_time).all())
            return [self._model_to_domain(model) for model in session_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting scheduled sessions: {str(e)}")

    def _model_to_domain(self, model: AuctionSessionModel) -> AuctionSession:
        """Convert AuctionSessionModel to AuctionSession domain object"""
        return AuctionSession(
            id=model.id,
            title=model.title,
            description=model.description,
            start_time=model.start_time,
            end_time=model.end_time,
            status=model.status,
            item_ids=model.item_ids or [],
            min_bid_increment=model.min_bid_increment,
            registration_required=model.registration_required,
            max_participants=model.max_participants,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
            started_at=model.started_at,
            ended_at=model.ended_at
        )

    def _domain_to_model(self, domain: AuctionSession) -> AuctionSessionModel:
        """Convert AuctionSession domain object to AuctionSessionModel"""
        return AuctionSessionModel(
            id=domain.id,
            title=domain.title,
            description=domain.description,
            start_time=domain.start_time,
            end_time=domain.end_time,
            status=domain.status,
            item_ids=domain.item_ids,
            min_bid_increment=domain.min_bid_increment,
            registration_required=domain.registration_required,
            max_participants=domain.max_participants,
            created_by=domain.created_by,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
            started_at=domain.started_at,
            ended_at=domain.ended_at
        )
