"""
User domain entity
"""
from datetime import datetime
from typing import Optional, List
from domain.enums import UserRole


class User:
    """User domain entity"""
    
    def __init__(
        self,
        id: Optional[str] = None,
        name: str = "",
        email: str = "",
        password_hash: str = "",
        role: UserRole = UserRole.MEMBER,
        is_active: bool = True,
        phone: Optional[str] = None,
        address: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.is_active = is_active
        self.phone = phone
        self.address = address
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role"""
        return self.role == role
    
    def has_permission(self, required_roles: List[UserRole]) -> bool:
        """Check if user has any of the required roles"""
        return self.role in required_roles
    
    def is_staff_or_above(self) -> bool:
        """Check if user is staff, manager, or admin"""
        return self.role in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]
    
    def is_manager_or_above(self) -> bool:
        """Check if user is manager or admin"""
        return self.role in [UserRole.MANAGER, UserRole.ADMIN]
    
    def is_admin(self) -> bool:
        """Check if user is admin"""
        return self.role == UserRole.ADMIN
    
    def can_sell(self) -> bool:
        """Check if user can sell items"""
        return self.role in [UserRole.MEMBER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]
    
    def can_bid(self) -> bool:
        """Check if user can place bids"""
        return self.role in [UserRole.MEMBER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]
    
    def can_manage_auctions(self) -> bool:
        """Check if user can manage auction sessions"""
        return self.role in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]
    
    def can_approve_items(self) -> bool:
        """Check if user can approve jewelry items"""
        return self.role in [UserRole.MANAGER, UserRole.ADMIN]
    
    def update_profile(self, name: str = None, phone: str = None, address: str = None):
        """Update user profile information"""
        if name is not None:
            self.name = name
        if phone is not None:
            self.phone = phone
        if address is not None:
            self.address = address
        self.updated_at = datetime.utcnow()
    
    def deactivate(self):
        """Deactivate user account"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def activate(self):
        """Activate user account"""
        self.is_active = True
        self.updated_at = datetime.utcnow()
    
    def __str__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email}, role={self.role.value})"
    
    def __repr__(self):
        return self.__str__()
