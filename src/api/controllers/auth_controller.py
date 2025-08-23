from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from flasgger import swag_from
import logging
from typing import Dict, Any

from src.domain.services.auth_service import IAuthService, AuthResult
from src.domain.models.user import UserRole
from src.api.middleware.auth_middleware import require_auth, get_current_user
from src.api.utils.response_helper import success_response, error_response, validation_error_response

logger = logging.getLogger(__name__)

# Create Blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

class AuthController:
    """Authentication controller for handling auth-related API endpoints"""

    def __init__(self, auth_service: IAuthService):
        self.auth_service = auth_service
        self._register_routes()

    def _register_routes(self):
        """Register all authentication routes"""
        auth_bp.add_url_rule('/register', 'register', self.register, methods=['POST'])
        auth_bp.add_url_rule('/verify-email', 'verify_email', self.verify_email, methods=['POST'])
        auth_bp.add_url_rule('/resend-verification', 'resend_verification', self.resend_verification, methods=['POST'])
        auth_bp.add_url_rule('/login', 'login', self.login, methods=['POST'])
        auth_bp.add_url_rule('/logout', 'logout', self.logout, methods=['POST'])
        auth_bp.add_url_rule('/forgot-password', 'forgot_password', self.forgot_password, methods=['POST'])
        auth_bp.add_url_rule('/reset-password', 'reset_password', self.reset_password, methods=['POST'])
        auth_bp.add_url_rule('/change-password', 'change_password', self.change_password, methods=['POST'])
        auth_bp.add_url_rule('/profile', 'get_profile', self.get_profile, methods=['GET'])
        auth_bp.add_url_rule('/profile', 'update_profile', self.update_profile, methods=['PUT'])
        auth_bp.add_url_rule('/validate-token', 'validate_token', self.validate_token, methods=['POST'])
        auth_bp.add_url_rule('/refresh-token', 'refresh_token', self.refresh_token, methods=['POST'])

    @cross_origin()
    def register(self):
        """
        Register new user
        ---
        tags:
          - Authentication
        summary: Register a new user account
        description: Create a new user account with email verification
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - email
                - password
                - first_name
                - last_name
              properties:
                email:
                  type: string
                  format: email
                  example: "user@example.com"
                password:
                  type: string
                  minLength: 6
                  example: "password123"
                first_name:
                  type: string
                  example: "Nguyễn"
                last_name:
                  type: string
                  example: "Văn A"
                phone:
                  type: string
                  example: "0901234567"
        responses:
          201:
            description: User registered successfully
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: "Đăng ký thành công! Vui lòng kiểm tra email để xác thực tài khoản."
                data:
                  type: object
                  properties:
                    user_id:
                      type: integer
                      example: 1
                    email:
                      type: string
                      example: "user@example.com"
          400:
            description: Validation error
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Email đã được sử dụng"
        """
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ['email', 'password', 'first_name', 'last_name']
            if not data or not all(field in data for field in required_fields):
                return validation_error_response("Thiếu thông tin bắt buộc: email, password, first_name, last_name")

            # Validate email format
            email = data['email'].strip().lower()
            if not self._is_valid_email(email):
                return validation_error_response("Email không hợp lệ")

            # Validate password strength
            password = data['password']
            if len(password) < 6:
                return validation_error_response("Mật khẩu phải có ít nhất 6 ký tự")

            # Get optional fields
            phone_number = data.get('phone_number', '').strip()
            role_str = data.get('role', 'buyer').lower()

            # Parse role
            try:
                role = UserRole(role_str)
            except ValueError:
                role = UserRole.BUYER

            # Register user
            result = self.auth_service.register(
                email=email,
                password=password,
                first_name=data['first_name'].strip(),
                last_name=data['last_name'].strip(),
                phone_number=phone_number,
                role=role
            )

            if result.success:
                return success_response(
                    message=result.message,
                    data={
                        "user": {
                            "id": result.user.id,
                            "email": result.user.email,
                            "full_name": result.user.full_name,
                            "role": result.user.role.value,
                            "status": result.user.status.value,
                            "is_email_verified": result.user.is_email_verified
                        },
                        "requires_verification": result.data.get("requires_verification", False)
                    }
                )
            else:
                return error_response(result.message, 400)

        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return error_response("Lỗi hệ thống khi đăng ký", 500)

    @cross_origin()
    def verify_email(self):
        """Verify email with verification code"""
        try:
            data = request.get_json()
            logger.info(f"Verify email request data: {data}")

            # Validate required fields
            if not data or 'email' not in data or 'code' not in data:
                logger.error(f"Missing required fields. Data: {data}")
                return validation_error_response("Thiếu email hoặc mã xác thực")

            email = data['email'].strip().lower()
            code = data['code'].strip()
            logger.info(f"Processing verification for email: {email}, code: {code}")

            # Validate code format (6 digits)
            if not code.isdigit() or len(code) != 6:
                logger.error(f"Invalid code format: {code}")
                return validation_error_response("Mã xác thực phải là 6 chữ số")

            # Verify email
            result = self.auth_service.verify_email(email, code)

            if result.success:
                return success_response(
                    message=result.message,
                    data={
                        "user": {
                            "id": result.user.id,
                            "email": result.user.email,
                            "full_name": result.user.full_name,
                            "role": result.user.role.value,
                            "status": result.user.status.value,
                            "is_email_verified": result.user.is_email_verified
                        },
                        "token": result.token,
                        "verified": result.data.get("verified", False)
                    }
                )
            else:
                return error_response(result.message, 400)

        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return error_response("Lỗi hệ thống khi xác thực email", 500)

    @cross_origin()
    def resend_verification(self):
        """Resend verification code"""
        try:
            data = request.get_json()

            if not data or 'email' not in data:
                return validation_error_response("Thiếu email")

            email = data['email'].strip().lower()

            # Resend verification code
            result = self.auth_service.resend_verification_code(email)

            if result.success:
                return success_response(result.message)
            else:
                return error_response(result.message, 400)

        except Exception as e:
            logger.error(f"Resend verification error: {str(e)}")
            return error_response("Lỗi hệ thống khi gửi lại mã xác thực", 500)

    @cross_origin()
    def login(self):
        """
        User login
        ---
        tags:
          - Authentication
        summary: Login user
        description: Authenticate user with email and password
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
                  example: "user@example.com"
                password:
                  type: string
                  example: "password123"
        responses:
          200:
            description: Login successful
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: true
                message:
                  type: string
                  example: "Đăng nhập thành công"
                data:
                  type: object
                  properties:
                    user:
                      type: object
                      properties:
                        id:
                          type: integer
                          example: 1
                        email:
                          type: string
                          example: "user@example.com"
                        full_name:
                          type: string
                          example: "Nguyễn Văn A"
                        role:
                          type: string
                          example: "USER"
                    token:
                      type: string
                      example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
          400:
            description: Invalid credentials
            schema:
              type: object
              properties:
                success:
                  type: boolean
                  example: false
                message:
                  type: string
                  example: "Email hoặc mật khẩu không đúng"
        """
        try:
            data = request.get_json()

            # Validate required fields
            if not data or 'email' not in data or 'password' not in data:
                return validation_error_response("Thiếu email hoặc mật khẩu")

            email = data['email'].strip().lower()
            password = data['password']

            # Login user
            result = self.auth_service.login(email, password)

            if result.success:
                return success_response(
                    message=result.message,
                    data={
                        "user": {
                            "id": result.user.id,
                            "email": result.user.email,
                            "full_name": result.user.full_name,
                            "role": result.user.role.value,
                            "status": result.user.status.value,
                            "is_email_verified": result.user.is_email_verified
                        },
                        "token": result.token,
                        "login_time": result.data.get("login_time")
                    }
                )
            else:
                status_code = 401 if "mật khẩu" in result.message.lower() else 400
                response_data = {"message": result.message}

                # Add verification info if needed
                if result.data.get("requires_verification"):
                    response_data["requires_verification"] = True
                    response_data["email"] = result.data.get("email")

                return error_response(response_data, status_code)

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return error_response("Lỗi hệ thống khi đăng nhập", 500)

    @cross_origin()
    @require_auth
    def logout(self):
        """Logout user"""
        try:
            # Get token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return error_response("Token không hợp lệ", 401)

            token = auth_header.split(' ')[1]

            # Logout user
            result = self.auth_service.logout(token)

            if result.success:
                return success_response(result.message)
            else:
                return error_response(result.message, 400)

        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return error_response("Lỗi hệ thống khi đăng xuất", 500)

    @cross_origin()
    def forgot_password(self):
        """Send password reset code"""
        try:
            data = request.get_json()

            if not data or 'email' not in data:
                return validation_error_response("Thiếu email")

            email = data['email'].strip().lower()

            # Send password reset code
            result = self.auth_service.forgot_password(email)

            if result.success:
                return success_response(result.message)
            else:
                return error_response(result.message, 400)

        except Exception as e:
            logger.error(f"Forgot password error: {str(e)}")
            return error_response("Lỗi hệ thống khi đặt lại mật khẩu", 500)

    @cross_origin()
    def reset_password(self):
        """Reset password with verification code"""
        try:
            data = request.get_json()

            # Validate required fields
            required_fields = ['email', 'code', 'new_password']
            if not data or not all(field in data for field in required_fields):
                return validation_error_response("Thiếu thông tin bắt buộc: email, code, new_password")

            email = data['email'].strip().lower()
            code = data['code'].strip()
            new_password = data['new_password']

            # Validate code format
            if not code.isdigit() or len(code) != 6:
                return validation_error_response("Mã xác thực phải là 6 chữ số")

            # Validate new password
            if len(new_password) < 6:
                return validation_error_response("Mật khẩu mới phải có ít nhất 6 ký tự")

            # Reset password
            result = self.auth_service.reset_password(email, code, new_password)

            if result.success:
                return success_response(result.message)
            else:
                return error_response(result.message, 400)

        except Exception as e:
            logger.error(f"Reset password error: {str(e)}")
            return error_response("Lỗi hệ thống khi đặt lại mật khẩu", 500)

    @cross_origin()
    @require_auth
    def change_password(self):
        """Change password for authenticated user"""
        try:
            data = request.get_json()
            current_user = get_current_user()

            # Validate required fields
            if not data or 'old_password' not in data or 'new_password' not in data:
                return validation_error_response("Thiếu mật khẩu cũ hoặc mật khẩu mới")

            old_password = data['old_password']
            new_password = data['new_password']

            # Validate new password
            if len(new_password) < 6:
                return validation_error_response("Mật khẩu mới phải có ít nhất 6 ký tự")

            # Change password
            result = self.auth_service.change_password(current_user.id, old_password, new_password)

            if result.success:
                return success_response(result.message)
            else:
                return error_response(result.message, 400)

        except Exception as e:
            logger.error(f"Change password error: {str(e)}")
            return error_response("Lỗi hệ thống khi đổi mật khẩu", 500)

    @cross_origin()
    @require_auth
    def get_profile(self):
        """Get user profile"""
        try:
            current_user = get_current_user()

            # Get user profile
            result = self.auth_service.get_user_profile(current_user.id)

            if result.success:
                return success_response(
                    message="Lấy thông tin tài khoản thành công",
                    data={
                        "user": {
                            "id": result.user.id,
                            "email": result.user.email,
                            "first_name": result.user.first_name,
                            "last_name": result.user.last_name,
                            "full_name": result.user.full_name,
                            "phone_number": result.user.phone_number,
                            "role": result.user.role.value,
                            "status": result.user.status.value,
                            "bio": result.user.bio,
                            "image_url": result.user.image_url,
                            "address": result.user.address,
                            "is_email_verified": result.user.is_email_verified,
                            "created_at": result.user.created_at.isoformat() if result.user.created_at else None
                        }
                    }
                )
            else:
                return error_response(result.message, 404)

        except Exception as e:
            logger.error(f"Get profile error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy thông tin tài khoản", 500)

    @cross_origin()
    @require_auth
    def update_profile(self):
        """Update user profile"""
        try:
            data = request.get_json()
            current_user = get_current_user()

            if not data:
                return validation_error_response("Không có dữ liệu để cập nhật")

            # Filter allowed fields
            allowed_fields = ['first_name', 'last_name', 'phone_number', 'bio', 'image_url', 'address']
            update_data = {k: v for k, v in data.items() if k in allowed_fields}

            if not update_data:
                return validation_error_response("Không có trường hợp lệ để cập nhật")

            # Update profile
            result = self.auth_service.update_user_profile(current_user.id, **update_data)

            if result.success:
                return success_response(
                    message=result.message,
                    data={
                        "user": {
                            "id": result.user.id,
                            "email": result.user.email,
                            "first_name": result.user.first_name,
                            "last_name": result.user.last_name,
                            "full_name": result.user.full_name,
                            "phone_number": result.user.phone_number,
                            "role": result.user.role.value,
                            "status": result.user.status.value,
                            "bio": result.user.bio,
                            "image_url": result.user.image_url,
                            "address": result.user.address,
                            "is_email_verified": result.user.is_email_verified
                        }
                    }
                )
            else:
                return error_response(result.message, 400)

        except Exception as e:
            logger.error(f"Update profile error: {str(e)}")
            return error_response("Lỗi hệ thống khi cập nhật thông tin", 500)

    @cross_origin()
    def validate_token(self):
        """Validate JWT token"""
        try:
            data = request.get_json()

            if not data or 'token' not in data:
                return validation_error_response("Thiếu token")

            token = data['token']

            # Validate token
            result = self.auth_service.validate_token(token)

            if result.success:
                return success_response(
                    message=result.message,
                    data={
                        "valid": True,
                        "user": {
                            "id": result.user.id,
                            "email": result.user.email,
                            "full_name": result.user.full_name,
                            "role": result.user.role.value,
                            "status": result.user.status.value
                        }
                    }
                )
            else:
                return error_response(result.message, 401)

        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return error_response("Lỗi hệ thống khi xác thực token", 500)

    @cross_origin()
    def refresh_token(self):
        """Refresh JWT token"""
        try:
            data = request.get_json()

            if not data or 'refresh_token' not in data:
                return validation_error_response("Thiếu refresh token")

            refresh_token = data['refresh_token']

            # Refresh token
            result = self.auth_service.refresh_token(refresh_token)

            if result.success:
                return success_response(
                    message=result.message,
                    data={
                        "token": result.token,
                        "user": {
                            "id": result.user.id,
                            "email": result.user.email,
                            "full_name": result.user.full_name,
                            "role": result.user.role.value
                        }
                    }
                )
            else:
                return error_response(result.message, 401)

        except Exception as e:
            logger.error(f"Refresh token error: {str(e)}")
            return error_response("Lỗi hệ thống khi làm mới token", 500)

    def _is_valid_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None