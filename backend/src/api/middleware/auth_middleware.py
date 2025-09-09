"""
Authentication middleware for the Jewelry Auction System
"""
from functools import wraps
from typing import List, Optional, Callable
import jwt
from flask import request, g, jsonify, current_app
from domain.enums import UserRole
from infrastructure.databases.mssql import db
from infrastructure.models.user_model import UserModel
from domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    InvalidCredentialsError,
    AccountDeactivatedError,
    InsufficientPermissionsError
)
from infrastructure.services.auth_service import AuthService


def _decode_jwt_token(token: str) -> dict:
    """Decode JWT token with fallback for different token types"""
    try:
        # First try Flask-JWT-Extended format
        secret_key = current_app.config.get('JWT_SECRET_KEY') or current_app.config['SECRET_KEY']
        algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except Exception:
        # Fallback to custom AuthService validation
        try:
            return AuthService.validate_access_token(token)
        except Exception as e:
            current_app.logger.error(f"JWT decode error: {str(e)}")
            raise InvalidCredentialsError()


def _get_user_id_from_email(email: str) -> Optional[str]:
    """Get user ID from email address"""
    try:
        user = db.session.query(UserModel).filter_by(email=email).first()
        return user.id if user else None
    except Exception as e:
        current_app.logger.warning(f"Failed to lookup user by email {email}: {e}")
        return None


def jwt_required(f: Callable) -> Callable:
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            token = AuthService.extract_token_from_header(auth_header)
            
            if not token:
                return jsonify({
                    'error': 'Authentication required',
                    'code': 'MISSING_TOKEN'
                }), 401
            
            # Validate token
            payload = _decode_jwt_token(token)

            # Store user info in Flask's g object
            # Handle both custom JWT (user_id) and Flask-JWT-Extended (sub)
            user_id = payload.get('user_id') or payload.get('sub')

            # If user_id looks like an email, convert to actual user ID
            if user_id and '@' in str(user_id):
                user_id = _get_user_id_from_email(user_id)

            g.current_user_id = user_id

            # Handle role - custom JWT has role field, Flask-JWT-Extended needs mapping
            if 'role' in payload:
                g.current_user_role = UserRole(payload['role'])
            else:
                # Map email to role for Flask-JWT-Extended tokens
                email = payload.get('sub', '')
                if email == 'admin@jewelry.com':
                    g.current_user_role = UserRole.ADMIN
                elif email == 'user@jewelry.com':
                    g.current_user_role = UserRole.MEMBER
                else:
                    g.current_user_role = UserRole.GUEST

            g.token_payload = payload
            
            return f(*args, **kwargs)
            
        except InvalidCredentialsError:
            return jsonify({
                'error': 'Invalid or expired token',
                'code': 'INVALID_TOKEN'
            }), 401
        except Exception as e:
            current_app.logger.error(f"Authentication error: {str(e)}")
            return jsonify({
                'error': 'Authentication failed',
                'code': 'AUTH_ERROR'
            }), 401
    
    return decorated_function


def role_required(required_roles: List[UserRole]) -> Callable:
    """Decorator to require specific roles"""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        @jwt_required
        def decorated_function(*args, **kwargs):
            try:
                current_role = g.current_user_role
                
                if current_role not in required_roles:
                    return jsonify({
                        'error': f'Requires one of: {[role.value for role in required_roles]}',
                        'code': 'INSUFFICIENT_PERMISSIONS'
                    }), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"Authorization error: {str(e)}")
                return jsonify({
                    'error': 'Authorization failed',
                    'code': 'AUTH_ERROR'
                }), 403
        
        return decorated_function
    return decorator


def admin_required(f: Callable) -> Callable:
    """Decorator to require admin role"""
    return role_required([UserRole.ADMIN])(f)


def staff_required(f: Callable) -> Callable:
    """Decorator to require staff role or higher"""
    return role_required([UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN])(f)


def manager_required(f: Callable) -> Callable:
    """Decorator to require manager role or higher"""
    return role_required([UserRole.MANAGER, UserRole.ADMIN])(f)


def member_required(f: Callable) -> Callable:
    """Decorator to require member role or higher"""
    return role_required([UserRole.MEMBER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN])(f)


def optional_auth(f: Callable) -> Callable:
    """Decorator for optional authentication (doesn't fail if no token)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            token = AuthService.extract_token_from_header(auth_header)
            
            if token:
                # Validate token if present
                payload = _decode_jwt_token(token)

                # Store user info in Flask's g object
                # Handle both custom JWT (user_id) and Flask-JWT-Extended (sub)
                user_id = payload.get('user_id') or payload.get('sub')

                # If user_id looks like an email, convert to actual user ID
                if user_id and '@' in str(user_id):
                    user_id = _get_user_id_from_email(user_id)

                g.current_user_id = user_id

                # Handle role - custom JWT has role field, Flask-JWT-Extended needs mapping
                if 'role' in payload:
                    g.current_user_role = UserRole(payload['role'])
                else:
                    # Map email to role for Flask-JWT-Extended tokens
                    email = payload.get('sub', '')
                    if email == 'admin@jewelry.com':
                        g.current_user_role = UserRole.ADMIN
                    elif email == 'user@jewelry.com':
                        g.current_user_role = UserRole.MEMBER
                    else:
                        g.current_user_role = UserRole.GUEST

                g.token_payload = payload
            else:
                # No token provided, set guest user
                g.current_user_id = None
                g.current_user_role = UserRole.GUEST
                g.token_payload = None
            
            return f(*args, **kwargs)
            
        except Exception as e:
            # If token validation fails, treat as guest
            current_app.logger.warning(f"Optional auth failed: {str(e)}")
            g.current_user_id = None
            g.current_user_role = UserRole.GUEST
            g.token_payload = None
            
            return f(*args, **kwargs)
    
    return decorated_function


def get_current_user() -> Optional[str]:
    """Get current user ID from Flask g object"""
    return getattr(g, 'current_user_id', None)


def get_current_user_role() -> UserRole:
    """Get current user role from Flask g object"""
    return getattr(g, 'current_user_role', UserRole.GUEST)


def is_authenticated() -> bool:
    """Check if current request is authenticated"""
    return get_current_user() is not None


def has_role(role: UserRole) -> bool:
    """Check if current user has specific role"""
    return get_current_user_role() == role


def has_any_role(roles: List[UserRole]) -> bool:
    """Check if current user has any of the specified roles"""
    return get_current_user_role() in roles


def is_admin() -> bool:
    """Check if current user is admin"""
    return has_role(UserRole.ADMIN)


def is_staff_or_above() -> bool:
    """Check if current user is staff or above"""
    return has_any_role([UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN])


def is_manager_or_above() -> bool:
    """Check if current user is manager or above"""
    return has_any_role([UserRole.MANAGER, UserRole.ADMIN])


def can_sell() -> bool:
    """Check if current user can sell items"""
    return has_any_role([UserRole.MEMBER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN])


def can_bid() -> bool:
    """Check if current user can place bids"""
    return has_any_role([UserRole.MEMBER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN])


def can_manage_auctions() -> bool:
    """Check if current user can manage auction sessions"""
    return has_any_role([UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN])


def can_approve_items() -> bool:
    """Check if current user can approve jewelry items"""
    return has_any_role([UserRole.MANAGER, UserRole.ADMIN])
