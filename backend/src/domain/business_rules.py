"""
Business rules for the Jewelry Auction System
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List
from domain.enums import SessionStatus, BidStatus, UserRole, SellRequestStatus, JewelryStatus


class AuctionRules:
    """Business rules for auction operations"""
    
    @staticmethod
    def can_place_bid(
        session_status: SessionStatus,
        bidder_role: UserRole,
        bid_amount: Decimal,
        current_highest: Decimal,
        step_price: Decimal,
        reserve_price: Optional[Decimal] = None
    ) -> tuple[bool, str]:
        """
        Validate if a bid can be placed
        Returns (is_valid, error_message)
        """
        # Session must be open
        if session_status != SessionStatus.OPEN:
            return False, "Auction session is not open for bidding"
        
        # User must have bidding privileges
        if bidder_role not in [UserRole.MEMBER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            return False, "User does not have bidding privileges"
        
        # Bid must be higher than current highest + step price
        minimum_bid = current_highest + step_price
        if bid_amount < minimum_bid:
            return False, f"Bid must be at least {minimum_bid}"
        
        # Bid must meet reserve price if set
        if reserve_price and bid_amount < reserve_price:
            return False, f"Bid must meet reserve price of {reserve_price}"
        
        return True, ""
    
    @staticmethod
    def can_start_session(
        session_status: SessionStatus,
        start_time: datetime,
        has_items: bool
    ) -> tuple[bool, str]:
        """
        Validate if an auction session can be started
        """
        if session_status != SessionStatus.SCHEDULED:
            return False, "Session must be scheduled to start"
        
        if not has_items:
            return False, "Session must have at least one item to start"
        
        if start_time > datetime.utcnow() + timedelta(minutes=5):
            return False, "Cannot start session more than 5 minutes before scheduled time"
        
        return True, ""
    
    @staticmethod
    def can_close_session(
        session_status: SessionStatus,
        end_time: Optional[datetime] = None
    ) -> tuple[bool, str]:
        """
        Validate if an auction session can be closed
        """
        if session_status not in [SessionStatus.OPEN, SessionStatus.PAUSED]:
            return False, "Can only close open or paused sessions"
        
        if end_time and datetime.utcnow() < end_time:
            return False, "Cannot close session before scheduled end time"
        
        return True, ""


class BiddingRules:
    """Business rules for bidding operations"""

    @staticmethod
    def validate_bid_amount(
        bid_amount: Decimal,
        current_price: Decimal,
        bid_increment: Decimal,
        reserve_price: Optional[Decimal] = None
    ) -> tuple[bool, str]:
        """
        Validate bid amount against current price and increment
        """
        minimum_bid = current_price + bid_increment

        if bid_amount < minimum_bid:
            return False, f"Bid must be at least {minimum_bid}"

        if reserve_price and bid_amount < reserve_price:
            return False, f"Bid must meet reserve price of {reserve_price}"

        return True, ""

    @staticmethod
    def can_user_bid(
        user_role: UserRole,
        is_enrolled: bool,
        deposit_paid: bool = True
    ) -> tuple[bool, str]:
        """
        Validate if user can place bids
        """
        if user_role not in [UserRole.MEMBER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            return False, "User does not have bidding privileges"

        if not is_enrolled:
            return False, "User must be enrolled in the auction session"

        if not deposit_paid:
            return False, "Required deposit must be paid before bidding"

        return True, ""

    @staticmethod
    def calculate_bid_increment(current_price: Decimal) -> Decimal:
        """
        Calculate appropriate bid increment based on current price
        """
        if current_price < Decimal('100'):
            return Decimal('5')
        elif current_price < Decimal('500'):
            return Decimal('10')
        elif current_price < Decimal('1000'):
            return Decimal('25')
        elif current_price < Decimal('5000'):
            return Decimal('50')
        elif current_price < Decimal('10000'):
            return Decimal('100')
        else:
            return Decimal('250')


class SellRequestRules:
    """Business rules for sell request operations"""
    
    @staticmethod
    def can_submit_sell_request(
        seller_role: UserRole,
        jewelry_title: str,
        jewelry_description: str,
        photos: List[str]
    ) -> tuple[bool, str]:
        """
        Validate if a sell request can be submitted
        """
        if seller_role not in [UserRole.MEMBER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            return False, "User does not have selling privileges"
        
        if not jewelry_title.strip():
            return False, "Jewelry title is required"
        
        if not jewelry_description.strip():
            return False, "Jewelry description is required"
        
        if len(photos) == 0:
            return False, "At least one photo is required"
        
        if len(jewelry_title) > 200:
            return False, "Jewelry title must be less than 200 characters"
        
        if len(jewelry_description) > 2000:
            return False, "Jewelry description must be less than 2000 characters"
        
        return True, ""
    
    @staticmethod
    def can_approve_sell_request(
        approver_role: UserRole,
        request_status: SellRequestStatus,
        estimated_price: Optional[Decimal] = None
    ) -> tuple[bool, str]:
        """
        Validate if a sell request can be approved
        """
        if approver_role not in [UserRole.MANAGER, UserRole.ADMIN]:
            return False, "Only managers and admins can approve sell requests"
        
        if request_status != SellRequestStatus.FINAL_APPRAISED:
            return False, "Request must be finally appraised before approval"
        
        if not estimated_price or estimated_price <= 0:
            return False, "Valid estimated price is required for approval"
        
        return True, ""


class PaymentRules:
    """Business rules for payment operations"""
    
    @staticmethod
    def calculate_buyer_total(
        winning_bid: Decimal,
        buyer_fee_percentage: Decimal,
        min_fee: Decimal,
        max_fee: Optional[Decimal] = None
    ) -> Decimal:
        """
        Calculate total amount buyer needs to pay including fees
        """
        fee = winning_bid * (buyer_fee_percentage / 100)
        
        # Apply minimum fee
        if fee < min_fee:
            fee = min_fee
        
        # Apply maximum fee if set
        if max_fee and fee > max_fee:
            fee = max_fee
        
        return winning_bid + fee
    
    @staticmethod
    def calculate_seller_payout(
        winning_bid: Decimal,
        seller_fee_percentage: Decimal,
        min_fee: Decimal,
        max_fee: Optional[Decimal] = None
    ) -> Decimal:
        """
        Calculate amount to pay out to seller after fees
        """
        fee = winning_bid * (seller_fee_percentage / 100)
        
        # Apply minimum fee
        if fee < min_fee:
            fee = min_fee
        
        # Apply maximum fee if set
        if max_fee and fee > max_fee:
            fee = max_fee
        
        return winning_bid - fee
    
    @staticmethod
    def can_process_payment(
        payment_amount: Decimal,
        expected_amount: Decimal,
        tolerance: Decimal = Decimal('0.01')
    ) -> tuple[bool, str]:
        """
        Validate if payment can be processed
        """
        if abs(payment_amount - expected_amount) > tolerance:
            return False, f"Payment amount {payment_amount} does not match expected amount {expected_amount}"
        
        if payment_amount <= 0:
            return False, "Payment amount must be positive"
        
        return True, ""


class UserRules:
    """Business rules for user operations"""
    
    @staticmethod
    def can_change_role(
        changer_role: UserRole,
        target_current_role: UserRole,
        target_new_role: UserRole
    ) -> tuple[bool, str]:
        """
        Validate if user role can be changed
        """
        # Only admins can change roles
        if changer_role != UserRole.ADMIN:
            return False, "Only admins can change user roles"
        
        # Cannot change admin role (except by another admin)
        if target_current_role == UserRole.ADMIN and changer_role != UserRole.ADMIN:
            return False, "Cannot change admin role"
        
        # Valid role transition
        valid_roles = [UserRole.GUEST, UserRole.MEMBER, UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]
        if target_new_role not in valid_roles:
            return False, "Invalid target role"
        
        return True, ""
    
    @staticmethod
    def can_deactivate_user(
        deactivator_role: UserRole,
        target_role: UserRole
    ) -> tuple[bool, str]:
        """
        Validate if user can be deactivated
        """
        # Staff and above can deactivate members
        if deactivator_role in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            if target_role == UserRole.MEMBER:
                return True, ""
        
        # Managers can deactivate staff
        if deactivator_role in [UserRole.MANAGER, UserRole.ADMIN]:
            if target_role == UserRole.STAFF:
                return True, ""
        
        # Only admins can deactivate managers
        if deactivator_role == UserRole.ADMIN:
            if target_role == UserRole.MANAGER:
                return True, ""
        
        return False, "Insufficient privileges to deactivate this user"


class JewelryRules:
    """Business rules for jewelry operations"""
    
    @staticmethod
    def can_assign_to_session(
        jewelry_status: JewelryStatus,
        session_status: SessionStatus
    ) -> tuple[bool, str]:
        """
        Validate if jewelry can be assigned to auction session
        """
        if jewelry_status != JewelryStatus.APPROVED:
            return False, "Jewelry must be approved before assignment to session"
        
        if session_status not in [SessionStatus.DRAFT, SessionStatus.SCHEDULED]:
            return False, "Can only assign jewelry to draft or scheduled sessions"
        
        return True, ""
    
    @staticmethod
    def validate_jewelry_attributes(attributes: dict) -> tuple[bool, str]:
        """
        Validate jewelry attributes
        """
        required_fields = ['material', 'weight', 'condition']
        
        for field in required_fields:
            if field not in attributes or not attributes[field]:
                return False, f"Required field '{field}' is missing"
        
        # Validate weight is positive number
        try:
            weight = float(attributes['weight'])
            if weight <= 0:
                return False, "Weight must be a positive number"
        except (ValueError, TypeError):
            return False, "Weight must be a valid number"
        
        return True, ""
