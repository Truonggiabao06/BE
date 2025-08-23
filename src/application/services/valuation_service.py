"""
Valuation Service - Business logic for item valuation workflow
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from decimal import Decimal

from src.domain.models.auction_item import AuctionItem, ItemStatus
from src.domain.models.user import User, UserRole
from src.domain.models.notification import Notification, NotificationType
from src.domain.repositories.auction_item_repo import IAuctionItemRepository
from src.domain.repositories.notification_repo import INotificationRepository
from src.infrastructure.services.mock_email_service import MockEmailService

logger = logging.getLogger(__name__)

class ValuationService:
    """Service for item valuation business logic"""
    
    def __init__(self, 
                 auction_item_repo: IAuctionItemRepository,
                 notification_repo: INotificationRepository,
                 email_service: MockEmailService):
        self.auction_item_repo = auction_item_repo
        self.notification_repo = notification_repo
        self.email_service = email_service
        
        # Valuation thresholds
        self.HIGH_VALUE_THRESHOLD = Decimal('50000000')  # 50 million VND
        self.MANAGER_APPROVAL_THRESHOLD = Decimal('100000000')  # 100 million VND

    def submit_item_for_valuation(self, item: AuctionItem, seller: User) -> AuctionItem:
        """Submit item for initial valuation"""
        try:
            if item.status != ItemStatus.PENDING_APPROVAL:
                raise ValueError("Item must be in pending approval status")
            
            # Save item
            created_item = self.auction_item_repo.create(item)
            
            # Create notification for staff
            notification = Notification.create_item_submitted_notification(
                recipient_id=1,  # TODO: Get staff user ID
                item_id=created_item.id,
                item_title=created_item.title
            )
            self.notification_repo.create(notification)
            
            # Send email notification
            self.email_service.send_item_submitted_notification(seller.email, created_item.title)
            
            logger.info(f"Item {created_item.id} submitted for valuation by user {seller.id}")
            return created_item
            
        except Exception as e:
            logger.error(f"Error submitting item for valuation: {str(e)}")
            raise

    def set_preliminary_valuation(self, item_id: int, staff: User, preliminary_price: Decimal, notes: Optional[str] = None) -> AuctionItem:
        """Set preliminary valuation by staff"""
        try:
            if not staff.is_staff:
                raise ValueError("Only staff members can set preliminary valuation")
            
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                raise ValueError("Item not found")
            
            # Set preliminary valuation
            item.set_preliminary_valuation(staff.id, preliminary_price, notes)
            
            # Update in database
            updated_item = self.auction_item_repo.update(item)
            
            # Create notification for seller
            notification = Notification.create_preliminary_valuation_notification(
                recipient_id=item.seller_id,
                item_id=item.id,
                item_title=item.title,
                price=float(preliminary_price)
            )
            self.notification_repo.create(notification)
            
            # Send email to seller
            # TODO: Get seller email and send notification
            
            logger.info(f"Preliminary valuation set for item {item_id} by staff {staff.id}: {preliminary_price}")
            return updated_item
            
        except Exception as e:
            logger.error(f"Error setting preliminary valuation: {str(e)}")
            raise

    def confirm_item_received(self, item_id: int, staff: User) -> AuctionItem:
        """Confirm that physical item has been received"""
        try:
            if not staff.is_staff:
                raise ValueError("Only staff members can confirm item receipt")
            
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                raise ValueError("Item not found")
            
            # Confirm item received
            item.confirm_item_received(staff.id)
            
            # Update in database
            updated_item = self.auction_item_repo.update(item)
            
            logger.info(f"Item {item_id} confirmed received by staff {staff.id}")
            return updated_item
            
        except Exception as e:
            logger.error(f"Error confirming item received: {str(e)}")
            raise

    def set_final_valuation(self, item_id: int, staff: User, final_price: Decimal, starting_price: Decimal, notes: Optional[str] = None) -> Dict[str, Any]:
        """Set final valuation by staff after receiving item"""
        try:
            if not staff.is_staff:
                raise ValueError("Only staff members can set final valuation")
            
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                raise ValueError("Item not found")
            
            # Validate prices
            if starting_price > final_price:
                raise ValueError("Starting price cannot be higher than final valuation")
            
            # Set final valuation
            item.set_final_valuation(staff.id, final_price, starting_price, notes)
            
            # Check if manager approval is needed
            needs_approval = final_price >= self.MANAGER_APPROVAL_THRESHOLD
            
            if needs_approval:
                item.submit_for_manager_approval()
                
                # Create notification for manager
                notification = Notification.create_manager_approval_notification(
                    recipient_id=1,  # TODO: Get manager user ID
                    item_id=item.id,
                    item_title=item.title
                )
                self.notification_repo.create(notification)
            
            # Update in database
            updated_item = self.auction_item_repo.update(item)
            
            result = {
                "item": updated_item,
                "needs_manager_approval": needs_approval,
                "threshold_amount": float(self.MANAGER_APPROVAL_THRESHOLD)
            }
            
            logger.info(f"Final valuation set for item {item_id} by staff {staff.id}: {final_price}, needs approval: {needs_approval}")
            return result
            
        except Exception as e:
            logger.error(f"Error setting final valuation: {str(e)}")
            raise

    def manager_approve_valuation(self, item_id: int, manager: User, notes: Optional[str] = None) -> AuctionItem:
        """Manager approves the final valuation"""
        try:
            if manager.role not in [UserRole.MANAGER, UserRole.ADMIN]:
                raise ValueError("Only managers can approve valuations")
            
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                raise ValueError("Item not found")
            
            # Manager approve
            item.manager_approve(manager.id, notes)
            
            # Update in database
            updated_item = self.auction_item_repo.update(item)
            
            # Create notification for seller
            notification = Notification.create_item_approved_notification(
                recipient_id=item.seller_id,
                item_id=item.id,
                item_title=item.title,
                final_price=float(item.starting_price)
            )
            self.notification_repo.create(notification)
            
            logger.info(f"Item {item_id} approved by manager {manager.id}")
            return updated_item
            
        except Exception as e:
            logger.error(f"Error approving valuation: {str(e)}")
            raise

    def manager_reject_valuation(self, item_id: int, manager: User, reason: str) -> AuctionItem:
        """Manager rejects the valuation"""
        try:
            if manager.role not in [UserRole.MANAGER, UserRole.ADMIN]:
                raise ValueError("Only managers can reject valuations")
            
            item = self.auction_item_repo.get_by_id(item_id)
            if not item:
                raise ValueError("Item not found")
            
            # Manager reject
            item.manager_reject(manager.id, reason)
            
            # Update in database
            updated_item = self.auction_item_repo.update(item)
            
            # TODO: Create notification for seller about rejection
            
            logger.info(f"Item {item_id} rejected by manager {manager.id}: {reason}")
            return updated_item
            
        except Exception as e:
            logger.error(f"Error rejecting valuation: {str(e)}")
            raise

    def get_items_pending_approval(self, page: int = 1, limit: int = 20) -> List[AuctionItem]:
        """Get items pending approval"""
        try:
            return self.auction_item_repo.get_by_status(ItemStatus.PENDING_APPROVAL, page, limit)
        except Exception as e:
            logger.error(f"Error getting items pending approval: {str(e)}")
            raise

    def get_items_pending_manager_approval(self, page: int = 1, limit: int = 20) -> List[AuctionItem]:
        """Get items pending manager approval"""
        try:
            return self.auction_item_repo.get_by_status(ItemStatus.PENDING_MANAGER_APPROVAL, page, limit)
        except Exception as e:
            logger.error(f"Error getting items pending manager approval: {str(e)}")
            raise

    def get_staff_assignments(self, staff_id: int, page: int = 1, limit: int = 20) -> List[AuctionItem]:
        """Get items assigned to a staff member"""
        try:
            return self.auction_item_repo.get_by_staff_assignment(staff_id, page, limit)
        except Exception as e:
            logger.error(f"Error getting staff assignments: {str(e)}")
            raise

    def get_valuation_statistics(self) -> Dict[str, Any]:
        """Get valuation workflow statistics"""
        try:
            stats = {}
            for status in [ItemStatus.PENDING_APPROVAL, ItemStatus.PRELIMINARY_VALUED, 
                          ItemStatus.AWAITING_ITEM, ItemStatus.ITEM_RECEIVED, 
                          ItemStatus.FINAL_VALUED, ItemStatus.PENDING_MANAGER_APPROVAL,
                          ItemStatus.APPROVED, ItemStatus.REJECTED]:
                stats[status.value] = self.auction_item_repo.count_by_status(status)
            
            return {
                "status_counts": stats,
                "total_items": sum(stats.values()),
                "approval_rate": stats.get('approved', 0) / max(sum(stats.values()), 1) * 100
            }
            
        except Exception as e:
            logger.error(f"Error getting valuation statistics: {str(e)}")
            raise
