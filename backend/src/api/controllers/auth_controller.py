"""
Authentication API controller for the Jewelry Auction System
"""
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError as MarshmallowValidationError
from api.middleware.auth_middleware import jwt_required, get_current_user
from services.auth_service import AuthenticationService
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.databases.mssql import get_db_session, db
from domain.exceptions import InvalidCredentialsError, AccountDeactivatedError
from domain.enums import UserRole
from domain.exceptions import (
    InvalidCredentialsError,
    AccountDeactivatedError,
    DuplicateEmailError,
    ValidationError,
    NotFoundError
)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

def get_auth_service():
    """Get authentication service instance"""
    session = get_db_session()
    user_repository = UserRepository(session)
    return AuthenticationService(user_repository)


@auth_bp.route('/decode-token', methods=['POST'])
def decode_token():
    """Decode token for debugging"""
    try:
        data = request.get_json()
        token = data.get('token', '')

        if not token:
            return jsonify({'error': 'Token required'}), 400

        import jwt
        from flask import current_app

        # Try different secret keys
        secret_keys = [
            current_app.config.get('JWT_SECRET_KEY'),
            current_app.config.get('SECRET_KEY'),
            'your-secret-key-change-in-production',
            'jwt-secret-key-change-in-production'
        ]

        results = []
        for i, secret in enumerate(secret_keys):
            if secret:
                try:
                    payload = jwt.decode(token, secret, algorithms=['HS256'])
                    results.append({
                        'secret_index': i,
                        'secret_preview': secret[:10] + '...' if len(secret) > 10 else secret,
                        'success': True,
                        'payload': payload
                    })
                except Exception as e:
                    results.append({
                        'secret_index': i,
                        'secret_preview': secret[:10] + '...' if len(secret) > 10 else secret,
                        'success': False,
                        'error': str(e)
                    })

        return jsonify({
            'results': results,
            'config_jwt_secret': current_app.config.get('JWT_SECRET_KEY'),
            'config_secret_key': current_app.config.get('SECRET_KEY')
        })

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@auth_bp.route('/auth', methods=['POST'])
def auth():
    """Authentication endpoint"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    from infrastructure.models import UserModel
    from infrastructure.services.auth_service import AuthService
    from flask_jwt_extended import create_access_token, create_refresh_token

    user = UserModel.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    if not AuthService.verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account deactivated'}), 403

    # Create tokens
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'user_id': user.id,
            'role': user.role.value,
            'type': 'access'
        }
    )
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'data': {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role.value
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    }), 200


@auth_bp.route('/simple-login', methods=['POST'])
def simple_login():
    """Simple login endpoint for testing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data'}), 400

        email = data.get('email', '').strip()
        password = data.get('password', '')

        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400

        from infrastructure.models import UserModel
        from infrastructure.services.auth_service import AuthService
        from flask_jwt_extended import create_access_token, create_refresh_token

        user = UserModel.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 401

        if not AuthService.verify_password(password, user.password_hash):
            return jsonify({'error': 'Invalid password'}), 401

        if not user.is_active:
            return jsonify({'error': 'Account deactivated'}), 403

        # Create tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'user_id': user.id,
                'role': user.role.value,
                'type': 'access'
            }
        )
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role.value
                },
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@auth_bp.route('/test-password', methods=['POST'])
def test_password():
    """Test password verification"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')

        from infrastructure.models import UserModel
        from infrastructure.services.auth_service import AuthService

        user = UserModel.query.filter_by(email=email).first()

        if user:
            is_valid = AuthService.verify_password(password, user.password_hash)
            return jsonify({
                'user_found': True,
                'user_email': user.email,
                'password_valid': is_valid,
                'password_hash_preview': user.password_hash[:20] + '...'
            })
        else:
            return jsonify({'user_found': False})

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@auth_bp.route('/debug-login', methods=['POST'])
def debug_login():
    """Debug login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email', '')
        password = data.get('password', '')

        # Test direct user lookup
        from infrastructure.models import UserModel
        user = UserModel.query.filter_by(email=email).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Test password verification
        from infrastructure.services.auth_service import AuthService
        is_valid = AuthService.verify_password(password, user.password_hash)

        if is_valid:
            # Test auth service
            auth_service = get_auth_service()
            result = auth_service.login(email, password)

            return jsonify({
                'user_found': True,
                'password_valid': is_valid,
                'user_email': user.email,
                'user_role': user.role.value,
                'auth_service_success': True,
                'token': result['access_token'][:50] + '...'
            })
        else:
            return jsonify({
                'user_found': True,
                'password_valid': is_valid,
                'user_email': user.email,
                'user_role': user.role.value,
                'auth_service_success': False
            })

    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - password
          properties:
            name:
              type: string
              example: "John Doe"
            email:
              type: string
              format: email
              example: "john@example.com"
            password:
              type: string
              minLength: 8
              example: "SecurePass123!"
            role:
              type: string
              enum: [MEMBER, STAFF, MANAGER, ADMIN]
              default: MEMBER
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                user:
                  type: object
                access_token:
                  type: string
                refresh_token:
                  type: string
      400:
        description: Validation error
      409:
        description: Email already exists
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required',
                'code': 'MISSING_BODY'
            }), 400

        # Extract and validate required fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role_str = data.get('role', 'MEMBER').upper()

        if not all([name, email, password]):
            return jsonify({
                'success': False,
                'error': 'Name, email, and password are required',
                'code': 'MISSING_FIELDS'
            }), 400

        # Parse role
        try:
            role = UserRole(role_str)
        except ValueError:
            role = UserRole.MEMBER

        # Register user
        auth_service = get_auth_service()
        result = auth_service.register_user(name, email, password, role)

        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': result
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except DuplicateEmailError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'DUPLICATE_EMAIL'
        }), 409
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Registration failed',
            'code': 'REGISTRATION_ERROR'
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: "admin@example.com"
            password:
              type: string
              example: "Admin@123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                user:
                  type: object
                access_token:
                  type: string
                refresh_token:
                  type: string
      401:
        description: Invalid credentials
      403:
        description: Account deactivated
    """
    # Use same logic as /auth endpoint which works
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data'}), 400

    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    from infrastructure.models import UserModel
    from infrastructure.services.auth_service import AuthService
    from flask_jwt_extended import create_access_token, create_refresh_token

    user = UserModel.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    if not AuthService.verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401

    if not user.is_active:
        return jsonify({'error': 'Account deactivated'}), 403

    # Create tokens
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'user_id': user.id,
            'role': user.role.value,
            'type': 'access'
        }
    )
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'success': True,
        'message': 'Login successful',
        'data': {
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role.value
            },
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    }), 200