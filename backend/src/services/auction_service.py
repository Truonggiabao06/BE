"""
Auction service for the Jewelry Auction System
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
from domain.entities.auction_session import AuctionSession
from domain.entities.session_item import SessionItem
from domain.entities.enrollment import Enrollment
from domain.enums import SessionStatus, EnrollmentStatus, JewelryStatus, UserRole
from domain.exceptions import (
    ValidationError, 
    NotFoundError, 
    BusinessRuleViolationError,
    AuthorizationError
)
from domain.business_rules import AuctionRules
from domain.repositories.base_repository import (
    IAuctionSessionRepository, 
    ISessionItemRepository, 
    IEnrollmentRepository,
    IJewelryItemRepository
)
from domain.constants import SESSION_CODE_PREFIX, SESSION_CODE_LENGTH
import uuid
import random
import string


class AuctionService:
    """Auction management service"""
    
    def __init__(self, 
                 session_repository: IAuctionSessionRepository,
                 session_item_repository: ISessionItemRepository,
                 enrollment_repository: IEnrollmentRepository,
                 jewelry_repository: IJewelryItemRepository):
        self.session_repository = session_repository
        self.session_item_repository = session_item_repository
        self.enrollment_repository = enrollment_repository
        self.jewelry_repository = jewelry_repository
    
    def create_auction_session(self, user_role: UserRole, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new auction session"""
        # Only staff and above can create sessions
        if user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to create auction sessions")
        
        # Validate session data
        is_valid, error_message = AuctionRules.can_create_session(
            name=session_data.get('name', ''),
            start_at=session_data.get('start_at'),
            end_at=session_data.get('end_at')
        )
        
        if not is_valid:
            raise BusinessRuleViolationError(error_message)
        
        # Generate session code
        session_code = self._generate_session_code()
        
        # Parse datetime strings
        start_at = None
        end_at = None
        if session_data.get('start_at'):
            start_at = datetime.fromisoformat(session_data['start_at'].replace('Z', '+00:00'))
        if session_data.get('end_at'):
            end_at = datetime.fromisoformat(session_data['end_at'].replace('Z', '+00:00'))
        
        # Create auction session
        session = AuctionSession(
            code=session_code,
            name=session_data['name'].strip(),
            description=session_data.get('description', '').strip(),
            start_at=start_at,
            end_at=end_at,
            status=SessionStatus.DRAFT,
            assigned_staff_id=session_data.get('assigned_staff_id'),
            rules=session_data.get('rules', {})
        )
        
        # Save session
        created_session = self.session_repository.create(session)
        self.session_repository.commit()
        
        return self._session_to_dict(created_session)
    
    def get_auction_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get auction session by ID"""
        session = self.session_repository.get_by_id(session_id)
        if not session:
            return None
        
        return self._session_to_dict(session)
    
    def get_session_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get auction session by code"""
        session = self.session_repository.get_by_code(code)
        if not session:
            return None
        
        return self._session_to_dict(session)
    
    def list_auction_sessions(self, filters: Optional[Dict[str, Any]] = None, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """List auction sessions with pagination"""
        sessions = self.session_repository.list(filters, page, page_size)
        total_count = self.session_repository.count(filters)
        
        return {
            'items': [self._session_to_dict(session) for session in sessions],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
    
    def update_auction_session(self, session_id: str, user_role: UserRole, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update auction session"""
        # Only staff and above can update sessions
        if user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to update auction sessions")
        
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")
        
        # Check if session can be updated
        if session.status not in [SessionStatus.DRAFT, SessionStatus.SCHEDULED]:
            raise BusinessRuleViolationError("Cannot update session in current status")
        
        # Update allowed fields
        if 'name' in updates:
            session.name = updates['name'].strip()
        
        if 'description' in updates:
            session.description = updates['description'].strip()
        
        if 'start_at' in updates:
            session.start_at = datetime.fromisoformat(updates['start_at'].replace('Z', '+00:00'))
        
        if 'end_at' in updates:
            session.end_at = datetime.fromisoformat(updates['end_at'].replace('Z', '+00:00'))
        
        if 'assigned_staff_id' in updates:
            session.assigned_staff_id = updates['assigned_staff_id']
        
        if 'rules' in updates:
            session.rules = updates['rules']
        
        session.updated_at = datetime.utcnow()
        
        # Save changes
        updated_session = self.session_repository.update(session)
        self.session_repository.commit()
        
        return self._session_to_dict(updated_session)
    
    def add_item_to_session(self, session_id: str, jewelry_item_id: str, user_role: UserRole, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add jewelry item to auction session"""
        # Only staff and above can add items to sessions
        if user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to add items to sessions")
        
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")
        
        jewelry_item = self.jewelry_repository.get_by_id(jewelry_item_id)
        if not jewelry_item:
            raise NotFoundError("Jewelry item not found")
        
        # Check if session can have items added
        if session.status not in [SessionStatus.DRAFT, SessionStatus.SCHEDULED]:
            raise BusinessRuleViolationError("Cannot add items to session in current status")
        
        # Check if jewelry item is approved
        if jewelry_item.status != JewelryStatus.APPROVED:
            raise BusinessRuleViolationError("Jewelry item must be approved before adding to session")
        
        # Generate lot number
        lot_number = self._generate_lot_number(session_id)
        
        # Create session item
        session_item = SessionItem(
            session_id=session_id,
            jewelry_item_id=jewelry_item_id,
            reserve_price=Decimal(str(item_data.get('reserve_price', 0))),
            start_price=Decimal(str(item_data.get('start_price', 1))),
            step_price=Decimal(str(item_data.get('step_price', 1))),
            lot_number=lot_number
        )
        
        # Save session item
        created_item = self.session_item_repository.create(session_item)
        
        # Update jewelry item status
        jewelry_item.status = JewelryStatus.IN_AUCTION
        jewelry_item.updated_at = datetime.utcnow()
        self.jewelry_repository.update(jewelry_item)
        
        self.session_repository.commit()
        
        return self._session_item_to_dict(created_item)
    
    def remove_item_from_session(self, session_id: str, session_item_id: str, user_role: UserRole) -> bool:
        """Remove jewelry item from auction session"""
        # Only staff and above can remove items from sessions
        if user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to remove items from sessions")
        
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")
        
        session_item = self.session_item_repository.get_by_id(session_item_id)
        if not session_item or session_item.session_id != session_id:
            raise NotFoundError("Session item not found")
        
        # Check if session allows item removal
        if session.status not in [SessionStatus.DRAFT, SessionStatus.SCHEDULED]:
            raise BusinessRuleViolationError("Cannot remove items from session in current status")
        
        # Update jewelry item status back to approved
        jewelry_item = self.jewelry_repository.get_by_id(session_item.jewelry_item_id)
        if jewelry_item:
            jewelry_item.status = JewelryStatus.APPROVED
            jewelry_item.updated_at = datetime.utcnow()
            self.jewelry_repository.update(jewelry_item)
        
        # Remove session item
        self.session_item_repository.delete(session_item_id)
        self.session_repository.commit()
        
        return True
    
    def get_session_items(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all items in an auction session"""
        session_items = self.session_item_repository.get_by_session_id(session_id)
        return [self._session_item_to_dict(item) for item in session_items]
    
    def enroll_user_in_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Enroll user in auction session"""
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")
        
        # Check if session allows enrollment
        if session.status not in [SessionStatus.SCHEDULED, SessionStatus.OPEN]:
            raise BusinessRuleViolationError("Session is not open for enrollment")
        
        # Check if user is already enrolled
        existing_enrollment = self.enrollment_repository.get_by_session_and_user(session_id, user_id)
        if existing_enrollment:
            return self._enrollment_to_dict(existing_enrollment)
        
        # Create enrollment
        enrollment = Enrollment(
            session_id=session_id,
            user_id=user_id,
            status=EnrollmentStatus.PENDING
        )
        
        created_enrollment = self.enrollment_repository.create(enrollment)
        self.enrollment_repository.commit()
        
        return self._enrollment_to_dict(created_enrollment)

    def schedule_session(self, session_id: str, user_role: UserRole) -> Dict[str, Any]:
        """Schedule an auction session"""
        if user_role not in [UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to schedule sessions")

        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")

        if session.status != SessionStatus.DRAFT:
            raise BusinessRuleViolationError("Can only schedule draft sessions")

        # Validate session has items and schedule
        session_items = self.session_item_repository.get_by_session_id(session_id)
        if not session_items:
            raise BusinessRuleViolationError("Session must have at least one item to be scheduled")

        if not session.start_at or not session.end_at:
            raise BusinessRuleViolationError("Session must have start and end times to be scheduled")

        # Update status
        session.status = SessionStatus.SCHEDULED
        session.updated_at = datetime.utcnow()

        updated_session = self.session_repository.update(session)
        self.session_repository.commit()

        return self._session_to_dict(updated_session)

    def open_session(self, session_id: str, user_role: UserRole) -> Dict[str, Any]:
        """Open an auction session for bidding"""
        if user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to open sessions")

        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")

        if session.status != SessionStatus.SCHEDULED:
            raise BusinessRuleViolationError("Can only open scheduled sessions")

        # Update status
        session.status = SessionStatus.OPEN
        session.opened_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()

        updated_session = self.session_repository.update(session)
        self.session_repository.commit()

        return self._session_to_dict(updated_session)

    def close_session(self, session_id: str, user_role: UserRole) -> Dict[str, Any]:
        """Close an auction session"""
        if user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to close sessions")

        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")

        if session.status not in [SessionStatus.OPEN, SessionStatus.PAUSED]:
            raise BusinessRuleViolationError("Can only close open or paused sessions")

        # Update status
        session.status = SessionStatus.CLOSED
        session.closed_at = datetime.utcnow()
        session.updated_at = datetime.utcnow()

        updated_session = self.session_repository.update(session)
        self.session_repository.commit()

        return self._session_to_dict(updated_session)

    def _generate_session_code(self) -> str:
        """Generate unique session code"""
        while True:
            # Generate random code
            random_part = ''.join(random.choices(string.digits, k=SESSION_CODE_LENGTH - len(SESSION_CODE_PREFIX)))
            code = f"{SESSION_CODE_PREFIX}{random_part}"
            
            # Check if code already exists
            existing = self.session_repository.get_by_code(code)
            if not existing:
                return code
    
    def _generate_lot_number(self, session_id: str) -> int:
        """Generate next lot number for session"""
        existing_items = self.session_item_repository.get_by_session_id(session_id)
        if not existing_items:
            return 1
        
        max_lot = max(item.lot_number for item in existing_items)
        return max_lot + 1
    
    def _session_to_dict(self, session: AuctionSession) -> Dict[str, Any]:
        """Convert auction session to dictionary"""
        return {
            'id': session.id,
            'code': session.code,
            'name': session.name,
            'description': session.description,
            'start_at': session.start_at.isoformat() if session.start_at else None,
            'end_at': session.end_at.isoformat() if session.end_at else None,
            'status': session.status.value,
            'assigned_staff_id': session.assigned_staff_id,
            'rules': session.rules,
            'created_at': session.created_at.isoformat() if session.created_at else None,
            'updated_at': session.updated_at.isoformat() if session.updated_at else None,
            'opened_at': session.opened_at.isoformat() if session.opened_at else None,
            'closed_at': session.closed_at.isoformat() if session.closed_at else None,
            'settled_at': session.settled_at.isoformat() if session.settled_at else None
        }
    
    def _session_item_to_dict(self, session_item: SessionItem) -> Dict[str, Any]:
        """Convert session item to dictionary"""
        return {
            'id': session_item.id,
            'session_id': session_item.session_id,
            'jewelry_item_id': session_item.jewelry_item_id,
            'reserve_price': float(session_item.reserve_price) if session_item.reserve_price else None,
            'start_price': float(session_item.start_price),
            'step_price': float(session_item.step_price),
            'lot_number': session_item.lot_number,
            'current_highest_bid': float(session_item.current_highest_bid) if session_item.current_highest_bid else None,
            'current_winner_id': session_item.current_winner_id,
            'bid_count': session_item.bid_count,
            'version': session_item.version,
            'created_at': session_item.created_at.isoformat() if session_item.created_at else None,
            'updated_at': session_item.updated_at.isoformat() if session_item.updated_at else None
        }
    
    def _enrollment_to_dict(self, enrollment: Enrollment) -> Dict[str, Any]:
        """Convert enrollment to dictionary"""
        return {
            'id': enrollment.id,
            'session_id': enrollment.session_id,
            'user_id': enrollment.user_id,
            'status': enrollment.status.value,
            'approved_by': enrollment.approved_by,
            'approved_at': enrollment.approved_at.isoformat() if enrollment.approved_at else None,
            'created_at': enrollment.created_at.isoformat() if enrollment.created_at else None,
            'updated_at': enrollment.updated_at.isoformat() if enrollment.updated_at else None
        }

    def create_session(self, user_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new auction session (MANAGER only)"""
        # Generate session code
        session_code = self._generate_session_code()

        # Parse dates if provided
        start_at = None
        end_at = None
        if session_data.get('start_at'):
            try:
                start_at = datetime.fromisoformat(session_data['start_at'].replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("Invalid start_at format")

        if session_data.get('end_at'):
            try:
                end_at = datetime.fromisoformat(session_data['end_at'].replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError("Invalid end_at format")

        # Create auction session
        session = AuctionSession(
            code=session_code,
            name=session_data['name'].strip(),
            description=session_data.get('description', '').strip(),
            start_at=start_at,
            end_at=end_at,
            status=SessionStatus.DRAFT,
            assigned_staff_id=user_id
        )

        # Save to database
        created_session = self.session_repository.create(session)
        self.session_repository.commit()

        return self._session_to_dict(created_session)

    def assign_items_to_session(self, session_id: str, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign jewelry items to auction session (MANAGER only)"""
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")

        if session.status != SessionStatus.DRAFT:
            raise BusinessRuleViolationError("Can only assign items to draft sessions")

        jewelry_item_ids = data.get('jewelry_item_ids', [])
        start_prices = data.get('start_prices', {})
        step_prices = data.get('step_prices', {})

        if not jewelry_item_ids:
            raise ValidationError("At least one jewelry item ID is required")

        assigned_items = []

        for jewelry_item_id in jewelry_item_ids:
            # Check if jewelry item exists and is approved
            jewelry_item = self.jewelry_repository.get_by_id(jewelry_item_id)
            if not jewelry_item:
                raise NotFoundError(f"Jewelry item {jewelry_item_id} not found")

            if jewelry_item.status != JewelryStatus.APPROVED:
                raise BusinessRuleViolationError(f"Jewelry item {jewelry_item_id} is not approved for auction")

            # Check if item is already in another active session
            existing_session_item = self.session_item_repository.get_by_jewelry_item_id(jewelry_item_id)
            if existing_session_item:
                raise BusinessRuleViolationError(f"Jewelry item {jewelry_item_id} is already assigned to another session")

            # Create session item
            lot_number = self._generate_lot_number(session_id)
            start_price = Decimal(str(start_prices.get(jewelry_item_id, 1.00)))
            step_price = Decimal(str(step_prices.get(jewelry_item_id, 1.00)))

            session_item = SessionItem(
                session_id=session_id,
                jewelry_item_id=jewelry_item_id,
                lot_number=lot_number,
                reserve_price=jewelry_item.reserve_price,
                start_price=start_price,
                step_price=step_price
            )

            created_item = self.session_item_repository.create(session_item)
            assigned_items.append(self._session_item_to_dict(created_item))

            # Update jewelry item status
            jewelry_item.status = JewelryStatus.IN_AUCTION
            self.jewelry_repository.update(jewelry_item)

        self.session_repository.commit()

        return {
            'session_id': session_id,
            'assigned_items': assigned_items,
            'total_assigned': len(assigned_items)
        }

    def open_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Open an auction session for bidding (MANAGER only)"""
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")

        if session.status != SessionStatus.DRAFT:
            raise BusinessRuleViolationError(f"Cannot open session with status {session.status.value}")

        # Check if session has items
        session_items = self.session_item_repository.get_by_session_id(session_id)
        if not session_items:
            raise BusinessRuleViolationError("Cannot open session without items")

        # Update session status
        session.status = SessionStatus.OPEN
        session.opened_at = datetime.utcnow()

        updated_session = self.session_repository.update(session)
        self.session_repository.commit()

        return self._session_to_dict(updated_session)

    def close_session(self, session_id: str, user_id: str) -> Dict[str, Any]:
        """Close an auction session and determine winners (MANAGER only)"""
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")

        if session.status != SessionStatus.OPEN:
            raise BusinessRuleViolationError(f"Cannot close session with status {session.status.value}")

        # Get all session items and determine winners
        session_items = self.session_item_repository.get_by_session_id(session_id)
        winners = []

        for session_item in session_items:
            if session_item.current_highest_bid and session_item.current_winner_id:
                winners.append({
                    'session_item_id': session_item.id,
                    'jewelry_item_id': session_item.jewelry_item_id,
                    'lot_number': session_item.lot_number,
                    'winner_id': session_item.current_winner_id,
                    'winning_bid': float(session_item.current_highest_bid)
                })

                # Update jewelry item status to SOLD
                jewelry_item = self.jewelry_repository.get_by_id(session_item.jewelry_item_id)
                if jewelry_item:
                    jewelry_item.status = JewelryStatus.SOLD
                    self.jewelry_repository.update(jewelry_item)
            else:
                # No bids - mark as unsold
                jewelry_item = self.jewelry_repository.get_by_id(session_item.jewelry_item_id)
                if jewelry_item:
                    jewelry_item.status = JewelryStatus.UNSOLD
                    self.jewelry_repository.update(jewelry_item)

        # Update session status
        session.status = SessionStatus.CLOSED
        session.closed_at = datetime.utcnow()

        updated_session = self.session_repository.update(session)
        self.session_repository.commit()

        return {
            'session': self._session_to_dict(updated_session),
            'winners': winners,
            'total_winners': len(winners)
        }
