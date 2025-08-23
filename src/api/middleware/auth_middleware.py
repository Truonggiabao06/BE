import jwt
import logging
from functools import wraps
from flask import request, g, current_app
from typing import Optional, List

from src.domain.models.user import User, UserRole
from src.api.utils.response_helper import unauthorized_response, forbidden_response

logger = logging.getLogger(__name__)

def get_token_from_header() -> Optional[str]:
    """Extract JWT token from Authorization header"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    # Expected format: "Bearer <token>"
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    return parts[1]

def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode JWT token and return payload"""
    try:
        # Get secret key from app config
        secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error decoding JWT token: {str(e)}")
        return None

def get_user_from_token(token: str) -> Optional[User]:
    """Get user object from JWT token"""
    payload = decode_jwt_token(token)
    if not payload:
        return None
    
    user_id = payload.get('user_id')
    if not user_id:
        return None
    
    try:
        # Import here to avoid circular imports
        from src.infrastructure.repositories.user_repository_impl import UserRepository
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.config import Config
        
        engine = create_engine(Config.DATABASE_URI)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        user_repo = UserRepository(session)
        user = user_repo.get_by_id(user_id)
        session.close()
        
        return user
    except Exception as e:
        logger.error(f"Error getting user from token: {str(e)}")
        return None

def require_auth(f):
    """Decorator to require authentication for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        if not token:
            return unauthorized_response("Token không được cung cấp")
        
        user = get_user_from_token(token)
        if not user:
            return unauthorized_response("Token không hợp lệ hoặc đã hết hạn")
        
        if not user.is_active:
            return unauthorized_response("Tài khoản không hoạt động")
        
        # Store user in Flask's g object for use in the route
        g.current_user = user
        g.current_token = token
        
        return f(*args, **kwargs)
    
    return decorated_function

def require_roles(allowed_roles: List[UserRole]):
    """Decorator to require specific roles for a route"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()
            
            if current_user.role not in allowed_roles:
                return forbidden_response("Bạn không có quyền truy cập chức năng này")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_seller(f):
    """Decorator to require seller role"""
    return require_roles([UserRole.SELLER, UserRole.ADMIN])(f)

def require_buyer(f):
    """Decorator to require buyer role"""
    return require_roles([UserRole.BUYER, UserRole.ADMIN])(f)

def require_admin(f):
    """Decorator to require admin role"""
    return require_roles([UserRole.ADMIN])(f)

def require_staff(f):
    """Decorator to require staff role (staff, manager, or admin)"""
    return require_roles([UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN])(f)

def require_manager(f):
    """Decorator to require manager role (manager or admin)"""
    return require_roles([UserRole.MANAGER, UserRole.ADMIN])(f)

def require_email_verified(f):
    """Decorator to require email verification"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        
        if not current_user.is_email_verified:
            return unauthorized_response("Vui lòng xác thực email trước khi sử dụng chức năng này")
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user() -> Optional[User]:
    """Get current authenticated user from Flask's g object"""
    return getattr(g, 'current_user', None)

def get_current_token() -> Optional[str]:
    """Get current JWT token from Flask's g object"""
    return getattr(g, 'current_token', None)

def optional_auth(f):
    """Decorator for optional authentication (user can be None)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_header()
        user = None
        
        if token:
            user = get_user_from_token(token)
            if user and user.is_active:
                g.current_user = user
                g.current_token = token
        
        return f(*args, **kwargs)
    
    return decorated_function

class AuthMiddleware:
    """Authentication middleware class for more complex scenarios"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with Flask app"""
        app.before_request(self.before_request)
    
    def before_request(self):
        """Process request before it reaches the route handler"""
        # Skip auth for certain routes
        exempt_routes = [
            '/api/auth/register',
            '/api/auth/login',
            '/api/auth/verify-email',
            '/api/auth/resend-verification',
            '/api/auth/forgot-password',
            '/api/auth/reset-password',
            '/api/auth/validate-token',
            '/api/auth/refresh-token',
            '/health',
            '/docs',
            '/swagger'
        ]
        
        if request.endpoint and any(route in request.path for route in exempt_routes):
            return
        
        # For other routes, you can add global auth logic here if needed
        pass
