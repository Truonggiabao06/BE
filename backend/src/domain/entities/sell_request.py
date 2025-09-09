"""
Sell Request domain entity
"""
from datetime import datetime
from typing import Optional
from domain.enums import SellRequestStatus


class SellRequest:
    """Sell Request domain entity for jewelry consignment"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        seller_id: str = "",
        jewelry_item_id: str = "",
        status: SellRequestStatus = SellRequestStatus.SUBMITTED,
        notes: str = "",
        seller_notes: str = "",
        staff_notes: str = "",
        manager_notes: str = "",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        submitted_at: Optional[datetime] = None,
        appraised_at: Optional[datetime] = None,
        approved_at: Optional[datetime] = None,
        accepted_at: Optional[datetime] = None
    ):
        self.id = id
        self.seller_id = seller_id
        self.jewelry_item_id = jewelry_item_id
        self.status = status
        self.notes = notes
        self.seller_notes = seller_notes
        self.staff_notes = staff_notes
        self.manager_notes = manager_notes
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.submitted_at = submitted_at
        self.appraised_at = appraised_at
        self.approved_at = approved_at
        self.accepted_at = accepted_at
    
    def update_status(self, new_status: SellRequestStatus, notes: str = ""):
        """Update sell request status with validation"""
        if self.can_transition_to(new_status):
            old_status = self.status
            self.status = new_status
            self.updated_at = datetime.utcnow()
            
            # Set specific timestamps
            if new_status == SellRequestStatus.SUBMITTED:
                self.submitted_at = datetime.utcnow()
            elif new_status == SellRequestStatus.FINAL_APPRAISED:
                self.appraised_at = datetime.utcnow()
            elif new_status == SellRequestStatus.MANAGER_APPROVED:
                self.approved_at = datetime.utcnow()
            elif new_status == SellRequestStatus.SELLER_ACCEPTED:
                self.accepted_at = datetime.utcnow()
            
            # Add notes if provided
            if notes:
                self.add_notes(notes)
                
        else:
            raise ValueError(f"Cannot transition from {self.status.value} to {new_status.value}")
    
    def can_transition_to(self, new_status: SellRequestStatus) -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            SellRequestStatus.SUBMITTED: [
                SellRequestStatus.PRELIM_APPRAISED,
                SellRequestStatus.REJECTED
            ],
            SellRequestStatus.PRELIM_APPRAISED: [
                SellRequestStatus.RECEIVED,
                SellRequestStatus.REJECTED
            ],
            SellRequestStatus.RECEIVED: [
                SellRequestStatus.FINAL_APPRAISED,
                SellRequestStatus.REJECTED
            ],
            SellRequestStatus.FINAL_APPRAISED: [
                SellRequestStatus.MANAGER_APPROVED,
                SellRequestStatus.REJECTED
            ],
            SellRequestStatus.MANAGER_APPROVED: [
                SellRequestStatus.SELLER_ACCEPTED,
                SellRequestStatus.REJECTED
            ],
            SellRequestStatus.SELLER_ACCEPTED: [
                SellRequestStatus.ASSIGNED_TO_SESSION
            ],
            SellRequestStatus.ASSIGNED_TO_SESSION: [],  # Final state
            SellRequestStatus.REJECTED: []  # Final state
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
    def add_notes(self, notes: str):
        """Add notes to the request"""
        if self.notes:
            self.notes += f"\n{datetime.utcnow().isoformat()}: {notes}"
        else:
            self.notes = f"{datetime.utcnow().isoformat()}: {notes}"
        self.updated_at = datetime.utcnow()
    
    def add_staff_notes(self, notes: str):
        """Add staff-specific notes"""
        if self.staff_notes:
            self.staff_notes += f"\n{datetime.utcnow().isoformat()}: {notes}"
        else:
            self.staff_notes = f"{datetime.utcnow().isoformat()}: {notes}"
        self.updated_at = datetime.utcnow()
    
    def add_manager_notes(self, notes: str):
        """Add manager-specific notes"""
        if self.manager_notes:
            self.manager_notes += f"\n{datetime.utcnow().isoformat()}: {notes}"
        else:
            self.manager_notes = f"{datetime.utcnow().isoformat()}: {notes}"
        self.updated_at = datetime.utcnow()
    
    def is_pending(self) -> bool:
        """Check if request is still pending"""
        return self.status not in [
            SellRequestStatus.ASSIGNED_TO_SESSION,
            SellRequestStatus.REJECTED
        ]
    
    def is_approved(self) -> bool:
        """Check if request is approved"""
        return self.status in [
            SellRequestStatus.MANAGER_APPROVED,
            SellRequestStatus.SELLER_ACCEPTED,
            SellRequestStatus.ASSIGNED_TO_SESSION
        ]
    
    def is_rejected(self) -> bool:
        """Check if request is rejected"""
        return self.status == SellRequestStatus.REJECTED
    
    def is_ready_for_auction(self) -> bool:
        """Check if request is ready to be assigned to auction"""
        return self.status == SellRequestStatus.SELLER_ACCEPTED
    
    def __str__(self):
        return f"SellRequest(id={self.id}, seller_id={self.seller_id}, status={self.status.value})"
    
    def __repr__(self):
        return self.__str__()
