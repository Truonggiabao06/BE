from datetime import datetime
from typing import Optional, List
from enum import Enum
from decimal import Decimal

class ItemCategory(Enum):
    """Categories for jewelry items"""
    RING = "ring"
    NECKLACE = "necklace"
    BRACELET = "bracelet"
    EARRINGS = "earrings"
    WATCH = "watch"
    BROOCH = "brooch"
    PENDANT = "pendant"
    OTHER = "other"

class ItemCondition(Enum):
    """Condition of jewelry items"""
    NEW = "new"
    EXCELLENT = "excellent"
    VERY_GOOD = "very_good"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class ItemStatus(Enum):
    """Status of auction items throughout the process"""
    PENDING_APPROVAL = "pending_approval"          # Chờ duyệt
    PRELIMINARY_VALUED = "preliminary_valued"      # Đã định giá sơ bộ
    AWAITING_ITEM = "awaiting_item"               # Chờ nhận trang sức
    ITEM_RECEIVED = "item_received"               # Đã nhận trang sức
    FINAL_VALUED = "final_valued"                 # Đã định giá cuối cùng
    PENDING_MANAGER_APPROVAL = "pending_manager_approval"  # Chờ manager phê duyệt
    APPROVED = "approved"                         # Sẵn sàng đấu giá
    ON_AUCTION = "on_auction"                    # Đang đấu giá
    SOLD_PENDING_PAYMENT = "sold_pending_payment"  # Chờ thanh toán
    SOLD_PENDING_DELIVERY = "sold_pending_delivery"  # Chờ bàn giao
    COMPLETED = "completed"                      # Đã hoàn tất
    UNSOLD = "unsold"                           # Không bán được
    REJECTED = "rejected"                       # Bị từ chối
    CANCELLED = "cancelled"                     # Đã hủy

class AuctionItem:
    """Domain model for auction items (jewelry)"""

    def __init__(
        self,
        id: Optional[int] = None,
        seller_id: int = None,
        title: str = "",
        description: str = "",
        category: ItemCategory = ItemCategory.OTHER,
        condition: ItemCondition = ItemCondition.GOOD,
        material: str = "",  # e.g., "Gold 18K", "Silver 925", "Diamond"
        weight: Optional[float] = None,  # in grams
        dimensions: Optional[str] = None,  # e.g., "2.5cm x 1.8cm"
        brand: Optional[str] = None,
        year_made: Optional[int] = None,
        certificate_number: Optional[str] = None,
        images: Optional[List[str]] = None,  # List of image URLs
        starting_price: Decimal = Decimal('0.00'),
        reserve_price: Optional[Decimal] = None,  # Minimum price to sell
        estimated_value: Optional[Decimal] = None,  # Appraised value
        status: ItemStatus = ItemStatus.PENDING_APPROVAL,
        staff_notes: Optional[str] = None,  # Internal notes from staff
        rejection_reason: Optional[str] = None,
        # New fields for pricing workflow
        preliminary_price: Optional[Decimal] = None,  # Định giá sơ bộ
        final_price: Optional[Decimal] = None,        # Định giá cuối cùng
        preliminary_valued_by: Optional[int] = None,   # Staff ID who did preliminary valuation
        preliminary_valued_at: Optional[datetime] = None,
        final_valued_by: Optional[int] = None,        # Staff ID who did final valuation
        final_valued_at: Optional[datetime] = None,
        item_received_by: Optional[int] = None,       # Staff ID who received the item
        item_received_at: Optional[datetime] = None,
        manager_notes: Optional[str] = None,          # Manager's notes
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        approved_at: Optional[datetime] = None,
        approved_by: Optional[int] = None  # Staff/Manager ID who approved
    ):
        self.id = id
        self.seller_id = seller_id
        self.title = title
        self.description = description
        self.category = category
        self.condition = condition
        self.material = material
        self.weight = weight
        self.dimensions = dimensions
        self.brand = brand
        self.year_made = year_made
        self.certificate_number = certificate_number
        self.images = images or []
        self.starting_price = starting_price
        self.reserve_price = reserve_price
        self.estimated_value = estimated_value
        self.status = status
        self.staff_notes = staff_notes
        self.rejection_reason = rejection_reason
        # New fields
        self.preliminary_price = preliminary_price
        self.final_price = final_price
        self.preliminary_valued_by = preliminary_valued_by
        self.preliminary_valued_at = preliminary_valued_at
        self.final_valued_by = final_valued_by
        self.final_valued_at = final_valued_at
        self.item_received_by = item_received_by
        self.item_received_at = item_received_at
        self.manager_notes = manager_notes
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.approved_at = approved_at
        self.approved_by = approved_by

    @property
    def is_pending_approval(self) -> bool:
        """Check if item is waiting for approval"""
        return self.status == ItemStatus.PENDING_APPROVAL

    @property
    def is_approved(self) -> bool:
        """Check if item is approved and ready for auction"""
        return self.status == ItemStatus.APPROVED

    @property
    def is_on_auction(self) -> bool:
        """Check if item is currently being auctioned"""
        return self.status == ItemStatus.ON_AUCTION

    @property
    def is_sold(self) -> bool:
        """Check if item has been sold"""
        return self.status in [
            ItemStatus.SOLD_PENDING_PAYMENT,
            ItemStatus.SOLD_PENDING_DELIVERY,
            ItemStatus.COMPLETED
        ]

    @property
    def has_reserve_price(self) -> bool:
        """Check if item has a reserve price"""
        return self.reserve_price is not None and self.reserve_price > 0

    def approve(self, staff_id: int, starting_price: Decimal, estimated_value: Optional[Decimal] = None):
        """Approve the item for auction"""
        self.status = ItemStatus.APPROVED
        self.starting_price = starting_price
        self.estimated_value = estimated_value
        self.approved_by = staff_id
        self.approved_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def reject(self, reason: str):
        """Reject the item with reason"""
        self.status = ItemStatus.REJECTED
        self.rejection_reason = reason
        self.updated_at = datetime.utcnow()

    def start_auction(self):
        """Mark item as being auctioned"""
        if self.status != ItemStatus.APPROVED:
            raise ValueError("Item must be approved before starting auction")
        self.status = ItemStatus.ON_AUCTION
        self.updated_at = datetime.utcnow()

    def mark_sold(self):
        """Mark item as sold, pending payment"""
        self.status = ItemStatus.SOLD_PENDING_PAYMENT
        self.updated_at = datetime.utcnow()

    def mark_payment_received(self):
        """Mark payment as received, pending delivery"""
        self.status = ItemStatus.SOLD_PENDING_DELIVERY
        self.updated_at = datetime.utcnow()

    def complete_sale(self):
        """Mark sale as completed"""
        self.status = ItemStatus.COMPLETED
        self.updated_at = datetime.utcnow()

    def mark_unsold(self):
        """Mark item as unsold after auction"""
        self.status = ItemStatus.UNSOLD
        self.updated_at = datetime.utcnow()

    def cancel(self):
        """Cancel the item listing"""
        if self.status == ItemStatus.ON_AUCTION:
            raise ValueError("Cannot cancel item that is currently being auctioned")
        self.status = ItemStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def set_preliminary_valuation(self, staff_id: int, preliminary_price: Decimal, notes: Optional[str] = None):
        """Set preliminary valuation by staff"""
        if self.status != ItemStatus.PENDING_APPROVAL:
            raise ValueError("Item must be pending approval for preliminary valuation")

        self.status = ItemStatus.PRELIMINARY_VALUED
        self.preliminary_price = preliminary_price
        self.preliminary_valued_by = staff_id
        self.preliminary_valued_at = datetime.utcnow()
        if notes:
            self.staff_notes = notes
        self.updated_at = datetime.utcnow()

    def confirm_item_received(self, staff_id: int):
        """Confirm that the physical item has been received"""
        if self.status != ItemStatus.PRELIMINARY_VALUED:
            raise ValueError("Item must be preliminary valued before receiving")

        self.status = ItemStatus.ITEM_RECEIVED
        self.item_received_by = staff_id
        self.item_received_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def set_final_valuation(self, staff_id: int, final_price: Decimal, starting_price: Decimal, notes: Optional[str] = None):
        """Set final valuation by staff after receiving item"""
        if self.status != ItemStatus.ITEM_RECEIVED:
            raise ValueError("Item must be received before final valuation")

        self.status = ItemStatus.FINAL_VALUED
        self.final_price = final_price
        self.starting_price = starting_price
        self.final_valued_by = staff_id
        self.final_valued_at = datetime.utcnow()
        if notes:
            self.staff_notes = notes
        self.updated_at = datetime.utcnow()

    def submit_for_manager_approval(self):
        """Submit item for manager approval"""
        if self.status != ItemStatus.FINAL_VALUED:
            raise ValueError("Item must be final valued before manager approval")

        self.status = ItemStatus.PENDING_MANAGER_APPROVAL
        self.updated_at = datetime.utcnow()

    def manager_approve(self, manager_id: int, notes: Optional[str] = None):
        """Manager approves the final valuation"""
        if self.status != ItemStatus.PENDING_MANAGER_APPROVAL:
            raise ValueError("Item must be pending manager approval")

        self.status = ItemStatus.APPROVED
        self.approved_by = manager_id
        self.approved_at = datetime.utcnow()
        if notes:
            self.manager_notes = notes
        self.updated_at = datetime.utcnow()

    def manager_reject(self, manager_id: int, reason: str):
        """Manager rejects the valuation"""
        if self.status != ItemStatus.PENDING_MANAGER_APPROVAL:
            raise ValueError("Item must be pending manager approval")

        self.status = ItemStatus.REJECTED
        self.rejection_reason = reason
        self.approved_by = manager_id
        if not self.manager_notes:
            self.manager_notes = reason
        self.updated_at = datetime.utcnow()

    def add_image(self, image_url: str):
        """Add an image to the item"""
        if image_url not in self.images:
            self.images.append(image_url)
            self.updated_at = datetime.utcnow()

    def remove_image(self, image_url: str):
        """Remove an image from the item"""
        if image_url in self.images:
            self.images.remove(image_url)
            self.updated_at = datetime.utcnow()

    def update_details(self, **kwargs):
        """Update item details"""
        allowed_fields = [
            'title', 'description', 'category', 'condition', 'material',
            'weight', 'dimensions', 'brand', 'year_made', 'certificate_number'
        ]
        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<AuctionItem(id={self.id}, title='{self.title}', status='{self.status.value}')>"