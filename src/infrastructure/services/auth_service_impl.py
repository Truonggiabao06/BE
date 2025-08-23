import hashlib
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from src.domain.services.auth_service import IAuthService, AuthResult
from src.domain.services.email_service import IEmailService
from src.domain.models.user import User, UserRole, UserStatus
from src.domain.models.verification_code import VerificationCode, VerificationCodeType
from src.domain.repositories.user_repo import IUserRepository
from src.domain.repositories.verification_code_repo import IVerificationCodeRepository

logger = logging.getLogger(__name__)

class AuthService(IAuthService):
    """Authentication service implementation"""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        verification_code_repository: IVerificationCodeRepository,
        email_service: IEmailService,
        jwt_secret: str = "your-secret-key",
        jwt_expiry_hours: int = 24
    ):
        self.user_repo = user_repository
        self.verification_repo = verification_code_repository
        self.email_service = email_service
        self.jwt_secret = jwt_secret
        self.jwt_expiry_hours = jwt_expiry_hours
    
    def register(self, email: str, password: str, first_name: str, last_name: str, phone_number: str = "", role: UserRole = UserRole.BUYER) -> AuthResult:
        """Register new user and send verification code"""
        try:
            # Check if user already exists
            existing_user = self.user_repo.get_by_username(email)
            if existing_user:
                if existing_user.is_email_verified:
                    return AuthResult(False, "Email đã được đăng ký và xác thực")
                else:
                    # User exists but not verified, resend verification code
                    return self.resend_verification_code(email)
            
            # Create new user
            password_hash = self._hash_password(password)
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                password_hash=password_hash,
                role=role,
                status=UserStatus.PENDING_VERIFICATION,
                is_email_verified=False
            )
            
            # Save user to database
            created_user = self.user_repo.create(new_user)
            
            # Generate and send verification code
            verification_result = self._send_verification_code(created_user.id, email, first_name)
            
            if verification_result:
                return AuthResult(
                    True, 
                    "Đăng ký thành công! Vui lòng kiểm tra email để xác thực tài khoản.",
                    created_user,
                    data={"requires_verification": True}
                )
            else:
                return AuthResult(False, "Đăng ký thành công nhưng không thể gửi email xác thực. Vui lòng thử lại.")
                
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return AuthResult(False, f"Lỗi đăng ký: {str(e)}")
    
    def verify_email(self, email: str, code: str) -> AuthResult:
        """Verify email with verification code"""
        try:
            # Get user
            user = self.user_repo.get_by_username(email)
            if not user:
                return AuthResult(False, "Không tìm thấy tài khoản với email này")
            
            if user.is_email_verified:
                return AuthResult(False, "Tài khoản đã được xác thực")
            
            # Get verification code
            verification_code = self.verification_repo.get_by_email_and_code(
                email, code, VerificationCodeType.EMAIL_VERIFICATION
            )
            
            if not verification_code:
                return AuthResult(False, "Mã xác thực không hợp lệ")
            
            # Verify code
            if verification_code.verify(code):
                # Activate user account
                user.activate_account()
                updated_user = self.user_repo.update(user)
                
                # Update verification code
                self.verification_repo.update(verification_code)
                
                # Send welcome email
                self.email_service.send_welcome_email(updated_user)
                
                # Generate JWT token
                token = self._generate_jwt_token(updated_user)
                
                return AuthResult(
                    True,
                    "Xác thực email thành công! Chào mừng bạn đến với hệ thống đấu giá.",
                    updated_user,
                    token,
                    {"verified": True}
                )
            else:
                # Update verification code with failed attempt
                self.verification_repo.update(verification_code)
                
                remaining_attempts = verification_code.remaining_attempts
                if remaining_attempts > 0:
                    return AuthResult(False, f"Mã xác thực không đúng. Còn {remaining_attempts} lần thử.")
                else:
                    return AuthResult(False, "Mã xác thực đã hết hạn hoặc đã sử dụng hết số lần thử. Vui lòng yêu cầu mã mới.")
                    
        except Exception as e:
            logger.error(f"Email verification error: {str(e)}")
            return AuthResult(False, f"Lỗi xác thực: {str(e)}")
    
    def resend_verification_code(self, email: str) -> AuthResult:
        """Resend verification code to email"""
        try:
            # Get user
            user = self.user_repo.get_by_username(email)
            if not user:
                return AuthResult(False, "Không tìm thấy tài khoản với email này")
            
            if user.is_email_verified:
                return AuthResult(False, "Tài khoản đã được xác thực")
            
            # Expire old codes
            self.verification_repo.expire_old_codes(email, VerificationCodeType.EMAIL_VERIFICATION)
            
            # Send new verification code
            verification_result = self._send_verification_code(user.id, email, user.first_name)
            
            if verification_result:
                return AuthResult(True, "Mã xác thực mới đã được gửi đến email của bạn.")
            else:
                return AuthResult(False, "Không thể gửi mã xác thực. Vui lòng thử lại sau.")
                
        except Exception as e:
            logger.error(f"Resend verification code error: {str(e)}")
            return AuthResult(False, f"Lỗi gửi mã xác thực: {str(e)}")
    
    def login(self, email: str, password: str) -> AuthResult:
        """Login user with email and password"""
        try:
            # Get user
            user = self.user_repo.get_by_username(email)
            if not user:
                return AuthResult(False, "Email hoặc mật khẩu không đúng")
            
            # Check password
            if not self._verify_password(password, user.password_hash):
                return AuthResult(False, "Email hoặc mật khẩu không đúng")
            
            # Check if email is verified
            if not user.is_email_verified:
                return AuthResult(
                    False, 
                    "Tài khoản chưa được xác thực. Vui lòng kiểm tra email để xác thực.",
                    data={"requires_verification": True, "email": email}
                )
            
            # Check if account is active
            if not user.is_active:
                return AuthResult(False, f"Tài khoản đang ở trạng thái: {user.status.value}")
            
            # Generate JWT token
            token = self._generate_jwt_token(user)
            
            return AuthResult(
                True,
                "Đăng nhập thành công!",
                user,
                token,
                {"login_time": datetime.utcnow().isoformat()}
            )
            
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return AuthResult(False, f"Lỗi đăng nhập: {str(e)}")
    
    def logout(self, token: str) -> AuthResult:
        """Logout user and invalidate token"""
        try:
            # In a real implementation, you would add the token to a blacklist
            # For now, we just return success
            return AuthResult(True, "Đăng xuất thành công!")
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return AuthResult(False, f"Lỗi đăng xuất: {str(e)}")
    
    def forgot_password(self, email: str) -> AuthResult:
        """Send password reset code to email"""
        try:
            # Get user
            user = self.user_repo.get_by_username(email)
            if not user:
                # Don't reveal if email exists or not for security
                return AuthResult(True, "Nếu email tồn tại, mã đặt lại mật khẩu đã được gửi.")
            
            # Expire old password reset codes
            self.verification_repo.expire_old_codes(email, VerificationCodeType.PASSWORD_RESET)
            
            # Generate and send password reset code
            verification_code = VerificationCode.generate_verification_code(
                user.id, email, VerificationCodeType.PASSWORD_RESET, expiry_minutes=10
            )
            
            created_code = self.verification_repo.create(verification_code)
            
            # Send email
            email_sent = self.email_service.send_password_reset_code(
                email, created_code.code, user.first_name
            )
            
            if email_sent:
                return AuthResult(True, "Mã đặt lại mật khẩu đã được gửi đến email của bạn.")
            else:
                return AuthResult(False, "Không thể gửi email. Vui lòng thử lại sau.")
                
        except Exception as e:
            logger.error(f"Forgot password error: {str(e)}")
            return AuthResult(False, f"Lỗi đặt lại mật khẩu: {str(e)}")
    
    def reset_password(self, email: str, code: str, new_password: str) -> AuthResult:
        """Reset password with verification code"""
        try:
            # Get user
            user = self.user_repo.get_by_username(email)
            if not user:
                return AuthResult(False, "Không tìm thấy tài khoản với email này")
            
            # Get verification code
            verification_code = self.verification_repo.get_by_email_and_code(
                email, code, VerificationCodeType.PASSWORD_RESET
            )
            
            if not verification_code:
                return AuthResult(False, "Mã xác thực không hợp lệ")
            
            # Verify code
            if verification_code.verify(code):
                # Update password
                user.password_hash = self._hash_password(new_password)
                updated_user = self.user_repo.update(user)
                
                # Update verification code
                self.verification_repo.update(verification_code)
                
                return AuthResult(True, "Đặt lại mật khẩu thành công! Vui lòng đăng nhập với mật khẩu mới.")
            else:
                # Update verification code with failed attempt
                self.verification_repo.update(verification_code)
                
                remaining_attempts = verification_code.remaining_attempts
                if remaining_attempts > 0:
                    return AuthResult(False, f"Mã xác thực không đúng. Còn {remaining_attempts} lần thử.")
                else:
                    return AuthResult(False, "Mã xác thực đã hết hạn hoặc đã sử dụng hết số lần thử. Vui lòng yêu cầu mã mới.")
                    
        except Exception as e:
            logger.error(f"Reset password error: {str(e)}")
            return AuthResult(False, f"Lỗi đặt lại mật khẩu: {str(e)}")
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> AuthResult:
        """Change password for authenticated user"""
        try:
            # Get user
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return AuthResult(False, "Không tìm thấy tài khoản")
            
            # Verify old password
            if not self._verify_password(old_password, user.password_hash):
                return AuthResult(False, "Mật khẩu cũ không đúng")
            
            # Update password
            user.password_hash = self._hash_password(new_password)
            updated_user = self.user_repo.update(user)
            
            return AuthResult(True, "Đổi mật khẩu thành công!")
            
        except Exception as e:
            logger.error(f"Change password error: {str(e)}")
            return AuthResult(False, f"Lỗi đổi mật khẩu: {str(e)}")
    
    def validate_token(self, token: str) -> AuthResult:
        """Validate JWT token and return user"""
        try:
            # Decode JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return AuthResult(False, "Token không hợp lệ")
            
            # Get user
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return AuthResult(False, "Không tìm thấy tài khoản")
            
            if not user.is_active:
                return AuthResult(False, "Tài khoản không hoạt động")
            
            return AuthResult(True, "Token hợp lệ", user, token)
            
        except jwt.ExpiredSignatureError:
            return AuthResult(False, "Token đã hết hạn")
        except jwt.InvalidTokenError:
            return AuthResult(False, "Token không hợp lệ")
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return AuthResult(False, f"Lỗi xác thực token: {str(e)}")
    
    def refresh_token(self, refresh_token: str) -> AuthResult:
        """Refresh JWT token"""
        # For now, just validate and generate new token
        validation_result = self.validate_token(refresh_token)
        if validation_result.success and validation_result.user:
            new_token = self._generate_jwt_token(validation_result.user)
            return AuthResult(True, "Token đã được làm mới", validation_result.user, new_token)
        return validation_result
    
    def get_user_profile(self, user_id: int) -> AuthResult:
        """Get user profile by ID"""
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return AuthResult(False, "Không tìm thấy tài khoản")
            
            return AuthResult(True, "Lấy thông tin tài khoản thành công", user)
            
        except Exception as e:
            logger.error(f"Get user profile error: {str(e)}")
            return AuthResult(False, f"Lỗi lấy thông tin tài khoản: {str(e)}")
    
    def update_user_profile(self, user_id: int, **kwargs) -> AuthResult:
        """Update user profile"""
        try:
            user = self.user_repo.get_by_id(user_id)
            if not user:
                return AuthResult(False, "Không tìm thấy tài khoản")
            
            user.update_profile(**kwargs)
            updated_user = self.user_repo.update(user)
            
            return AuthResult(True, "Cập nhật thông tin thành công", updated_user)
            
        except Exception as e:
            logger.error(f"Update user profile error: {str(e)}")
            return AuthResult(False, f"Lỗi cập nhật thông tin: {str(e)}")
    
    def _send_verification_code(self, user_id: int, email: str, user_name: str) -> bool:
        """Generate and send verification code"""
        try:
            # Generate verification code
            verification_code = VerificationCode.generate_verification_code(
                user_id, email, VerificationCodeType.EMAIL_VERIFICATION, expiry_minutes=10
            )
            
            # Save to database
            created_code = self.verification_repo.create(verification_code)
            
            # Send email
            return self.email_service.send_verification_code(email, created_code.code, user_name)
            
        except Exception as e:
            logger.error(f"Send verification code error: {str(e)}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == password_hash
    
    def _generate_jwt_token(self, user: User) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(hours=self.jwt_expiry_hours),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.jwt_secret, algorithm='HS256')
