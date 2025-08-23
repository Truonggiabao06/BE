from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from typing import Dict, Any, Optional

from src.domain.models.notification import Notification, NotificationType, NotificationStatus
from src.domain.repositories.notification_repo import INotificationRepository
from src.api.middleware.auth_middleware import require_auth, get_current_user
from src.api.utils.response_helper import success_response, error_response, validation_error_response, paginated_response

logger = logging.getLogger(__name__)

# Create Blueprint
notification_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

class NotificationController:
    """Controller for notification operations"""

    def __init__(self, notification_repo: INotificationRepository):
        self.notification_repo = notification_repo
        self._register_routes()

    def _register_routes(self):
        """Register all notification routes"""
        notification_bp.add_url_rule('', 'list_notifications', self.list_notifications, methods=['GET'])
        notification_bp.add_url_rule('/unread', 'get_unread_notifications', self.get_unread_notifications, methods=['GET'])
        notification_bp.add_url_rule('/unread/count', 'get_unread_count', self.get_unread_count, methods=['GET'])
        notification_bp.add_url_rule('/<int:notification_id>/read', 'mark_as_read', self.mark_as_read, methods=['POST'])
        notification_bp.add_url_rule('/mark-all-read', 'mark_all_as_read', self.mark_all_as_read, methods=['POST'])

    @cross_origin()
    @require_auth
    def list_notifications(self):
        """Get user's notifications with pagination"""
        try:
            current_user = get_current_user()
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            status = request.args.get('status')  # unread, read, archived

            # Validate pagination
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 20

            # Get notifications
            notifications = self.notification_repo.get_by_recipient(current_user.id, page=page, limit=limit)

            # Filter by status if provided
            if status:
                try:
                    status_filter = NotificationStatus(status)
                    notifications = [n for n in notifications if n.status == status_filter]
                except ValueError:
                    return validation_error_response(f"Invalid status: {status}")

            # Convert to response format
            notifications_data = []
            for notification in notifications:
                notifications_data.append({
                    'id': notification.id,
                    'type': notification.type.value,
                    'title': notification.title,
                    'message': notification.message,
                    'data': notification.data,
                    'status': notification.status.value,
                    'created_at': notification.created_at.isoformat() if notification.created_at else None,
                    'read_at': notification.read_at.isoformat() if notification.read_at else None
                })

            return paginated_response(
                data=notifications_data,
                page=page,
                limit=limit,
                total=len(notifications_data),
                message="Lấy danh sách thông báo thành công"
            )

        except Exception as e:
            logger.error(f"List notifications error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy danh sách thông báo", 500)

    @cross_origin()
    @require_auth
    def get_unread_notifications(self):
        """Get user's unread notifications"""
        try:
            current_user = get_current_user()
            
            # Get unread notifications
            notifications = self.notification_repo.get_unread_by_recipient(current_user.id)

            # Convert to response format
            notifications_data = []
            for notification in notifications:
                notifications_data.append({
                    'id': notification.id,
                    'type': notification.type.value,
                    'title': notification.title,
                    'message': notification.message,
                    'data': notification.data,
                    'created_at': notification.created_at.isoformat() if notification.created_at else None
                })

            return success_response({
                'notifications': notifications_data,
                'count': len(notifications_data)
            }, "Lấy thông báo chưa đọc thành công")

        except Exception as e:
            logger.error(f"Get unread notifications error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy thông báo chưa đọc", 500)

    @cross_origin()
    @require_auth
    def get_unread_count(self):
        """Get count of unread notifications"""
        try:
            current_user = get_current_user()
            
            # Get unread count
            count = self.notification_repo.count_unread(current_user.id)

            return success_response({
                'unread_count': count
            }, "Lấy số lượng thông báo chưa đọc thành công")

        except Exception as e:
            logger.error(f"Get unread count error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy số lượng thông báo chưa đọc", 500)

    @cross_origin()
    @require_auth
    def mark_as_read(self, notification_id: int):
        """Mark a notification as read"""
        try:
            current_user = get_current_user()
            
            # Get notification
            notification = self.notification_repo.get(notification_id)
            if not notification:
                return error_response("Không tìm thấy thông báo", 404)

            # Check ownership
            if notification.recipient_id != current_user.id:
                return error_response("Không có quyền truy cập thông báo này", 403)

            # Mark as read
            if notification.status == NotificationStatus.UNREAD:
                notification.mark_as_read()
                self.notification_repo.update(notification)

            return success_response({
                'notification': {
                    'id': notification.id,
                    'status': notification.status.value,
                    'read_at': notification.read_at.isoformat() if notification.read_at else None
                }
            }, "Đánh dấu thông báo đã đọc thành công")

        except Exception as e:
            logger.error(f"Mark as read error: {str(e)}")
            return error_response("Lỗi hệ thống khi đánh dấu thông báo đã đọc", 500)

    @cross_origin()
    @require_auth
    def mark_all_as_read(self):
        """Mark all notifications as read for current user"""
        try:
            current_user = get_current_user()
            
            # Mark all as read
            count = self.notification_repo.mark_all_as_read(current_user.id)

            return success_response({
                'marked_count': count
            }, f"Đánh dấu {count} thông báo đã đọc thành công")

        except Exception as e:
            logger.error(f"Mark all as read error: {str(e)}")
            return error_response("Lỗi hệ thống khi đánh dấu tất cả thông báo đã đọc", 500)
