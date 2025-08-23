from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.domain.models.user import User, UserRole, UserStatus
from src.domain.models.verification_code import VerificationCode, VerificationCodeType

class AuthResult:
    """Result object for authentication operations"""
    
    def __init__(self, success: bool, message: str = "", user: Optional[User] = None, token: Optional[str] = None, data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.user = user
        self.token = token
        self.data = data or {}
    
    def __bool__(self):
        return self.success

class IAuthService(ABC):
    """Interface for authentication service"""
    
    @abstractmethod
    def register(self, email: str, password: str, first_name: str, last_name: str, phone_number: str = "", role: UserRole = UserRole.BUYER) -> AuthResult:
        """Register new user and send verification code"""
        pass
    
    @abstractmethod
    def verify_email(self, email: str, code: str) -> AuthResult:
        """Verify email with verification code"""
        pass
    
    @abstractmethod
    def resend_verification_code(self, email: str) -> AuthResult:
        """Resend verification code to email"""
        pass
    
    @abstractmethod
    def login(self, email: str, password: str) -> AuthResult:
        """Login user with email and password"""
        pass
    
    @abstractmethod
    def logout(self, token: str) -> AuthResult:
        """Logout user and invalidate token"""
        pass
    
    @abstractmethod
    def forgot_password(self, email: str) -> AuthResult:
        """Send password reset code to email"""
        pass
    
    @abstractmethod
    def reset_password(self, email: str, code: str, new_password: str) -> AuthResult:
        """Reset password with verification code"""
        pass
    
    @abstractmethod
    def change_password(self, user_id: int, old_password: str, new_password: str) -> AuthResult:
        """Change password for authenticated user"""
        pass
    
    @abstractmethod
    def validate_token(self, token: str) -> AuthResult:
        """Validate JWT token and return user"""
        pass
    
    @abstractmethod
    def refresh_token(self, refresh_token: str) -> AuthResult:
        """Refresh JWT token"""
        pass
    
    @abstractmethod
    def get_user_profile(self, user_id: int) -> AuthResult:
        """Get user profile by ID"""
        pass
    
    @abstractmethod
    def update_user_profile(self, user_id: int, **kwargs) -> AuthResult:
        """Update user profile"""
        pass
