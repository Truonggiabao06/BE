from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from typing import Dict, Any, Optional

from src.domain.models.auction_item import AuctionItem, ItemCategory, ItemCondition, ItemStatus
from src.domain.models.user import UserRole
from src.domain.repositories.auction_item_repo import IAuctionItemRepository
from src.api.middleware.auth_middleware import require_auth, require_seller, require_email_verified, get_current_user, optional_auth
from src.api.utils.response_helper import success_response, error_response, validation_error_response, paginated_response

logger = logging.getLogger(__name__)

# Create Blueprint
auction_item_bp = Blueprint('auction_items', __name__, url_prefix='/api/auction-items')

class AuctionItemController:
    """Auction Item controller for handling auction item-related API endpoints"""

    def __init__(self, auction_item_repository: IAuctionItemRepository):
        self.auction_item_repo = auction_item_repository
        self._register_routes()

    def _register_routes(self):
        """Register all auction item routes"""
        auction_item_bp.add_url_rule('', 'list_items', self.list_items, methods=['GET'])
        auction_item_bp.add_url_rule('', 'create_item', self.create_item, methods=['POST'])
        auction_item_bp.add_url_rule('/<int:item_id>', 'get_item', self.get_item, methods=['GET'])
        auction_item_bp.add_url_rule('/<int:item_id>', 'update_item', self.update_item, methods=['PUT'])
        auction_item_bp.add_url_rule('/<int:item_id>', 'delete_item', self.delete_item, methods=['DELETE'])
        auction_item_bp.add_url_rule('/<int:item_id>/status', 'update_status', self.update_status, methods=['PATCH'])
        auction_item_bp.add_url_rule('/my-items', 'get_my_items', self.get_my_items, methods=['GET'])
        auction_item_bp.add_url_rule('/categories', 'get_categories', self.get_categories, methods=['GET'])
        auction_item_bp.add_url_rule('/search', 'search_items', self.search_items, methods=['GET'])

    @cross_origin()
    @optional_auth
    def list_items(self):
        """List auction items with pagination and filtering"""
        try:
            # Get query parameters
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            category = request.args.get('category')
            status = request.args.get('status', 'approved')  # Default to approved items
            min_price = request.args.get('min_price', type=float)
            max_price = request.args.get('max_price', type=float)
            condition = request.args.get('condition')

            # Validate pagination
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 20

            # Parse filters
            filters = {}
            if category:
                try:
                    filters['category'] = ItemCategory(category)
                except ValueError:
                    return validation_error_response(f"Invalid category: {category}")

            if status:
                try:
                    filters['status'] = ItemStatus(status)
                except ValueError:
                    return validation_error_response(f"Invalid status: {status}")

            if condition:
                try:
                    filters['condition'] = ItemCondition(condition)
                except ValueError:
                    return validation_error_response(f"Invalid condition: {condition}")

            if min_price is not None:
                filters['min_starting_price'] = min_price

            if max_price is not None:
                filters['max_starting_price'] = max_price

            # Get items (filtering will be done in memory for now)
            items = self.auction_item_repo.list(page=page, limit=limit)

            # Convert to response format
            items_data = []
            for item in items:
                item_data = self._item_to_dict(item)
                # Hide seller info for public listing
                if 'seller' in item_data:
                    item_data['seller'] = {
                        'id': item_data['seller']['id'],
                        'name': item_data['seller']['full_name']
                    }
                items_data.append(item_data)

            # For now, we'll use the count of returned items as total
            # In a real implementation, you'd have a separate count query
            total = len(items) if len(items) < limit else (page * limit) + 1

            return paginated_response(
                data=items_data,
                page=page,
                limit=limit,
                total=total,
                message="Lấy danh sách sản phẩm thành công"
            )

        except Exception as e:
            logger.error(f"List items error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy danh sách sản phẩm", 500)

    @cross_origin()
    @require_seller
    @require_email_verified
    def create_item(self):
        """Create new auction item"""
        try:
            data = request.get_json()
            current_user = get_current_user()

            # Validate required fields
            required_fields = ['title', 'description', 'category', 'condition', 'starting_price']
            if not data or not all(field in data for field in required_fields):
                return validation_error_response("Thiếu thông tin bắt buộc: title, description, category, condition, starting_price")

            # Validate data types and values
            try:
                category = ItemCategory(data['category'])
                condition = ItemCondition(data['condition'])
                starting_price = float(data['starting_price'])

                if starting_price <= 0:
                    return validation_error_response("Giá khởi điểm phải lớn hơn 0")

            except ValueError as e:
                return validation_error_response(f"Dữ liệu không hợp lệ: {str(e)}")

            # Create auction item
            auction_item = AuctionItem(
                title=data['title'].strip(),
                description=data['description'].strip(),
                category=category,
                condition=condition,
                starting_price=starting_price,
                reserve_price=data.get('reserve_price', starting_price),
                seller_id=current_user.id,
                status=ItemStatus.PENDING_APPROVAL,  # New items start as pending approval
                images=data.get('images', []),
                specifications=data.get('specifications', {}),
                provenance=data.get('provenance', '').strip(),
                estimated_value=data.get('estimated_value')
            )

            # Save to database
            created_item = self.auction_item_repo.create(auction_item)

            return success_response(
                message="Tạo sản phẩm đấu giá thành công! Sản phẩm đang chờ duyệt.",
                data={
                    "item": self._item_to_dict(created_item)
                }
            )

        except Exception as e:
            logger.error(f"Create item error: {str(e)}")
            return error_response("Lỗi hệ thống khi tạo sản phẩm", 500)

    @cross_origin()
    @optional_auth
    def get_item(self, item_id: int):
        """Get auction item by ID"""
        try:
            item = self.auction_item_repo.get(item_id)

            if not item:
                return error_response("Không tìm thấy sản phẩm", 404)

            # Check if user can view this item
            current_user = get_current_user()
            if item.status == ItemStatus.PENDING_APPROVAL:
                # Only seller and admin can view pending items
                if not current_user or (current_user.id != item.seller_id and current_user.role != UserRole.ADMIN):
                    return error_response("Không có quyền xem sản phẩm này", 403)

            return success_response(
                message="Lấy thông tin sản phẩm thành công",
                data={
                    "item": self._item_to_dict(item, include_seller_details=True)
                }
            )

        except Exception as e:
            logger.error(f"Get item error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy thông tin sản phẩm", 500)

    @cross_origin()
    def get_categories(self):
        """Get available item categories"""
        try:
            categories = [
                {
                    "value": category.value,
                    "label": self._get_category_label(category)
                }
                for category in ItemCategory
            ]

            return success_response(
                message="Lấy danh sách danh mục thành công",
                data={"categories": categories}
            )

        except Exception as e:
            logger.error(f"Get categories error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy danh mục", 500)

    @cross_origin()
    @require_auth
    def update_item(self, item_id: int):
        """Update auction item - placeholder"""
        return error_response("Chức năng đang phát triển", 501)

    @cross_origin()
    @require_auth
    def delete_item(self, item_id: int):
        """Delete auction item - placeholder"""
        return error_response("Chức năng đang phát triển", 501)

    @cross_origin()
    @require_auth
    def update_status(self, item_id: int):
        """Update status - placeholder"""
        return error_response("Chức năng đang phát triển", 501)

    @cross_origin()
    @require_auth
    def get_my_items(self):
        """Get items belonging to current user"""
        try:
            current_user = get_current_user()
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            status = request.args.get('status')

            # Validate pagination
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 20

            # Get user's items
            items = self.auction_item_repo.get_by_seller(current_user.id, page=page, limit=limit)

            # Filter by status if provided
            if status:
                try:
                    status_filter = ItemStatus(status)
                    items = [item for item in items if item.status == status_filter]
                except ValueError:
                    return validation_error_response(f"Invalid status: {status}")

            # Convert to response format
            items_data = []
            for item in items:
                items_data.append(self._item_to_dict(item, include_seller_details=False))

            return paginated_response(
                data=items_data,
                page=page,
                limit=limit,
                total=len(items_data),
                message="Lấy danh sách sản phẩm của tôi thành công"
            )

        except Exception as e:
            logger.error(f"Get my items error: {str(e)}")
            return error_response("Lỗi hệ thống khi lấy danh sách sản phẩm", 500)

    @cross_origin()
    @optional_auth
    def search_items(self):
        """Search items by various criteria"""
        try:
            # Get search parameters
            query = request.args.get('q', '').strip()
            category = request.args.get('category')
            condition = request.args.get('condition')
            min_price = request.args.get('min_price')
            max_price = request.args.get('max_price')
            status = request.args.get('status', 'approved')  # Default to approved items
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))

            # Validate pagination
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 20

            # For now, get all items and filter (in production, use database queries)
            try:
                status_filter = ItemStatus(status)
            except ValueError:
                status_filter = ItemStatus.APPROVED

            items = self.auction_item_repo.get_by_status(status_filter, page=1, limit=1000)

            # Apply filters
            filtered_items = []
            for item in items:
                # Text search in title and description
                if query and query.lower() not in item.title.lower() and query.lower() not in item.description.lower():
                    continue

                # Category filter
                if category and item.category.value != category:
                    continue

                # Condition filter
                if condition and item.condition.value != condition:
                    continue

                # Price range filter
                if min_price:
                    try:
                        min_val = float(min_price)
                        if item.starting_price < min_val:
                            continue
                    except ValueError:
                        pass

                if max_price:
                    try:
                        max_val = float(max_price)
                        if item.starting_price > max_val:
                            continue
                    except ValueError:
                        pass

                filtered_items.append(item)

            # Apply pagination to filtered results
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paginated_items = filtered_items[start_idx:end_idx]

            # Convert to response format
            items_data = []
            for item in paginated_items:
                items_data.append(self._item_to_dict(item, include_seller_details=False))

            return paginated_response(
                data=items_data,
                page=page,
                limit=limit,
                total=len(filtered_items),
                message="Tìm kiếm sản phẩm thành công"
            )

        except Exception as e:
            logger.error(f"Search items error: {str(e)}")
            return error_response("Lỗi hệ thống khi tìm kiếm sản phẩm", 500)

    def _item_to_dict(self, item: AuctionItem, include_seller_details: bool = False):
        """Convert AuctionItem to dictionary"""
        item_dict = {
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "category": item.category.value,
            "condition": item.condition.value,
            "starting_price": item.starting_price,
            "reserve_price": item.reserve_price,
            "current_price": item.current_price,
            "status": item.status.value,
            "images": item.images,
            "specifications": item.specifications,
            "provenance": item.provenance,
            "estimated_value": item.estimated_value,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "updated_at": item.updated_at.isoformat() if item.updated_at else None
        }

        if include_seller_details and hasattr(item, 'seller') and item.seller:
            item_dict["seller"] = {
                "id": item.seller.id,
                "full_name": item.seller.full_name,
                "email": item.seller.email
            }
        elif item.seller_id:
            item_dict["seller_id"] = item.seller_id

        return item_dict

    def _get_category_label(self, category: ItemCategory) -> str:
        """Get Vietnamese label for category"""
        labels = {
            ItemCategory.RING: "Nhẫn",
            ItemCategory.NECKLACE: "Dây chuyền",
            ItemCategory.EARRINGS: "Bông tai",
            ItemCategory.BRACELET: "Vòng tay",
            ItemCategory.WATCH: "Đồng hồ",
            ItemCategory.BROOCH: "Trâm cài",
            ItemCategory.PENDANT: "Mặt dây chuyền",
            ItemCategory.OTHER: "Khác"
        }
        return labels.get(category, category.value)