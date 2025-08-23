from abc import ABC, abstractmethod
from typing import Optional, List
from src.domain.models.verification_code import VerificationCode, VerificationCodeType

class IVerificationCodeRepository(ABC):
    """Interface for verification code repository"""
    
    @abstractmethod
    def get_by_id(self, code_id: int) -> Optional[VerificationCode]:
        """Get verification code by ID"""
        pass
    
    @abstractmethod
    def get_active_code(self, email: str, code_type: VerificationCodeType) -> Optional[VerificationCode]:
        """Get active verification code for email and type"""
        pass
    
    @abstractmethod
    def create(self, verification_code: VerificationCode) -> VerificationCode:
        """Create new verification code"""
        pass
    
    @abstractmethod
    def update(self, verification_code: VerificationCode) -> VerificationCode:
        """Update existing verification code"""
        pass
    
    @abstractmethod
    def delete(self, code_id: int) -> None:
        """Delete verification code by ID"""
        pass
    
    @abstractmethod
    def get_by_email_and_code(self, email: str, code: str, code_type: VerificationCodeType) -> Optional[VerificationCode]:
        """Get verification code by email, code value, and type"""
        pass
    
    @abstractmethod
    def expire_old_codes(self, email: str, code_type: VerificationCodeType) -> None:
        """Expire all old active codes for email and type"""
        pass
    
    @abstractmethod
    def cleanup_expired_codes(self) -> int:
        """Clean up expired verification codes and return count of deleted codes"""
        pass
    
    @abstractmethod
    def get_user_codes(self, user_id: int, code_type: Optional[VerificationCodeType] = None) -> List[VerificationCode]:
        """Get verification codes for a user, optionally filtered by type"""
        pass
