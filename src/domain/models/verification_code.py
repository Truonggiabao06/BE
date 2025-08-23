from datetime import datetime, timedelta, timezone
from typing import Optional
from enum import Enum
import random
import string

class VerificationCodeType(Enum):
    """Types of verification codes"""
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    PHONE_VERIFICATION = "phone_verification"

class VerificationCodeStatus(Enum):
    """Status of verification codes"""
    ACTIVE = "active"
    USED = "used"
    EXPIRED = "expired"

class VerificationCode:
    """Domain model for verification codes sent via email/SMS"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        user_id: int = None,
        email: str = "",
        code: str = "",
        code_type: VerificationCodeType = VerificationCodeType.EMAIL_VERIFICATION,
        status: VerificationCodeStatus = VerificationCodeStatus.ACTIVE,
        expires_at: Optional[datetime] = None,
        is_used: bool = False,
        used_at: Optional[datetime] = None,
        attempts: int = 0,
        max_attempts: int = 3,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.email = email
        self.code = code or self._generate_code()
        self.code_type = code_type
        self.status = status
        self.expires_at = expires_at or self._calculate_expiry()
        self.is_used = is_used
        self.used_at = used_at
        self.attempts = attempts
        self.max_attempts = max_attempts
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
    
    @property
    def is_expired(self) -> bool:
        """Check if verification code is expired"""
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if verification code is valid for use"""
        return (
            self.status == VerificationCodeStatus.ACTIVE and
            not self.is_expired and
            not self.is_used and
            self.attempts < self.max_attempts
        )
    
    @property
    def time_remaining(self) -> Optional[timedelta]:
        """Get remaining time before expiry"""
        if self.is_expired:
            return timedelta(0)
        return self.expires_at - datetime.now(timezone.utc)
    
    @property
    def remaining_attempts(self) -> int:
        """Get remaining verification attempts"""
        return max(0, self.max_attempts - self.attempts)
    
    def verify(self, input_code: str) -> bool:
        """Verify the input code against stored code"""
        self.attempts += 1
        self.updated_at = datetime.now(timezone.utc)
        
        # Check if code is valid
        if not self.is_valid:
            if self.is_expired:
                self.status = VerificationCodeStatus.EXPIRED
            return False
        
        # Check if code matches
        if self.code == input_code.strip():
            self.is_used = True
            self.used_at = datetime.now(timezone.utc)
            self.status = VerificationCodeStatus.USED
            return True

        # Check if max attempts reached
        if self.attempts >= self.max_attempts:
            self.status = VerificationCodeStatus.EXPIRED

        return False

    def expire(self):
        """Manually expire the verification code"""
        self.status = VerificationCodeStatus.EXPIRED
        self.updated_at = datetime.now(timezone.utc)

    def extend_expiry(self, minutes: int = 10):
        """Extend the expiry time"""
        if self.status == VerificationCodeStatus.ACTIVE:
            self.expires_at = datetime.now(timezone.utc) + timedelta(minutes=minutes)
            self.updated_at = datetime.now(timezone.utc)

    def regenerate_code(self):
        """Generate a new verification code"""
        if self.status == VerificationCodeStatus.ACTIVE:
            self.code = self._generate_code()
            self.expires_at = self._calculate_expiry()
            self.attempts = 0
            self.updated_at = datetime.now(timezone.utc)
    
    def _generate_code(self) -> str:
        """Generate a 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    def _calculate_expiry(self) -> datetime:
        """Calculate expiry time (default: 10 minutes from now)"""
        return datetime.now(timezone.utc) + timedelta(minutes=10)
    
    @staticmethod
    def generate_verification_code(
        user_id: int,
        email: str,
        code_type: VerificationCodeType = VerificationCodeType.EMAIL_VERIFICATION,
        expiry_minutes: int = 10
    ) -> 'VerificationCode':
        """Factory method to create a new verification code"""
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expiry_minutes)
        
        return VerificationCode(
            user_id=user_id,
            email=email,
            code_type=code_type,
            expires_at=expires_at
        )
    
    def __repr__(self):
        return f"<VerificationCode(id={self.id}, email='{self.email}', type='{self.code_type.value}', status='{self.status.value}')>"
