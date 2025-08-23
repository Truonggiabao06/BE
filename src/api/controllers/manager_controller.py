from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from typing import Dict, Any, Optional
from decimal import Decimal

from src.domain.models.auction_item import AuctionItem, ItemStatus
from src.domain.models.fee_config import FeeConfig, FeeType, FeeAppliedTo
from src.domain.models.user import UserRole
from src.domain.repositories.auction_item_repo import IAuctionItemRepository
from src.domain.repositories.fee_config_repo import IFeeConfigRepository
from src.api.middleware.auth_middleware import require_auth, require_manager, get_current_user
from src.api.utils.response_helper import success_response, error_response, validation_error_response, paginated_response

logger = logging.getLogger(__name__)

# Create Blueprint
manager_bp = Blueprint('manager', __name__, url_prefix='/api/manager')

class ManagerController:
    """Controller for manager-specific operations"""

    def __init__(self, auction_item_repo: IAuctionItemRepository, fee_config_repo: IFeeConfigRepository):
        self.auction_item_repo = auction_item_repo
        self.fee_config_repo = fee_config_repo
        self._register_routes()

    def _register_routes(self):
        """Register all manager routes"""
        # Item approval
        manager_bp.add_url_rule('/items/pending-approval', 'get_items_pending_approval', self.get_items_pending_approval, methods=['GET'])
        manager_bp.add_url_rule('/items/<int:item_id>/approve', 'approve_item', self.approve_item, methods=['POST'])
        manager_bp.add_url_rule('/items/<int:item_id>/reject', 'reject_item', self.reject_item, methods=['POST'])
        
        # Fee configuration
        manager_bp.add_url_rule('/fees', 'list_fee_configs', self.list_fee_configs, methods=['GET'])
        manager_bp.add_url_rule('/fees', 'create_fee_config', self.create_fee_config, methods=['POST'])
        manager_bp.add_url_rule('/fees/<int:fee_id>', 'update_fee_config', self.update_fee_config, methods=['PUT'])
        manager_bp.add_url_rule('/fees/<int:fee_id>/activate', 'activate_fee_config', self.activate_fee_config, methods=['POST'])
        manager_bp.add_url_rule('/fees/<int:fee_id>/deactivate', 'deactivate_fee_config', self.deactivate_fee_config, methods=['POST'])
        
        # Reports and dashboard
        manager_bp.add_url_rule('/dashboard', 'get_dashboard', self.get_dashboard, methods=['GET'])
        manager_bp.add_url_rule('/reports/revenue', 'get_revenue_report', self.get_revenue_report, methods=['GET'])
        manager_bp.add_url_rule('/reports/items', 'get_items_report', self.get_items_report, methods=['GET'])

    @cross_origin()
    @require_manager
    def get_items_pending_approval(self):
        """Get items pending manager approval"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))

            # Validate pagination
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 20

            # Get items pending manager approval
            items = self.auction_item_repo.get_by_status(ItemStatus.PENDING_MANAGER_APPROVAL, page=page, limit=limit)
            total = self.auction_item_repo.count_by_status(ItemStatus.PENDING_MANAGER_APPROVAL)

            # Convert to response format
            items_data = []
            for item in items:
                items_data.append({
                    'id': item.id,
                    'title': item.title,
                    'description': item.description,
                    'category': item.category.value,
                    'condition': item.condition.value,
                    'material': item.material,
                    'weight': item.weight,
                    'images': item.images,
                    'preliminary_price': float(item.preliminary_price) if item.preliminary_price else None,
                    'final_price': float(item.final_price) if item.final_price else None,
                    'starting_price': float(item.starting_price) if item.starting_price else None,
                    'staff_notes': item.staff_notes,
                    'final_valued_at': item.final_valued_at.isoformat() if item.final_valued_at else None,
                    'final_valued_by': item.final_valued_by,
                    'seller_id': item.seller_id
                })

            return paginated_response(
                data=items_data,
                page=page,
                limit=limit,
                total=total,
                message="Lấy danh sách sản phẩm chờ phê duyệt thành công"
            )

        except Exception as e:
            logger.error(f"Get items pending approval error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy danh sách sản phẩm chờ phê duyệt", 500)

    @cross_origin()
    @require_manager
    def approve_item(self, item_id: int):
        """Approve item for auction"""
        try:
            data = request.get_json() or {}
            current_user = get_current_user()

            # Get item
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                return error_response("Không tìm thấy sản phẩm", 404)

            # Approve item
            notes = data.get('notes', '')
            item.manager_approve(current_user.id, notes)

            # Update in database
            updated_item = self.auction_item_repo.update(item)

            # TODO: Send notification to seller

            return success_response({
                'item': {
                    'id': updated_item.id,
                    'status': updated_item.status.value,
                    'approved_at': updated_item.approved_at.isoformat(),
                    'approved_by': updated_item.approved_by,
                    'manager_notes': updated_item.manager_notes
                }
            }, "Phê duyệt sản phẩm thành công")

        except ValueError as e:
            return validation_error_response(str(e))
        except Exception as e:
            logger.error(f"Approve item error: {str(e)}")
            return error_response("Lỗi hệ thống khi phê duyệt sản phẩm", 500)

    @cross_origin()
    @require_manager
    def reject_item(self, item_id: int):
        """Reject item"""
        try:
            data = request.get_json()
            current_user = get_current_user()

            if not data or 'reason' not in data:
                return validation_error_response("Thiếu lý do từ chối")

            reason = data['reason'].strip()
            if not reason:
                return validation_error_response("Lý do từ chối không được để trống")

            # Get item
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                return error_response("Không tìm thấy sản phẩm", 404)

            # Reject item
            item.manager_reject(current_user.id, reason)

            # Update in database
            updated_item = self.auction_item_repo.update(item)

            # TODO: Send notification to seller

            return success_response({
                'item': {
                    'id': updated_item.id,
                    'status': updated_item.status.value,
                    'rejection_reason': updated_item.rejection_reason,
                    'manager_notes': updated_item.manager_notes
                }
            }, "Từ chối sản phẩm thành công")

        except ValueError as e:
            return validation_error_response(str(e))
        except Exception as e:
            logger.error(f"Reject item error: {str(e)}")
            return error_response("Lỗi hệ thống khi từ chối sản phẩm", 500)

    @cross_origin()
    @require_manager
    def list_fee_configs(self):
        """List fee configurations"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))

            # Get fee configurations
            fee_configs = self.fee_config_repo.list(page=page, limit=limit)
            total = self.fee_config_repo.count()

            # Convert to response format
            configs_data = []
            for config in fee_configs:
                configs_data.append({
                    'id': config.id,
                    'fee_type': config.fee_type.value,
                    'name': config.name,
                    'description': config.description,
                    'rate': float(config.rate),
                    'fixed_amount': float(config.fixed_amount) if config.fixed_amount else None,
                    'min_amount': float(config.min_amount) if config.min_amount else None,
                    'max_amount': float(config.max_amount) if config.max_amount else None,
                    'applied_to': config.applied_to.value,
                    'is_active': config.is_active,
                    'created_at': config.created_at.isoformat() if config.created_at else None
                })

            return paginated_response(
                data=configs_data,
                page=page,
                limit=limit,
                total=total,
                message="Lấy danh sách cấu hình phí thành công"
            )

        except Exception as e:
            logger.error(f"List fee configs error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy danh sách cấu hình phí", 500)

    @cross_origin()
    @require_manager
    def create_fee_config(self):
        """Create new fee configuration"""
        try:
            data = request.get_json()
            current_user = get_current_user()

            if not data:
                return validation_error_response("Không có dữ liệu")

            # Validate required fields
            required_fields = ['fee_type', 'name', 'rate', 'applied_to']
            for field in required_fields:
                if field not in data:
                    return validation_error_response(f"Thiếu trường {field}")

            # Validate enums
            try:
                fee_type = FeeType(data['fee_type'])
                applied_to = FeeAppliedTo(data['applied_to'])
            except ValueError as e:
                return validation_error_response(f"Giá trị enum không hợp lệ: {str(e)}")

            # Validate rate
            try:
                rate = Decimal(str(data['rate']))
                if rate < 0:
                    return validation_error_response("Tỷ lệ phí không được âm")
            except (ValueError, TypeError):
                return validation_error_response("Tỷ lệ phí không hợp lệ")

            # Create fee config
            fee_config = FeeConfig(
                fee_type=fee_type,
                name=data['name'].strip(),
                description=data.get('description', '').strip(),
                rate=rate,
                fixed_amount=Decimal(str(data['fixed_amount'])) if data.get('fixed_amount') else None,
                min_amount=Decimal(str(data['min_amount'])) if data.get('min_amount') else None,
                max_amount=Decimal(str(data['max_amount'])) if data.get('max_amount') else None,
                applied_to=applied_to,
                is_active=data.get('is_active', True),
                created_by=current_user.id
            )

            # Save to database
            created_config = self.fee_config_repo.create(fee_config)

            return success_response({
                'fee_config': {
                    'id': created_config.id,
                    'fee_type': created_config.fee_type.value,
                    'name': created_config.name,
                    'rate': float(created_config.rate),
                    'is_active': created_config.is_active
                }
            }, "Tạo cấu hình phí thành công")

        except Exception as e:
            logger.error(f"Create fee config error: {str(e)}")
            return error_response("Lỗi hệ thống khi tạo cấu hình phí", 500)

    @cross_origin()
    @require_manager
    def get_dashboard(self):
        """Get manager dashboard statistics"""
        try:
            # Get item statistics by status
            item_stats = {}
            for status in ItemStatus:
                item_stats[status.value] = self.auction_item_repo.count_by_status(status)

            # Get fee configurations
            active_fees = len(self.fee_config_repo.get_active_configs())
            total_fees = self.fee_config_repo.count()

            return success_response({
                'item_statistics': item_stats,
                'fee_statistics': {
                    'active_configs': active_fees,
                    'total_configs': total_fees
                },
                'pending_approvals': item_stats.get('pending_manager_approval', 0)
            }, "Lấy thống kê dashboard thành công")

        except Exception as e:
            logger.error(f"Get manager dashboard error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy thống kê dashboard", 500)

    @cross_origin()
    @require_manager
    def get_revenue_report(self):
        """Get revenue report (placeholder)"""
        try:
            # TODO: Implement actual revenue calculation
            return success_response({
                'total_revenue': 0,
                'platform_fees': 0,
                'payment_fees': 0,
                'period': 'monthly'
            }, "Báo cáo doanh thu (đang phát triển)")

        except Exception as e:
            logger.error(f"Get revenue report error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy báo cáo doanh thu", 500)

    @cross_origin()
    @require_manager
    def get_items_report(self):
        """Get items report (placeholder)"""
        try:
            # TODO: Implement actual items report
            return success_response({
                'total_items': 0,
                'sold_items': 0,
                'success_rate': 0
            }, "Báo cáo sản phẩm (đang phát triển)")

        except Exception as e:
            logger.error(f"Get items report error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy báo cáo sản phẩm", 500)
