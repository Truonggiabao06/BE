"""
Notification Service - Business logic for notifications and real-time updates
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from enum import Enum

from src.domain.models.user import User
from src.domain.models.auction_session import AuctionSession
from src.domain.models.bid import Bid
from src.domain.models.payment import Payment

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types of notifications"""
    BID_PLACED = "bid_placed"
    BID_OUTBID = "bid_outbid"
    AUCTION_STARTED = "auction_started"
    AUCTION_ENDING = "auction_ending"
    AUCTION_ENDED = "auction_ended"
    AUCTION_WON = "auction_won"
    PAYMENT_DUE = "payment_due"
    PAYMENT_OVERDUE = "payment_overdue"
    PAYMENT_CONFIRMED = "payment_confirmed"
    ITEM_APPROVED = "item_approved"
    ITEM_REJECTED = "item_rejected"

class NotificationPriority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationService:
    """Service for notification management and real-time updates"""
    
    def __init__(self):
        # In a real implementation, this would connect to:
        # - WebSocket server for real-time notifications
        # - Email service for email notifications
        # - SMS service for SMS notifications
        # - Push notification service for mobile apps
        pass
    
    def notify_bid_placed(self, bid: Bid, session: AuctionSession, bidder: User) -> Dict[str, Any]:
        """Notify all participants about a new bid"""
        try:
            notification_data = {
                "type": NotificationType.BID_PLACED.value,
                "priority": NotificationPriority.MEDIUM.value,
                "session_id": session.id,
                "session_title": session.title,
                "bid_amount": bid.amount,
                "bidder_name": bidder.full_name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Có lượt đặt giá mới: {bid.amount:,.0f} VND trong phiên '{session.title}'"
            }
            
            # Notify all participants except the bidder
            recipients = [user_id for user_id in session.participants if user_id != bidder.id]
            
            # Send real-time notifications
            self._send_realtime_notification(recipients, notification_data)
            
            # Log notification
            logger.info(f"Sent bid notification for session {session.id}, amount {bid.amount}")
            
            return {
                "sent": True,
                "recipients": len(recipients),
                "notification_data": notification_data
            }
            
        except Exception as e:
            logger.error(f"Notify bid placed error: {str(e)}")
            return {"sent": False, "error": str(e)}
    
    def notify_bid_outbid(self, previous_highest_bidder: User, new_bid: Bid, session: AuctionSession) -> Dict[str, Any]:
        """Notify user when they've been outbid"""
        try:
            notification_data = {
                "type": NotificationType.BID_OUTBID.value,
                "priority": NotificationPriority.HIGH.value,
                "session_id": session.id,
                "session_title": session.title,
                "new_highest_bid": new_bid.amount,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Bạn đã bị vượt giá trong phiên '{session.title}'. Giá hiện tại: {new_bid.amount:,.0f} VND"
            }
            
            # Send to the outbid user
            self._send_realtime_notification([previous_highest_bidder.id], notification_data)
            self._send_email_notification(previous_highest_bidder.email, "Bạn đã bị vượt giá", notification_data)
            
            logger.info(f"Sent outbid notification to user {previous_highest_bidder.id}")
            
            return {
                "sent": True,
                "recipient": previous_highest_bidder.id,
                "notification_data": notification_data
            }
            
        except Exception as e:
            logger.error(f"Notify bid outbid error: {str(e)}")
            return {"sent": False, "error": str(e)}
    
    def notify_auction_starting(self, session: AuctionSession, participants: List[User]) -> Dict[str, Any]:
        """Notify participants that auction is starting"""
        try:
            notification_data = {
                "type": NotificationType.AUCTION_STARTED.value,
                "priority": NotificationPriority.HIGH.value,
                "session_id": session.id,
                "session_title": session.title,
                "start_time": session.actual_start_time.isoformat() if session.actual_start_time else None,
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Phiên đấu giá '{session.title}' đã bắt đầu!"
            }
            
            recipient_ids = [user.id for user in participants]
            
            # Send real-time notifications
            self._send_realtime_notification(recipient_ids, notification_data)
            
            # Send email notifications
            for user in participants:
                self._send_email_notification(user.email, "Phiên đấu giá đã bắt đầu", notification_data)
            
            logger.info(f"Sent auction start notifications for session {session.id}")
            
            return {
                "sent": True,
                "recipients": len(participants),
                "notification_data": notification_data
            }
            
        except Exception as e:
            logger.error(f"Notify auction starting error: {str(e)}")
            return {"sent": False, "error": str(e)}
    
    def notify_auction_ending_soon(self, session: AuctionSession, participants: List[User], minutes_remaining: int) -> Dict[str, Any]:
        """Notify participants that auction is ending soon"""
        try:
            notification_data = {
                "type": NotificationType.AUCTION_ENDING.value,
                "priority": NotificationPriority.URGENT.value,
                "session_id": session.id,
                "session_title": session.title,
                "minutes_remaining": minutes_remaining,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Phiên đấu giá '{session.title}' sẽ kết thúc trong {minutes_remaining} phút!"
            }
            
            recipient_ids = [user.id for user in participants]
            
            # Send real-time notifications
            self._send_realtime_notification(recipient_ids, notification_data)
            
            logger.info(f"Sent auction ending notification for session {session.id}")
            
            return {
                "sent": True,
                "recipients": len(participants),
                "notification_data": notification_data
            }
            
        except Exception as e:
            logger.error(f"Notify auction ending soon error: {str(e)}")
            return {"sent": False, "error": str(e)}
    
    def notify_auction_ended(self, session: AuctionSession, winner: Optional[User], participants: List[User]) -> Dict[str, Any]:
        """Notify all participants that auction has ended"""
        try:
            base_notification = {
                "type": NotificationType.AUCTION_ENDED.value,
                "priority": NotificationPriority.HIGH.value,
                "session_id": session.id,
                "session_title": session.title,
                "final_price": session.final_price,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            notifications_sent = 0
            
            # Notify winner
            if winner:
                winner_notification = {
                    **base_notification,
                    "type": NotificationType.AUCTION_WON.value,
                    "message": f"Chúc mừng! Bạn đã thắng phiên đấu giá '{session.title}' với giá {session.final_price:,.0f} VND"
                }
                
                self._send_realtime_notification([winner.id], winner_notification)
                self._send_email_notification(winner.email, "Chúc mừng bạn đã thắng đấu giá!", winner_notification)
                notifications_sent += 1
            
            # Notify other participants
            other_participants = [user for user in participants if not winner or user.id != winner.id]
            if other_participants:
                other_notification = {
                    **base_notification,
                    "message": f"Phiên đấu giá '{session.title}' đã kết thúc. Giá thắng: {session.final_price:,.0f} VND" if session.final_price else f"Phiên đấu giá '{session.title}' đã kết thúc mà không có người thắng."
                }
                
                other_ids = [user.id for user in other_participants]
                self._send_realtime_notification(other_ids, other_notification)
                notifications_sent += len(other_participants)
            
            logger.info(f"Sent auction ended notifications for session {session.id}")
            
            return {
                "sent": True,
                "recipients": notifications_sent,
                "winner_notified": winner is not None
            }
            
        except Exception as e:
            logger.error(f"Notify auction ended error: {str(e)}")
            return {"sent": False, "error": str(e)}
    
    def notify_payment_due(self, payment: Payment, user: User) -> Dict[str, Any]:
        """Notify user about payment due"""
        try:
            notification_data = {
                "type": NotificationType.PAYMENT_DUE.value,
                "priority": NotificationPriority.HIGH.value,
                "payment_id": payment.id,
                "amount": payment.total_amount,
                "due_date": payment.due_date.isoformat() if payment.due_date else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Bạn cần thanh toán {payment.total_amount:,.0f} VND trước ngày {payment.due_date.strftime('%d/%m/%Y') if payment.due_date else 'N/A'}"
            }
            
            self._send_realtime_notification([user.id], notification_data)
            self._send_email_notification(user.email, "Thông báo thanh toán", notification_data)
            
            logger.info(f"Sent payment due notification for payment {payment.id}")
            
            return {
                "sent": True,
                "recipient": user.id,
                "notification_data": notification_data
            }
            
        except Exception as e:
            logger.error(f"Notify payment due error: {str(e)}")
            return {"sent": False, "error": str(e)}
    
    def notify_payment_overdue(self, payment: Payment, user: User, days_overdue: int) -> Dict[str, Any]:
        """Notify user about overdue payment"""
        try:
            notification_data = {
                "type": NotificationType.PAYMENT_OVERDUE.value,
                "priority": NotificationPriority.URGENT.value,
                "payment_id": payment.id,
                "amount": payment.total_amount,
                "days_overdue": days_overdue,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": f"Thanh toán {payment.total_amount:,.0f} VND đã quá hạn {days_overdue} ngày. Vui lòng thanh toán ngay!"
            }
            
            self._send_realtime_notification([user.id], notification_data)
            self._send_email_notification(user.email, "KHẨN CẤP: Thanh toán quá hạn", notification_data)
            
            logger.info(f"Sent payment overdue notification for payment {payment.id}")
            
            return {
                "sent": True,
                "recipient": user.id,
                "notification_data": notification_data
            }
            
        except Exception as e:
            logger.error(f"Notify payment overdue error: {str(e)}")
            return {"sent": False, "error": str(e)}
    
    def notify_item_status_change(self, item_id: int, seller: User, new_status: str, admin_notes: str = "") -> Dict[str, Any]:
        """Notify seller about item status change"""
        try:
            if new_status == "approved":
                notification_type = NotificationType.ITEM_APPROVED
                message = f"Sản phẩm #{item_id} của bạn đã được duyệt và có thể tham gia đấu giá"
                priority = NotificationPriority.MEDIUM
            else:
                notification_type = NotificationType.ITEM_REJECTED
                message = f"Sản phẩm #{item_id} của bạn đã bị từ chối. Lý do: {admin_notes}"
                priority = NotificationPriority.HIGH
            
            notification_data = {
                "type": notification_type.value,
                "priority": priority.value,
                "item_id": item_id,
                "new_status": new_status,
                "admin_notes": admin_notes,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "message": message
            }
            
            self._send_realtime_notification([seller.id], notification_data)
            self._send_email_notification(seller.email, f"Cập nhật trạng thái sản phẩm #{item_id}", notification_data)
            
            logger.info(f"Sent item status change notification for item {item_id}")
            
            return {
                "sent": True,
                "recipient": seller.id,
                "notification_data": notification_data
            }
            
        except Exception as e:
            logger.error(f"Notify item status change error: {str(e)}")
            return {"sent": False, "error": str(e)}
    
    def get_user_notifications(self, user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent notifications for a user"""
        try:
            # In a real implementation, this would fetch from a notifications database
            # For now, return empty list as placeholder
            return []
            
        except Exception as e:
            logger.error(f"Get user notifications error: {str(e)}")
            return []
    
    def mark_notification_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        try:
            # In a real implementation, this would update the notification status
            logger.info(f"Marked notification {notification_id} as read for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Mark notification read error: {str(e)}")
            return False
    
    def _send_realtime_notification(self, recipient_ids: List[int], notification_data: Dict[str, Any]) -> None:
        """Send real-time notification via WebSocket"""
        try:
            # In a real implementation, this would:
            # 1. Connect to WebSocket server
            # 2. Send notification to connected users
            # 3. Store notification in database for offline users
            
            logger.info(f"Real-time notification sent to {len(recipient_ids)} users: {notification_data['type']}")
            
        except Exception as e:
            logger.error(f"Send realtime notification error: {str(e)}")
    
    def _send_email_notification(self, email: str, subject: str, notification_data: Dict[str, Any]) -> None:
        """Send email notification"""
        try:
            # In a real implementation, this would:
            # 1. Format email template
            # 2. Send via email service (SMTP, SendGrid, etc.)
            
            logger.info(f"Email notification sent to {email}: {subject}")
            
        except Exception as e:
            logger.error(f"Send email notification error: {str(e)}")
    
    def _send_sms_notification(self, phone: str, message: str) -> None:
        """Send SMS notification"""
        try:
            # In a real implementation, this would send SMS via SMS service
            logger.info(f"SMS notification sent to {phone}: {message[:50]}...")
            
        except Exception as e:
            logger.error(f"Send SMS notification error: {str(e)}")
    
    def schedule_auction_reminders(self, session: AuctionSession, participants: List[User]) -> Dict[str, Any]:
        """Schedule reminder notifications for auction"""
        try:
            # In a real implementation, this would:
            # 1. Schedule notifications at specific times (1 hour before, 15 minutes before, etc.)
            # 2. Use a task queue (Celery, RQ) to handle scheduled notifications
            
            reminders_scheduled = []
            
            if session.start_time:
                # Schedule reminder 1 hour before start
                reminders_scheduled.append("1_hour_before_start")
                
                # Schedule reminder 15 minutes before start
                reminders_scheduled.append("15_minutes_before_start")
            
            if session.end_time:
                # Schedule reminder 15 minutes before end
                reminders_scheduled.append("15_minutes_before_end")
                
                # Schedule reminder 5 minutes before end
                reminders_scheduled.append("5_minutes_before_end")
            
            logger.info(f"Scheduled {len(reminders_scheduled)} reminders for session {session.id}")
            
            return {
                "scheduled": True,
                "reminders": reminders_scheduled,
                "participants": len(participants)
            }
            
        except Exception as e:
            logger.error(f"Schedule auction reminders error: {str(e)}")
            return {"scheduled": False, "error": str(e)}
