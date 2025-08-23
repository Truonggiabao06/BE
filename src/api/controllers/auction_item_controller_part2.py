    @cross_origin()
    @require_auth
    def update_item(self, item_id: int):
        """Update auction item"""
        try:
            data = request.get_json()
            current_user = get_current_user()
            
            if not data:
                return validation_error_response("Không có dữ liệu để cập nhật")
            
            # Get existing item
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                return error_response("Không tìm thấy sản phẩm", 404)
            
            # Check permissions
            if current_user.id != item.seller_id and current_user.role != UserRole.ADMIN:
                return error_response("Không có quyền chỉnh sửa sản phẩm này", 403)
            
            # Check if item can be updated
            if item.status not in [ItemStatus.PENDING, ItemStatus.REJECTED]:
                return error_response("Chỉ có thể chỉnh sửa sản phẩm đang chờ duyệt hoặc bị từ chối", 400)
            
            # Update allowed fields
            updatable_fields = ['title', 'description', 'category', 'condition', 'starting_price', 
                              'reserve_price', 'images', 'specifications', 'provenance', 'estimated_value']
            
            for field in updatable_fields:
                if field in data:
                    if field == 'category':
                        try:
                            setattr(item, field, ItemCategory(data[field]))
                        except ValueError:
                            return validation_error_response(f"Invalid category: {data[field]}")
                    elif field == 'condition':
                        try:
                            setattr(item, field, ItemCondition(data[field]))
                        except ValueError:
                            return validation_error_response(f"Invalid condition: {data[field]}")
                    elif field in ['starting_price', 'reserve_price', 'estimated_value']:
                        try:
                            value = float(data[field]) if data[field] is not None else None
                            if field in ['starting_price', 'reserve_price'] and value is not None and value <= 0:
                                return validation_error_response(f"{field} phải lớn hơn 0")
                            setattr(item, field, value)
                        except ValueError:
                            return validation_error_response(f"Invalid {field}: {data[field]}")
                    else:
                        setattr(item, field, data[field])
            
            # Reset status to pending if it was rejected
            if item.status == ItemStatus.REJECTED:
                item.status = ItemStatus.PENDING
            
            # Update in database
            updated_item = self.auction_item_repo.update(item)
            
            return success_response(
                message="Cập nhật sản phẩm thành công",
                data={
                    "item": self._item_to_dict(updated_item)
                }
            )
            
        except Exception as e:
            logger.error(f"Update item error: {str(e)}")
            return error_response("Lỗi hệ thống khi cập nhật sản phẩm", 500)
    
    @cross_origin()
    @require_auth
    def delete_item(self, item_id: int):
        """Delete auction item"""
        try:
            current_user = get_current_user()
            
            # Get existing item
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                return error_response("Không tìm thấy sản phẩm", 404)
            
            # Check permissions
            if current_user.id != item.seller_id and current_user.role != UserRole.ADMIN:
                return error_response("Không có quyền xóa sản phẩm này", 403)
            
            # Check if item can be deleted
            if item.status in [ItemStatus.ACTIVE, ItemStatus.SOLD]:
                return error_response("Không thể xóa sản phẩm đang đấu giá hoặc đã bán", 400)
            
            # Delete from database
            self.auction_item_repo.delete(item_id)
            
            return success_response("Xóa sản phẩm thành công")
            
        except Exception as e:
            logger.error(f"Delete item error: {str(e)}")
            return error_response("Lỗi hệ thống khi xóa sản phẩm", 500)
    
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
            ItemCategory.EARRING: "Bông tai",
            ItemCategory.BRACELET: "Vòng tay",
            ItemCategory.WATCH: "Đồng hồ",
            ItemCategory.BROOCH: "Trâm cài",
            ItemCategory.PENDANT: "Mặt dây chuyền",
            ItemCategory.CUFFLINK: "Khuy măng sét",
            ItemCategory.OTHER: "Khác"
        }
        return labels.get(category, category.value)
