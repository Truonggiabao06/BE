from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from decimal import Decimal

from src.domain.models.auction_item import AuctionItem, ItemStatus
from src.domain.models.user import UserRole
from src.domain.repositories.auction_item_repo import IAuctionItemRepository
from src.api.middleware.auth_middleware import require_auth, require_staff, get_current_user
from src.api.utils.response_helper import success_response, error_response, validation_error_response, paginated_response

# Bỏ logger để đơn giản

# Create Blueprint
staff_bp = Blueprint('staff', __name__, url_prefix='/api/staff')

class StaffController:
    """Controller for staff-specific operations"""

    def __init__(self, auction_item_repo: IAuctionItemRepository):
        self.auction_item_repo = auction_item_repo
        self._register_routes()

    def _register_routes(self):
        """Register all staff routes"""
        # Item management
        staff_bp.add_url_rule('/items/pending', 'get_pending_items', self.get_pending_items, methods=['GET'])
        staff_bp.add_url_rule('/items/<int:item_id>/preliminary-valuation', 'set_preliminary_valuation', self.set_preliminary_valuation, methods=['POST'])
        staff_bp.add_url_rule('/items/<int:item_id>/confirm-received', 'confirm_item_received', self.confirm_item_received, methods=['POST'])
        staff_bp.add_url_rule('/items/<int:item_id>/final-valuation', 'set_final_valuation', self.set_final_valuation, methods=['POST'])
        staff_bp.add_url_rule('/items/my-assignments', 'get_my_assignments', self.get_my_assignments, methods=['GET'])
        
        # Dashboard
        staff_bp.add_url_rule('/dashboard', 'get_dashboard', self.get_dashboard, methods=['GET'])

    @cross_origin()
    @require_staff
    def get_pending_items(self):
        """Get items pending approval/valuation"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            status = request.args.get('status', 'pending_approval')

            # Validate pagination
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 20

            # Parse status filter
            try:
                status_filter = ItemStatus(status)
            except ValueError:
                return validation_error_response(f"Invalid status: {status}")

            # Get items by status
            items = self.auction_item_repo.get_by_status(status_filter, page=page, limit=limit)
            total = self.auction_item_repo.count_by_status(status_filter)

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
                    'status': item.status.value,
                    'preliminary_price': float(item.preliminary_price) if item.preliminary_price else None,
                    'final_price': float(item.final_price) if item.final_price else None,
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                    'seller_id': item.seller_id
                })

            return paginated_response(
                data=items_data,
                page=page,
                limit=limit,
                total=total,
                message=f"Lấy danh sách sản phẩm {status} thành công"
            )

        except Exception as e:
            logger.error(f"Get pending items error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy danh sách sản phẩm", 500)

    @cross_origin()
    @require_staff
    def set_preliminary_valuation(self, item_id: int):
        """Set preliminary valuation for an item"""
        try:
            data = request.get_json()
            current_user = get_current_user()

            if not data:
                return validation_error_response("Không có dữ liệu")

            # Validate required fields
            if 'preliminary_price' not in data:
                return validation_error_response("Thiếu giá định giá sơ bộ")

            try:
                preliminary_price = Decimal(str(data['preliminary_price']))
                if preliminary_price <= 0:
                    return validation_error_response("Giá định giá sơ bộ phải lớn hơn 0")
            except (ValueError, TypeError):
                return validation_error_response("Giá định giá sơ bộ không hợp lệ")

            # Get item
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                return error_response("Không tìm thấy sản phẩm", 404)

            # Set preliminary valuation
            notes = data.get('notes', '')
            item.set_preliminary_valuation(current_user.id, preliminary_price, notes)

            # Update in database
            updated_item = self.auction_item_repo.update(item)

            # TODO: Send notification to seller

            return success_response({
                'item': {
                    'id': updated_item.id,
                    'status': updated_item.status.value,
                    'preliminary_price': float(updated_item.preliminary_price),
                    'preliminary_valued_at': updated_item.preliminary_valued_at.isoformat()
                }
            }, "Định giá sơ bộ thành công")

        except ValueError as e:
            return validation_error_response(str(e))
        except Exception as e:
            logger.error(f"Set preliminary valuation error: {str(e)}")
            return error_response("Lỗi hệ thống khi định giá sơ bộ", 500)

    @cross_origin()
    @require_staff
    def confirm_item_received(self, item_id: int):
        """Confirm that physical item has been received"""
        try:
            current_user = get_current_user()

            # Get item
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                return error_response("Không tìm thấy sản phẩm", 404)

            # Confirm item received
            item.confirm_item_received(current_user.id)

            # Update in database
            updated_item = self.auction_item_repo.update(item)

            return success_response({
                'item': {
                    'id': updated_item.id,
                    'status': updated_item.status.value,
                    'item_received_at': updated_item.item_received_at.isoformat()
                }
            }, "Xác nhận nhận trang sức thành công")

        except ValueError as e:
            return validation_error_response(str(e))
        except Exception as e:
            logger.error(f"Confirm item received error: {str(e)}")
            return error_response("Lỗi hệ thống khi xác nhận nhận trang sức", 500)

    @cross_origin()
    @require_staff
    def set_final_valuation(self, item_id: int):
        """Set final valuation for an item after receiving it"""
        try:
            data = request.get_json()
            current_user = get_current_user()

            if not data:
                return validation_error_response("Không có dữ liệu")

            # Validate required fields
            required_fields = ['final_price', 'starting_price']
            for field in required_fields:
                if field not in data:
                    return validation_error_response(f"Thiếu trường {field}")

            try:
                final_price = Decimal(str(data['final_price']))
                starting_price = Decimal(str(data['starting_price']))
                
                if final_price <= 0 or starting_price <= 0:
                    return validation_error_response("Giá phải lớn hơn 0")
                    
                if starting_price > final_price:
                    return validation_error_response("Giá khởi điểm không được lớn hơn giá định giá")
                    
            except (ValueError, TypeError):
                return validation_error_response("Giá không hợp lệ")

            # Get item
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                return error_response("Không tìm thấy sản phẩm", 404)

            # Set final valuation
            notes = data.get('notes', '')
            item.set_final_valuation(current_user.id, final_price, starting_price, notes)

            # Submit for manager approval if needed (high value items)
            if final_price >= Decimal('50000000'):  # 50 million VND threshold
                item.submit_for_manager_approval()

            # Update in database
            updated_item = self.auction_item_repo.update(item)

            # TODO: Send notification to manager if approval needed

            return success_response({
                'item': {
                    'id': updated_item.id,
                    'status': updated_item.status.value,
                    'final_price': float(updated_item.final_price),
                    'starting_price': float(updated_item.starting_price),
                    'final_valued_at': updated_item.final_valued_at.isoformat(),
                    'needs_manager_approval': updated_item.status == ItemStatus.PENDING_MANAGER_APPROVAL
                }
            }, "Định giá cuối cùng thành công")

        except ValueError as e:
            return validation_error_response(str(e))
        except Exception as e:
            logger.error(f"Set final valuation error: {str(e)}")
            return error_response("Lỗi hệ thống khi định giá cuối cùng", 500)

    @cross_origin()
    @require_staff
    def get_my_assignments(self):
        """Get items assigned to current staff member"""
        try:
            current_user = get_current_user()
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))

            # Get items where current user is involved in valuation
            items = self.auction_item_repo.get_by_staff_assignment(current_user.id, page=page, limit=limit)
            total = self.auction_item_repo.count_by_staff_assignment(current_user.id)

            # Convert to response format
            items_data = []
            for item in items:
                items_data.append({
                    'id': item.id,
                    'title': item.title,
                    'status': item.status.value,
                    'preliminary_price': float(item.preliminary_price) if item.preliminary_price else None,
                    'final_price': float(item.final_price) if item.final_price else None,
                    'created_at': item.created_at.isoformat() if item.created_at else None,
                    'preliminary_valued_at': item.preliminary_valued_at.isoformat() if item.preliminary_valued_at else None,
                    'final_valued_at': item.final_valued_at.isoformat() if item.final_valued_at else None
                })

            return paginated_response(
                data=items_data,
                page=page,
                limit=limit,
                total=total,
                message="Lấy danh sách công việc thành công"
            )

        except Exception as e:
            logger.error(f"Get my assignments error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy danh sách công việc", 500)

    @cross_origin()
    @require_staff
    def get_dashboard(self):
        """Get staff dashboard statistics"""
        try:
            current_user = get_current_user()

            # Get statistics
            stats = {
                'pending_approval': self.auction_item_repo.count_by_status(ItemStatus.PENDING_APPROVAL),
                'preliminary_valued': self.auction_item_repo.count_by_status(ItemStatus.PRELIMINARY_VALUED),
                'awaiting_item': self.auction_item_repo.count_by_status(ItemStatus.AWAITING_ITEM),
                'item_received': self.auction_item_repo.count_by_status(ItemStatus.ITEM_RECEIVED),
                'final_valued': self.auction_item_repo.count_by_status(ItemStatus.FINAL_VALUED),
                'pending_manager_approval': self.auction_item_repo.count_by_status(ItemStatus.PENDING_MANAGER_APPROVAL),
                'my_assignments': self.auction_item_repo.count_by_staff_assignment(current_user.id)
            }

            return success_response({
                'statistics': stats,
                'user': {
                    'id': current_user.id,
                    'name': current_user.full_name,
                    'role': current_user.role.value
                }
            }, "Lấy thống kê dashboard thành công")

        except Exception as e:
            logger.error(f"Get staff dashboard error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy thống kê dashboard", 500)
