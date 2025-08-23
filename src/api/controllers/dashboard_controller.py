from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from src.domain.models.auction_item import ItemStatus
from src.domain.models.user import UserRole
from src.domain.repositories.auction_item_repo import IAuctionItemRepository
from src.domain.repositories.auction_session_repo import IAuctionSessionRepository
from src.domain.repositories.payment_repo import IPaymentRepository
from src.domain.repositories.user_repo import IUserRepository
from src.api.middleware.auth_middleware import require_auth, require_manager, get_current_user
from src.api.utils.response_helper import success_response, error_response, validation_error_response

logger = logging.getLogger(__name__)

# Create Blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')

class DashboardController:
    """Controller for dashboard and reporting"""

    def __init__(self, 
                 auction_item_repo: IAuctionItemRepository,
                 auction_session_repo: IAuctionSessionRepository,
                 payment_repo: IPaymentRepository,
                 user_repo: IUserRepository):
        self.auction_item_repo = auction_item_repo
        self.auction_session_repo = auction_session_repo
        self.payment_repo = payment_repo
        self.user_repo = user_repo
        self._register_routes()

    def _register_routes(self):
        """Register all dashboard routes"""
        # General dashboard
        dashboard_bp.add_url_rule('/overview', 'get_overview', self.get_overview, methods=['GET'])
        
        # Staff dashboard
        dashboard_bp.add_url_rule('/staff', 'get_staff_dashboard', self.get_staff_dashboard, methods=['GET'])
        
        # Manager dashboard
        dashboard_bp.add_url_rule('/manager', 'get_manager_dashboard', self.get_manager_dashboard, methods=['GET'])
        
        # Reports
        dashboard_bp.add_url_rule('/reports/revenue', 'get_revenue_report', self.get_revenue_report, methods=['GET'])
        dashboard_bp.add_url_rule('/reports/items', 'get_items_report', self.get_items_report, methods=['GET'])
        dashboard_bp.add_url_rule('/reports/users', 'get_users_report', self.get_users_report, methods=['GET'])
        dashboard_bp.add_url_rule('/reports/performance', 'get_performance_report', self.get_performance_report, methods=['GET'])

    @cross_origin()
    @require_auth
    def get_overview(self):
        """Get general dashboard overview"""
        try:
            current_user = get_current_user()
            
            # Basic statistics
            overview = {
                'total_items': self.auction_item_repo.count_by_status(ItemStatus.PENDING_APPROVAL) + 
                              self.auction_item_repo.count_by_status(ItemStatus.APPROVED) +
                              self.auction_item_repo.count_by_status(ItemStatus.COMPLETED),
                'active_auctions': 0,  # TODO: Implement when auction sessions are ready
                'completed_auctions': 0,  # TODO: Implement
                'total_users': 0,  # TODO: Implement user count
                'pending_approvals': self.auction_item_repo.count_by_status(ItemStatus.PENDING_APPROVAL),
                'user_role': current_user.role.value
            }

            # Role-specific data
            if current_user.is_staff:
                overview['staff_assignments'] = self.auction_item_repo.count_by_staff_assignment(current_user.id)
                
            if current_user.role in [UserRole.MANAGER, UserRole.ADMIN]:
                overview['pending_manager_approval'] = self.auction_item_repo.count_by_status(ItemStatus.PENDING_MANAGER_APPROVAL)

            return success_response(overview, "Lấy tổng quan dashboard thành công")

        except Exception as e:
            logger.error(f"Get overview error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy tổng quan dashboard", 500)

    @cross_origin()
    @require_auth
    def get_staff_dashboard(self):
        """Get staff-specific dashboard"""
        try:
            current_user = get_current_user()
            
            if not current_user.is_staff:
                return error_response("Chỉ nhân viên mới có thể truy cập dashboard này", 403)

            # Staff workflow statistics
            stats = {
                'pending_approval': self.auction_item_repo.count_by_status(ItemStatus.PENDING_APPROVAL),
                'preliminary_valued': self.auction_item_repo.count_by_status(ItemStatus.PRELIMINARY_VALUED),
                'awaiting_item': self.auction_item_repo.count_by_status(ItemStatus.AWAITING_ITEM),
                'item_received': self.auction_item_repo.count_by_status(ItemStatus.ITEM_RECEIVED),
                'final_valued': self.auction_item_repo.count_by_status(ItemStatus.FINAL_VALUED),
                'my_assignments': self.auction_item_repo.count_by_staff_assignment(current_user.id)
            }

            # Recent activity (placeholder)
            recent_activity = []  # TODO: Implement recent activity tracking

            dashboard_data = {
                'statistics': stats,
                'recent_activity': recent_activity,
                'user_info': {
                    'id': current_user.id,
                    'name': current_user.full_name,
                    'role': current_user.role.value
                }
            }

            return success_response(dashboard_data, "Lấy dashboard nhân viên thành công")

        except Exception as e:
            logger.error(f"Get staff dashboard error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy dashboard nhân viên", 500)

    @cross_origin()
    @require_manager
    def get_manager_dashboard(self):
        """Get manager-specific dashboard"""
        try:
            current_user = get_current_user()

            # Manager overview statistics
            item_stats = {}
            for status in ItemStatus:
                item_stats[status.value] = self.auction_item_repo.count_by_status(status)

            # Financial overview (placeholder)
            financial_stats = {
                'total_revenue': 0,  # TODO: Calculate from completed payments
                'platform_fees': 0,  # TODO: Calculate platform fees
                'pending_payments': 0,  # TODO: Count pending payments
                'this_month_revenue': 0  # TODO: Calculate monthly revenue
            }

            # Performance metrics
            total_items = sum(item_stats.values())
            approved_items = item_stats.get('approved', 0) + item_stats.get('completed', 0)
            approval_rate = (approved_items / max(total_items, 1)) * 100

            performance_stats = {
                'approval_rate': round(approval_rate, 2),
                'total_items_processed': total_items,
                'items_pending_approval': item_stats.get('pending_manager_approval', 0)
            }

            dashboard_data = {
                'item_statistics': item_stats,
                'financial_statistics': financial_stats,
                'performance_statistics': performance_stats,
                'user_info': {
                    'id': current_user.id,
                    'name': current_user.full_name,
                    'role': current_user.role.value
                }
            }

            return success_response(dashboard_data, "Lấy dashboard quản lý thành công")

        except Exception as e:
            logger.error(f"Get manager dashboard error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy dashboard quản lý", 500)

    @cross_origin()
    @require_manager
    def get_revenue_report(self):
        """Get revenue report"""
        try:
            # Get query parameters
            period = request.args.get('period', 'monthly')  # daily, weekly, monthly, yearly
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            # TODO: Implement actual revenue calculation from payments
            revenue_data = {
                'period': period,
                'total_revenue': 0,
                'platform_fees': 0,
                'payment_processing_fees': 0,
                'net_revenue': 0,
                'transaction_count': 0,
                'average_transaction_value': 0,
                'revenue_by_period': [],  # Array of {period: string, revenue: number}
                'top_categories': []  # Array of {category: string, revenue: number}
            }

            return success_response(revenue_data, "Lấy báo cáo doanh thu thành công")

        except Exception as e:
            logger.error(f"Get revenue report error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy báo cáo doanh thu", 500)

    @cross_origin()
    @require_manager
    def get_items_report(self):
        """Get items performance report"""
        try:
            # Get query parameters
            period = request.args.get('period', 'monthly')
            category = request.args.get('category')

            # Item statistics by status
            item_stats = {}
            for status in ItemStatus:
                count = self.auction_item_repo.count_by_status(status)
                item_stats[status.value] = count

            # Calculate success rate
            total_items = sum(item_stats.values())
            completed_items = item_stats.get('completed', 0)
            success_rate = (completed_items / max(total_items, 1)) * 100

            # TODO: Implement category breakdown, time series data
            items_data = {
                'period': period,
                'total_items': total_items,
                'completed_items': completed_items,
                'success_rate': round(success_rate, 2),
                'items_by_status': item_stats,
                'items_by_category': {},  # TODO: Implement
                'items_by_period': [],  # TODO: Implement time series
                'average_processing_time': 0,  # TODO: Calculate processing time
                'rejection_reasons': []  # TODO: Analyze rejection reasons
            }

            return success_response(items_data, "Lấy báo cáo sản phẩm thành công")

        except Exception as e:
            logger.error(f"Get items report error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy báo cáo sản phẩm", 500)

    @cross_origin()
    @require_manager
    def get_users_report(self):
        """Get users report"""
        try:
            # TODO: Implement user statistics
            users_data = {
                'total_users': 0,
                'active_users': 0,
                'new_users_this_month': 0,
                'users_by_role': {
                    'buyer': 0,
                    'seller': 0,
                    'staff': 0,
                    'manager': 0,
                    'admin': 0
                },
                'user_activity': [],  # TODO: User activity metrics
                'top_sellers': [],  # TODO: Top sellers by items/revenue
                'top_buyers': []  # TODO: Top buyers by spending
            }

            return success_response(users_data, "Lấy báo cáo người dùng thành công")

        except Exception as e:
            logger.error(f"Get users report error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy báo cáo người dùng", 500)

    @cross_origin()
    @require_manager
    def get_performance_report(self):
        """Get system performance report"""
        try:
            # TODO: Implement performance metrics
            performance_data = {
                'processing_times': {
                    'average_approval_time': 0,  # Hours
                    'average_valuation_time': 0,  # Hours
                    'average_auction_duration': 0  # Hours
                },
                'efficiency_metrics': {
                    'items_processed_per_day': 0,
                    'staff_productivity': [],  # Per staff member
                    'approval_rate_by_staff': []
                },
                'system_health': {
                    'api_response_time': 0,  # Milliseconds
                    'database_performance': 'good',
                    'error_rate': 0  # Percentage
                }
            }

            return success_response(performance_data, "Lấy báo cáo hiệu suất thành công")

        except Exception as e:
            logger.error(f"Get performance report error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy báo cáo hiệu suất", 500)
