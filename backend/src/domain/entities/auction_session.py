"""
Auction Session domain entity
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from domain.enums import SessionStatus


class AuctionSession:
    """Auction Session domain entity"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        code: str = "",
        name: str = "",
        description: str = "",
        start_at: Optional[datetime] = None,
        end_at: Optional[datetime] = None,
        status: SessionStatus = SessionStatus.DRAFT,
        assigned_staff_id: Optional[str] = None,
        rules: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        opened_at: Optional[datetime] = None,
        closed_at: Optional[datetime] = None,
        settled_at: Optional[datetime] = None
    ):
        self.id = id
        self.code = code
        self.name = name
        self.description = description
        self.start_at = start_at
        self.end_at = end_at
        self.status = status
        self.assigned_staff_id = assigned_staff_id
        self.rules = rules or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.opened_at = opened_at
        self.closed_at = closed_at
        self.settled_at = settled_at
    
    def update_status(self, new_status: SessionStatus):
        """Update session status with validation"""
        if self.can_transition_to(new_status):
            old_status = self.status
            self.status = new_status
            self.updated_at = datetime.utcnow()
            
            # Set specific timestamps
            if new_status == SessionStatus.OPEN:
                self.opened_at = datetime.utcnow()
            elif new_status == SessionStatus.CLOSED:
                self.closed_at = datetime.utcnow()
            elif new_status == SessionStatus.SETTLED:
                self.settled_at = datetime.utcnow()
                
        else:
            raise ValueError(f"Cannot transition from {self.status.value} to {new_status.value}")
    
    def can_transition_to(self, new_status: SessionStatus) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            SessionStatus.DRAFT: [
                SessionStatus.SCHEDULED,
                SessionStatus.CANCELED
            ],
            SessionStatus.SCHEDULED: [
                SessionStatus.OPEN,
                SessionStatus.CANCELED
            ],
            SessionStatus.OPEN: [
                SessionStatus.PAUSED,
                SessionStatus.CLOSED
            ],
            SessionStatus.PAUSED: [
                SessionStatus.OPEN,
                SessionStatus.CLOSED
            ],
            SessionStatus.CLOSED: [
                SessionStatus.SETTLED
            ],
            SessionStatus.SETTLED: [],  # Final state
            SessionStatus.CANCELED: []  # Final state
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
    def schedule(self, start_at: datetime, end_at: datetime):
        """Schedule the auction session"""
        if self.status != SessionStatus.DRAFT:
            raise ValueError("Can only schedule draft sessions")
        
        if start_at >= end_at:
            raise ValueError("Start time must be before end time")
        
        if start_at <= datetime.utcnow():
            raise ValueError("Start time must be in the future")
        
        self.start_at = start_at
        self.end_at = end_at
        self.update_status(SessionStatus.SCHEDULED)
    
    def open_session(self):
        """Open the auction session for bidding"""
        if self.status != SessionStatus.SCHEDULED:
            raise ValueError("Can only open scheduled sessions")
        
        now = datetime.utcnow()
        if self.start_at and now < self.start_at:
            raise ValueError("Cannot open session before scheduled start time")
        
        self.update_status(SessionStatus.OPEN)
    
    def pause_session(self):
        """Pause the auction session"""
        if self.status != SessionStatus.OPEN:
            raise ValueError("Can only pause open sessions")
        
        self.update_status(SessionStatus.PAUSED)
    
    def resume_session(self):
        """Resume the auction session"""
        if self.status != SessionStatus.PAUSED:
            raise ValueError("Can only resume paused sessions")
        
        self.update_status(SessionStatus.OPEN)
    
    def close_session(self):
        """Close the auction session"""
        if self.status not in [SessionStatus.OPEN, SessionStatus.PAUSED]:
            raise ValueError("Can only close open or paused sessions")
        
        self.update_status(SessionStatus.CLOSED)
    
    def settle_session(self):
        """Settle the auction session (finalize all transactions)"""
        if self.status != SessionStatus.CLOSED:
            raise ValueError("Can only settle closed sessions")
        
        self.update_status(SessionStatus.SETTLED)
    
    def cancel_session(self):
        """Cancel the auction session"""
        if self.status in [SessionStatus.SETTLED, SessionStatus.CANCELED]:
            raise ValueError("Cannot cancel settled or already canceled sessions")
        
        self.update_status(SessionStatus.CANCELED)
    
    def assign_staff(self, staff_id: str):
        """Assign staff member to manage the session"""
        self.assigned_staff_id = staff_id
        self.updated_at = datetime.utcnow()
    
    def update_rules(self, rules: Dict[str, Any]):
        """Update session rules"""
        self.rules.update(rules)
        self.updated_at = datetime.utcnow()
    
    def set_rule(self, key: str, value: Any):
        """Set a specific rule"""
        self.rules[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_rule(self, key: str, default: Any = None) -> Any:
        """Get a specific rule"""
        return self.rules.get(key, default)
    
    def is_active(self) -> bool:
        """Check if session is currently active (open or paused)"""
        return self.status in [SessionStatus.OPEN, SessionStatus.PAUSED]
    
    def is_open_for_bidding(self) -> bool:
        """Check if session is open for bidding"""
        return self.status == SessionStatus.OPEN
    
    def is_finished(self) -> bool:
        """Check if session is finished"""
        return self.status in [SessionStatus.CLOSED, SessionStatus.SETTLED, SessionStatus.CANCELED]
    
    def can_accept_bids(self) -> bool:
        """Check if session can accept new bids"""
        return self.status == SessionStatus.OPEN
    
    def update_details(self, name: str = None, description: str = None):
        """Update session details"""
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        self.updated_at = datetime.utcnow()
    
    def get_duration_minutes(self) -> Optional[int]:
        """Get session duration in minutes"""
        if self.start_at and self.end_at:
            return int((self.end_at - self.start_at).total_seconds() / 60)
        return None

    def is_scheduled_to_start(self) -> bool:
        """Check if session is scheduled to start now"""
        if self.status != SessionStatus.SCHEDULED or not self.start_at:
            return False
        return datetime.utcnow() >= self.start_at

    def is_scheduled_to_end(self) -> bool:
        """Check if session is scheduled to end now"""
        if self.status != SessionStatus.OPEN or not self.end_at:
            return False
        return datetime.utcnow() >= self.end_at

    def __str__(self):
        return f"AuctionSession(id={self.id}, code={self.code}, name={self.name}, status={self.status.value})"

    def __repr__(self):
        return self.__str__()
