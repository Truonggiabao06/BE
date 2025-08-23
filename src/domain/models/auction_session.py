from datetime import datetime, timedelta
from typing import Optional, List
from enum import Enum
from decimal import Decimal

class SessionStatus(Enum):
    """Status of auction sessions"""
    SCHEDULED = "scheduled"      # Đã lên lịch
    ACTIVE = "active"           # Đang diễn ra
    PAUSED = "paused"           # Tạm dừng
    COMPLETED = "completed"     # Đã kết thúc
    CANCELLED = "cancelled"     # Đã hủy

class AuctionSession:
    """Domain model for auction sessions"""

    def __init__(
        self,
        id: Optional[int] = None,
        title: str = "",
        description: str = "",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: SessionStatus = SessionStatus.SCHEDULED,
        item_ids: Optional[List[int]] = None,  # List of auction item IDs
        min_bid_increment: Decimal = Decimal('10.00'),  # Minimum bid increment
        registration_required: bool = True,
        max_participants: Optional[int] = None,
        created_by: Optional[int] = None,  # Staff ID who created the session
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        started_at: Optional[datetime] = None,
        ended_at: Optional[datetime] = None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.item_ids = item_ids or []
        self.min_bid_increment = min_bid_increment
        self.registration_required = registration_required
        self.max_participants = max_participants
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.started_at = started_at
        self.ended_at = ended_at

    @property
    def is_scheduled(self) -> bool:
        """Check if session is scheduled"""
        return self.status == SessionStatus.SCHEDULED

    @property
    def is_active(self) -> bool:
        """Check if session is currently active"""
        return self.status == SessionStatus.ACTIVE

    @property
    def is_completed(self) -> bool:
        """Check if session is completed"""
        return self.status == SessionStatus.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """Check if session is cancelled"""
        return self.status == SessionStatus.CANCELLED

    @property
    def duration_minutes(self) -> Optional[int]:
        """Get session duration in minutes"""
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return None

    @property
    def can_start(self) -> bool:
        """Check if session can be started"""
        now = datetime.utcnow()
        return (
            self.status == SessionStatus.SCHEDULED and
            self.start_time and
            now >= self.start_time and
            len(self.item_ids) > 0
        )

    @property
    def should_end(self) -> bool:
        """Check if session should end based on end time"""
        if not self.end_time or self.status != SessionStatus.ACTIVE:
            return False
        return datetime.utcnow() >= self.end_time

    @property
    def time_remaining(self) -> Optional[timedelta]:
        """Get remaining time for active session"""
        if self.status == SessionStatus.ACTIVE and self.end_time:
            remaining = self.end_time - datetime.utcnow()
            return remaining if remaining.total_seconds() > 0 else timedelta(0)
        return None

    def add_item(self, item_id: int):
        """Add an item to the auction session"""
        if self.status == SessionStatus.ACTIVE:
            raise ValueError("Cannot add items to active session")
        if item_id not in self.item_ids:
            self.item_ids.append(item_id)
            self.updated_at = datetime.utcnow()

    def remove_item(self, item_id: int):
        """Remove an item from the auction session"""
        if self.status == SessionStatus.ACTIVE:
            raise ValueError("Cannot remove items from active session")
        if item_id in self.item_ids:
            self.item_ids.remove(item_id)
            self.updated_at = datetime.utcnow()

    def start_session(self):
        """Start the auction session"""
        if not self.can_start:
            raise ValueError("Session cannot be started")
        self.status = SessionStatus.ACTIVE
        self.started_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def pause_session(self):
        """Pause the auction session"""
        if self.status != SessionStatus.ACTIVE:
            raise ValueError("Can only pause active sessions")
        self.status = SessionStatus.PAUSED
        self.updated_at = datetime.utcnow()

    def resume_session(self):
        """Resume a paused auction session"""
        if self.status != SessionStatus.PAUSED:
            raise ValueError("Can only resume paused sessions")
        self.status = SessionStatus.ACTIVE
        self.updated_at = datetime.utcnow()

    def end_session(self):
        """End the auction session"""
        if self.status not in [SessionStatus.ACTIVE, SessionStatus.PAUSED]:
            raise ValueError("Can only end active or paused sessions")
        self.status = SessionStatus.COMPLETED
        self.ended_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def cancel_session(self):
        """Cancel the auction session"""
        if self.status == SessionStatus.COMPLETED:
            raise ValueError("Cannot cancel completed session")
        self.status = SessionStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def extend_session(self, additional_minutes: int):
        """Extend the session by additional minutes"""
        if not self.end_time:
            raise ValueError("Session must have an end time to extend")
        self.end_time += timedelta(minutes=additional_minutes)
        self.updated_at = datetime.utcnow()

    def update_details(self, **kwargs):
        """Update session details"""
        if self.status == SessionStatus.ACTIVE:
            raise ValueError("Cannot update details of active session")

        allowed_fields = [
            'title', 'description', 'start_time', 'end_time',
            'min_bid_increment', 'registration_required', 'max_participants'
        ]
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<AuctionSession(id={self.id}, title='{self.title}', status='{self.status.value}')>"