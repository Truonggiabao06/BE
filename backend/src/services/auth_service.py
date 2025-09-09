"""
Authentication service for the Jewelry Auction System
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from domain.entities.user import User
from domain.enums import UserRole
from domain.exceptions import (
    InvalidCredentialsError, 
    AccountDeactivatedError, 
    DuplicateEmailError,
    ValidationError,
    NotFoundError
)
from domain.repositories.base_repository import IUserRepository
from infrastructure.services.auth_service import AuthService as InfraAuthService, PasswordService
from infrastructure.repositories.user_repository import UserRepository


class AuthenticationService:
    """Authentication business service"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    def register_user(self, name: str, email: str, password: str, role: UserRole = UserRole.MEMBER) -> Dict[str, Any]:
        """Register a new user"""
        # Validate input
        if not name or not name.strip():
            raise ValidationError("Name is required")
        
        if not email or not email.strip():
            raise ValidationError("Email is required")
        
        # Validate email format (basic validation)
        if '@' not in email or '.' not in email:
            raise ValidationError("Invalid email format")
        
        # Validate password strength
        is_valid, error_message = PasswordService.validate_password_strength(password)
        if not is_valid:
            raise ValidationError(error_message)
        
        # Check if email already exists
        existing_user = self.user_repository.get_by_email(email.lower())
        if existing_user:
            raise DuplicateEmailError()
        
        # Hash password
        password_hash = InfraAuthService.hash_password(password)
        
        # Create user entity
        user = User(
            name=name.strip(),
            email=email.lower().strip(),
            password_hash=password_hash,
            role=role,
            is_active=True
        )
        
        # Save user
        created_user = self.user_repository.create(user)
        self.user_repository.commit()
        
        # Generate tokens
        access_token = InfraAuthService.generate_access_token(created_user.id, created_user.role)
        refresh_token = InfraAuthService.generate_refresh_token(created_user.id)
        
        return {
            'user': {
                'id': created_user.id,
                'name': created_user.name,
                'email': created_user.email,
                'role': created_user.role.value,
                'is_active': created_user.is_active
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return tokens"""
        if not email or not password:
            raise InvalidCredentialsError()
        
        # Get user by email
        user = self.user_repository.get_by_email(email.lower())
        if not user:
            raise InvalidCredentialsError()
        
        # Check if account is active
        if not user.is_active:
            raise AccountDeactivatedError()
        
        # Verify password
        if not InfraAuthService.verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        self.user_repository.update(user)
        self.user_repository.commit()
        
        # Generate tokens
        access_token = InfraAuthService.generate_access_token(user.id, user.role)
        refresh_token = InfraAuthService.generate_refresh_token(user.id)
        
        return {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role.value,
                'is_active': user.is_active
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token"""
        try:
            # Validate refresh token
            payload = InfraAuthService.validate_refresh_token(refresh_token)
            user_id = payload['user_id']
            
            # Get user to ensure they still exist and are active
            user = self.user_repository.get_by_id(user_id)
            if not user or not user.is_active:
                raise InvalidCredentialsError()
            
            # Generate new access token
            access_token = InfraAuthService.generate_access_token(user.id, user.role)
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token  # Keep the same refresh token
            }
            
        except Exception:
            raise InvalidCredentialsError()
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """Change user password"""
        # Get user
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Verify current password
        if not InfraAuthService.verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError()
        
        # Validate new password strength
        is_valid, error_message = PasswordService.validate_password_strength(new_password)
        if not is_valid:
            raise ValidationError(error_message)
        
        # Hash new password
        new_password_hash = InfraAuthService.hash_password(new_password)
        
        # Update user
        user.password_hash = new_password_hash
        user.updated_at = datetime.utcnow()
        
        self.user_repository.update(user)
        self.user_repository.commit()
        
        return True
    
    def reset_password(self, email: str) -> str:
        """Generate password reset token"""
        user = self.user_repository.get_by_email(email.lower())
        if not user:
            # Don't reveal if email exists or not
            return "If the email exists, a reset link has been sent"
        
        if not user.is_active:
            raise AccountDeactivatedError()
        
        # Generate reset token
        reset_token = PasswordService.generate_reset_token(user.id)
        
        # TODO: Send email with reset token
        # EmailService.send_password_reset_email(user.email, reset_token)
        
        return reset_token  # In production, don't return the token directly
    
    def confirm_password_reset(self, reset_token: str, new_password: str) -> bool:
        """Confirm password reset with token"""
        try:
            # Validate reset token
            payload = PasswordService.validate_reset_token(reset_token)
            user_id = payload['user_id']
            
            # Get user
            user = self.user_repository.get_by_id(user_id)
            if not user or not user.is_active:
                raise InvalidCredentialsError()
            
            # Validate new password strength
            is_valid, error_message = PasswordService.validate_password_strength(new_password)
            if not is_valid:
                raise ValidationError(error_message)
            
            # Hash new password
            new_password_hash = InfraAuthService.hash_password(new_password)
            
            # Update user
            user.password_hash = new_password_hash
            user.updated_at = datetime.utcnow()
            
            self.user_repository.update(user)
            self.user_repository.commit()
            
            return True
            
        except Exception:
            raise InvalidCredentialsError()
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None
        
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role.value,
            'is_active': user.is_active,
            'phone': user.phone,
            'address': user.address,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }
    
    def update_user_profile(self, user_id: str, name: str = None, phone: str = None, address: str = None) -> Dict[str, Any]:
        """Update user profile"""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise NotFoundError("User not found")
        
        # Update fields
        if name is not None:
            user.name = name.strip()
        if phone is not None:
            user.phone = phone.strip() if phone else None
        if address is not None:
            user.address = address.strip() if address else None
        
        user.updated_at = datetime.utcnow()
        
        updated_user = self.user_repository.update(user)
        self.user_repository.commit()
        
        return {
            'id': updated_user.id,
            'name': updated_user.name,
            'email': updated_user.email,
            'role': updated_user.role.value,
            'is_active': updated_user.is_active,
            'phone': updated_user.phone,
            'address': updated_user.address,
            'updated_at': updated_user.updated_at.isoformat() if updated_user.updated_at else None
        }
