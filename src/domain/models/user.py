from datetime import datetime
from typing import Optional, List
from enum import Enum

class UserRole(Enum):
    """User roles in the auction system"""
    GUEST = "guest"
    BUYER = "buyer"
    SELLER = "seller"
    STAFF = "staff"
    MANAGER = "manager"
    ADMIN = "admin"

class UserStatus(Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"

class User:
    """Domain model for User entity in auction system"""

    def __init__(
        self,
        id: Optional[int] = None,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        phone_number: str = "",
        password_hash: str = "",
        role: UserRole = UserRole.BUYER,
        status: UserStatus = UserStatus.PENDING_VERIFICATION,
        bio: Optional[str] = None,
        image_url: Optional[str] = None,
        address: Optional[str] = None,
        is_email_verified: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.password_hash = password_hash
        self.role = role
        self.status = status
        self.bio = bio
        self.image_url = image_url
        self.address = address
        self.is_email_verified = is_email_verified
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    @property
    def full_name(self) -> str:
        """Get user's full name"""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_active(self) -> bool:
        """Check if user account is active"""
        return self.status == UserStatus.ACTIVE

    @property
    def can_sell(self) -> bool:
        """Check if user can sell items"""
        return self.role in [UserRole.SELLER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN] and self.is_active

    @property
    def can_buy(self) -> bool:
        """Check if user can participate in auctions"""
        return self.role in [UserRole.BUYER, UserRole.SELLER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN] and self.is_active

    @property
    def is_staff(self) -> bool:
        """Check if user is staff member"""
        return self.role in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]

    def activate_account(self):
        """Activate user account after email verification"""
        self.status = UserStatus.ACTIVE
        self.is_email_verified = True
        self.updated_at = datetime.utcnow()

    def suspend_account(self):
        """Suspend user account"""
        self.status = UserStatus.SUSPENDED
        self.updated_at = datetime.utcnow()

    def update_profile(self, **kwargs):
        """Update user profile information"""
        allowed_fields = ['first_name', 'last_name', 'phone_number', 'bio', 'image_url', 'address']
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"