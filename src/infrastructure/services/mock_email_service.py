import logging
from datetime import datetime
from typing import Dict, Any
from src.domain.services.email_service import IEmailService, EmailTemplate
from src.domain.models.user import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockEmailService(IEmailService):
    """Mock email service for development - logs emails instead of sending them"""
    
    def __init__(self):
        self.sent_emails = []  # Store sent emails for testing
        logger.info("🔧 MockEmailService initialized - emails will be logged instead of sent")
    
    def send_verification_code(self, email: str, code: str, user_name: str = "") -> bool:
        """Send email verification code (mock)"""
        try:
            template = EmailTemplate.verification_code_template(code, user_name)
            
            # Log the email instead of sending
            logger.info("📧 MOCK EMAIL - Verification Code")
            logger.info(f"   To: {email}")
            logger.info(f"   Subject: {template['subject']}")
            logger.info(f"   Verification Code: {code}")
            logger.info(f"   User Name: {user_name or 'N/A'}")
            logger.info("   " + "="*50)
            
            # Store for testing
            from datetime import datetime
            email_data = {
                "type": "verification_code",
                "to": email,
                "code": code,
                "user_name": user_name,
                "subject": template['subject'],
                "sent_at": datetime.utcnow()
            }
            self.sent_emails.append(email_data)
            
            # Print to console for easy viewing
            print(f"\n🔐 VERIFICATION CODE EMAIL")
            print(f"📧 To: {email}")
            print(f"👤 User: {user_name or 'N/A'}")
            print(f"🔢 Code: {code}")
            print(f"⏰ Valid for: 10 minutes")
            print("="*50)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in mock email service: {str(e)}")
            return False
    
    def send_password_reset_code(self, email: str, code: str, user_name: str = "") -> bool:
        """Send password reset code (mock)"""
        try:
            template = EmailTemplate.password_reset_template(code, user_name)
            
            # Log the email instead of sending
            logger.info("📧 MOCK EMAIL - Password Reset Code")
            logger.info(f"   To: {email}")
            logger.info(f"   Subject: {template['subject']}")
            logger.info(f"   Reset Code: {code}")
            logger.info(f"   User Name: {user_name or 'N/A'}")
            logger.info("   " + "="*50)
            
            # Store for testing
            email_data = {
                "type": "password_reset",
                "to": email,
                "code": code,
                "user_name": user_name,
                "subject": template['subject'],
                "sent_at": datetime.utcnow()
            }
            self.sent_emails.append(email_data)
            
            # Print to console for easy viewing
            print(f"\n🔑 PASSWORD RESET EMAIL")
            print(f"📧 To: {email}")
            print(f"👤 User: {user_name or 'N/A'}")
            print(f"🔢 Reset Code: {code}")
            print(f"⏰ Valid for: 10 minutes")
            print("="*50)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in mock email service: {str(e)}")
            return False
    
    def send_welcome_email(self, user: User) -> bool:
        """Send welcome email (mock)"""
        try:
            template = EmailTemplate.welcome_template(user)
            
            # Log the email instead of sending
            logger.info("📧 MOCK EMAIL - Welcome Email")
            logger.info(f"   To: {user.email}")
            logger.info(f"   Subject: {template['subject']}")
            logger.info(f"   User: {user.full_name}")
            logger.info("   " + "="*50)
            
            # Store for testing
            email_data = {
                "type": "welcome",
                "to": user.email,
                "user_name": user.full_name,
                "subject": template['subject'],
                "sent_at": datetime.utcnow()
            }
            self.sent_emails.append(email_data)
            
            # Print to console for easy viewing
            print(f"\n🎉 WELCOME EMAIL")
            print(f"📧 To: {user.email}")
            print(f"👤 User: {user.full_name}")
            print(f"🎯 Role: {user.role.value}")
            print("="*50)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in mock email service: {str(e)}")
            return False
    
    def send_auction_notification(self, email: str, subject: str, message: str) -> bool:
        """Send auction notification (mock)"""
        try:
            # Log the email instead of sending
            logger.info("📧 MOCK EMAIL - Auction Notification")
            logger.info(f"   To: {email}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   Message: {message[:100]}...")
            logger.info("   " + "="*50)
            
            # Store for testing
            email_data = {
                "type": "auction_notification",
                "to": email,
                "subject": subject,
                "message": message,
                "sent_at": datetime.utcnow()
            }
            self.sent_emails.append(email_data)
            
            # Print to console for easy viewing
            print(f"\n🔔 AUCTION NOTIFICATION")
            print(f"📧 To: {email}")
            print(f"📋 Subject: {subject}")
            print(f"💬 Message: {message[:100]}...")
            print("="*50)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in mock email service: {str(e)}")
            return False
    
    def send_payment_confirmation(self, email: str, payment_details: Dict[str, Any]) -> bool:
        """Send payment confirmation (mock)"""
        try:
            # Log the email instead of sending
            logger.info("📧 MOCK EMAIL - Payment Confirmation")
            logger.info(f"   To: {email}")
            logger.info(f"   Amount: {payment_details.get('amount', 'N/A')}")
            logger.info(f"   Item: {payment_details.get('item_title', 'N/A')}")
            logger.info("   " + "="*50)
            
            # Store for testing
            email_data = {
                "type": "payment_confirmation",
                "to": email,
                "payment_details": payment_details,
                "sent_at": datetime.utcnow()
            }
            self.sent_emails.append(email_data)
            
            # Print to console for easy viewing
            print(f"\n💳 PAYMENT CONFIRMATION")
            print(f"📧 To: {email}")
            print(f"💰 Amount: {payment_details.get('amount', 'N/A')}")
            print(f"💎 Item: {payment_details.get('item_title', 'N/A')}")
            print("="*50)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in mock email service: {str(e)}")
            return False
    
    def get_sent_emails(self) -> list:
        """Get list of sent emails (for testing)"""
        return self.sent_emails
    
    def clear_sent_emails(self):
        """Clear sent emails list (for testing)"""
        self.sent_emails.clear()
        logger.info("🧹 Cleared sent emails list")
    
    def get_last_verification_code(self, email: str) -> str:
        """Get last verification code sent to email (for testing)"""
        for email_data in reversed(self.sent_emails):
            if email_data["to"] == email and email_data["type"] == "verification_code":
                return email_data["code"]
        return ""
