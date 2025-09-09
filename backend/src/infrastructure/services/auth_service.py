"""
Authentication service for the Jewelry Auction System
"""
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import current_app
from domain.enums import UserRole
from domain.exceptions import (
    InvalidCredentialsError, 
    TokenExpiredError, 
    AccountDeactivatedError,
    ValidationError
)


class AuthService:
    """Authentication service"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        if not password or len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long")
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    @staticmethod
    def generate_access_token(user_id: str, role: UserRole, expires_delta: Optional[timedelta] = None) -> str:
        """Generate JWT access token"""
        if expires_delta is None:
            expires_delta = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=1))
        
        expire = datetime.utcnow() + expires_delta
        payload = {
            'user_id': user_id,
            'role': role.value,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config['SECRET_KEY']
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        
        return jwt.encode(payload, secret_key, algorithm=algorithm)
    
    @staticmethod
    def generate_refresh_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Generate JWT refresh token"""
        if expires_delta is None:
            expires_delta = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', timedelta(days=30))
        
        expire = datetime.utcnow() + expires_delta
        payload = {
            'user_id': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config['SECRET_KEY']
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        
        return jwt.encode(payload, secret_key, algorithm=algorithm)
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate JWT token"""
        try:
            secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config['SECRET_KEY']
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.InvalidTokenError:
            raise InvalidCredentialsError()
    
    @staticmethod
    def validate_access_token(token: str) -> Dict[str, Any]:
        """Validate access token and return payload"""
        payload = AuthService.decode_token(token)
        
        if payload.get('type') != 'access':
            raise InvalidCredentialsError()
        
        return payload
    
    @staticmethod
    def validate_refresh_token(token: str) -> Dict[str, Any]:
        """Validate refresh token and return payload"""
        payload = AuthService.decode_token(token)
        
        if payload.get('type') != 'refresh':
            raise InvalidCredentialsError()
        
        return payload
    
    @staticmethod
    def extract_token_from_header(auth_header: str) -> Optional[str]:
        """Extract token from Authorization header"""
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]


class PasswordService:
    """Password management service"""
    
    @staticmethod
    def validate_password_strength(password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"
        
        return True, ""
    
    @staticmethod
    def generate_reset_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """Generate password reset token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=1)  # Reset tokens expire in 1 hour
        
        expire = datetime.utcnow() + expires_delta
        payload = {
            'user_id': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'password_reset'
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config['SECRET_KEY']
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        
        return jwt.encode(payload, secret_key, algorithm=algorithm)
    
    @staticmethod
    def validate_reset_token(token: str) -> Dict[str, Any]:
        """Validate password reset token"""
        payload = AuthService.decode_token(token)
        
        if payload.get('type') != 'password_reset':
            raise InvalidCredentialsError()
        
        return payload


class EmailVerificationService:
    """Email verification service"""
    
    @staticmethod
    def generate_verification_token(user_id: str, email: str, expires_delta: Optional[timedelta] = None) -> str:
        """Generate email verification token"""
        if expires_delta is None:
            expires_delta = timedelta(days=7)  # Verification tokens expire in 7 days
        
        expire = datetime.utcnow() + expires_delta
        payload = {
            'user_id': user_id,
            'email': email,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'email_verification'
        }
        
        secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config['SECRET_KEY']
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        
        return jwt.encode(payload, secret_key, algorithm=algorithm)
    
    @staticmethod
    def validate_verification_token(token: str) -> Dict[str, Any]:
        """Validate email verification token"""
        payload = AuthService.decode_token(token)
        
        if payload.get('type') != 'email_verification':
            raise InvalidCredentialsError()
        
        return payload
