from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from src.domain.models.user import User

class IEmailService(ABC):
    """Interface for email service"""
    
    @abstractmethod
    def send_verification_code(self, email: str, code: str, user_name: str = "") -> bool:
        """Send email verification code"""
        pass
    
    @abstractmethod
    def send_password_reset_code(self, email: str, code: str, user_name: str = "") -> bool:
        """Send password reset code"""
        pass
    
    @abstractmethod
    def send_welcome_email(self, user: User) -> bool:
        """Send welcome email after successful verification"""
        pass
    
    @abstractmethod
    def send_auction_notification(self, email: str, subject: str, message: str) -> bool:
        """Send auction-related notifications"""
        pass
    
    @abstractmethod
    def send_payment_confirmation(self, email: str, payment_details: Dict[str, Any]) -> bool:
        """Send payment confirmation email"""
        pass

class EmailTemplate:
    """Email template helper class"""
    
    @staticmethod
    def verification_code_template(code: str, user_name: str = "") -> Dict[str, str]:
        """Template for email verification code"""
        greeting = f"Xin chào {user_name}," if user_name else "Xin chào,"
        
        return {
            "subject": "Mã xác thực tài khoản - Hệ thống đấu giá trang sức",
            "html_body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2c3e50;">🏺 Hệ thống đấu giá trang sức</h1>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                        <h2 style="color: #2c3e50; margin-top: 0;">Xác thực tài khoản</h2>
                        <p>{greeting}</p>
                        <p>Cảm ơn bạn đã đăng ký tài khoản tại hệ thống đấu giá trang sức của chúng tôi.</p>
                        <p>Vui lòng sử dụng mã xác thực bên dưới để hoàn tất quá trình đăng ký:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <div style="background: #3498db; color: white; font-size: 32px; font-weight: bold; 
                                        padding: 15px 30px; border-radius: 8px; display: inline-block; 
                                        letter-spacing: 5px;">{code}</div>
                        </div>
                        
                        <p><strong>Lưu ý quan trọng:</strong></p>
                        <ul>
                            <li>Mã xác thực có hiệu lực trong <strong>10 phút</strong></li>
                            <li>Bạn có tối đa <strong>3 lần</strong> nhập mã</li>
                            <li>Không chia sẻ mã này với bất kỳ ai</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; color: #7f8c8d; font-size: 14px;">
                        <p>Nếu bạn không đăng ký tài khoản này, vui lòng bỏ qua email này.</p>
                        <p>© 2024 Hệ thống đấu giá trang sức. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "text_body": f"""
            Hệ thống đấu giá trang sức
            
            {greeting}
            
            Cảm ơn bạn đã đăng ký tài khoản tại hệ thống đấu giá trang sức của chúng tôi.
            
            Mã xác thực của bạn là: {code}
            
            Lưu ý:
            - Mã có hiệu lực trong 10 phút
            - Bạn có tối đa 3 lần nhập mã
            - Không chia sẻ mã này với bất kỳ ai
            
            Nếu bạn không đăng ký tài khoản này, vui lòng bỏ qua email này.
            """
        }
    
    @staticmethod
    def password_reset_template(code: str, user_name: str = "") -> Dict[str, str]:
        """Template for password reset code"""
        greeting = f"Xin chào {user_name}," if user_name else "Xin chào,"
        
        return {
            "subject": "Mã đặt lại mật khẩu - Hệ thống đấu giá trang sức",
            "html_body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2c3e50;">🏺 Hệ thống đấu giá trang sức</h1>
                    </div>
                    
                    <div style="background: #fff3cd; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ffc107;">
                        <h2 style="color: #856404; margin-top: 0;">Đặt lại mật khẩu</h2>
                        <p>{greeting}</p>
                        <p>Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.</p>
                        <p>Vui lòng sử dụng mã xác thực bên dưới để đặt lại mật khẩu:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <div style="background: #dc3545; color: white; font-size: 32px; font-weight: bold; 
                                        padding: 15px 30px; border-radius: 8px; display: inline-block; 
                                        letter-spacing: 5px;">{code}</div>
                        </div>
                        
                        <p><strong>Lưu ý quan trọng:</strong></p>
                        <ul>
                            <li>Mã xác thực có hiệu lực trong <strong>10 phút</strong></li>
                            <li>Bạn có tối đa <strong>3 lần</strong> nhập mã</li>
                            <li>Không chia sẻ mã này với bất kỳ ai</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; color: #7f8c8d; font-size: 14px;">
                        <p>Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.</p>
                        <p>© 2024 Hệ thống đấu giá trang sức. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "text_body": f"""
            Hệ thống đấu giá trang sức
            
            {greeting}
            
            Chúng tôi nhận được yêu cầu đặt lại mật khẩu cho tài khoản của bạn.
            
            Mã xác thực của bạn là: {code}
            
            Lưu ý:
            - Mã có hiệu lực trong 10 phút
            - Bạn có tối đa 3 lần nhập mã
            - Không chia sẻ mã này với bất kỳ ai
            
            Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
            """
        }
    
    @staticmethod
    def welcome_template(user: User) -> Dict[str, str]:
        """Template for welcome email"""
        return {
            "subject": "Chào mừng bạn đến với Hệ thống đấu giá trang sức!",
            "html_body": f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <h1 style="color: #2c3e50;">🏺 Hệ thống đấu giá trang sức</h1>
                    </div>
                    
                    <div style="background: #d4edda; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #28a745;">
                        <h2 style="color: #155724; margin-top: 0;">Chào mừng {user.full_name}!</h2>
                        <p>Tài khoản của bạn đã được xác thực thành công.</p>
                        <p>Bạn có thể bắt đầu khám phá và tham gia đấu giá các sản phẩm trang sức độc đáo tại hệ thống của chúng tôi.</p>
                        
                        <div style="margin: 20px 0;">
                            <h3 style="color: #155724;">Bạn có thể:</h3>
                            <ul>
                                <li>🔍 Duyệt xem các sản phẩm trang sức đang đấu giá</li>
                                <li>💎 Tham gia đấu giá các món trang sức yêu thích</li>
                                <li>📝 Ký gửi trang sức của bạn để đấu giá</li>
                                <li>💰 Theo dõi lịch sử đấu giá và thanh toán</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div style="text-align: center; color: #7f8c8d; font-size: 14px;">
                        <p>Cảm ơn bạn đã tin tưởng và sử dụng dịch vụ của chúng tôi!</p>
                        <p>© 2024 Hệ thống đấu giá trang sức. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """,
            "text_body": f"""
            Hệ thống đấu giá trang sức
            
            Chào mừng {user.full_name}!
            
            Tài khoản của bạn đã được xác thực thành công.
            
            Bạn có thể bắt đầu khám phá và tham gia đấu giá các sản phẩm trang sức độc đáo tại hệ thống của chúng tôi.
            
            Cảm ơn bạn đã tin tưởng và sử dụng dịch vụ của chúng tôi!
            """
        }
