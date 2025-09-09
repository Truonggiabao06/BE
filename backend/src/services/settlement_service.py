"""
Settlement service for the Jewelry Auction System
Handles the settlement process after auction sessions close
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from domain.entities.payment import Payment
from domain.entities.payout import Payout
from domain.enums import (
    SessionStatus, PaymentStatus, PayoutStatus, 
    JewelryStatus, BidStatus, PaymentMethod
)
from domain.exceptions import (
    ValidationError, 
    NotFoundError, 
    BusinessRuleViolationError,
    AuthorizationError
)
from domain.repositories.base_repository import (
    IAuctionSessionRepository,
    ISessionItemRepository,
    IBidRepository,
    IPaymentRepository,
    IPayoutRepository,
    IJewelryItemRepository,
    ITransactionFeeRepository
)
from infrastructure.databases.mssql import get_db_session
from sqlalchemy import text
import uuid


class SettlementService:
    """Settlement service for auction sessions"""
    
    def __init__(self, 
                 session_repository: IAuctionSessionRepository,
                 session_item_repository: ISessionItemRepository,
                 bid_repository: IBidRepository,
                 payment_repository: IPaymentRepository,
                 payout_repository: IPayoutRepository,
                 jewelry_repository: IJewelryItemRepository,
                 fee_repository: ITransactionFeeRepository):
        self.session_repository = session_repository
        self.session_item_repository = session_item_repository
        self.bid_repository = bid_repository
        self.payment_repository = payment_repository
        self.payout_repository = payout_repository
        self.jewelry_repository = jewelry_repository
        self.fee_repository = fee_repository
    
    def settle_session(self, session_id: str, user_role: str) -> Dict[str, Any]:
        """Settle an auction session after it closes"""
        from domain.enums import UserRole
        
        # Only staff and above can settle sessions
        if user_role not in [UserRole.STAFF, UserRole.MANAGER, UserRole.ADMIN]:
            raise AuthorizationError("Not authorized to settle sessions")
        
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")
        
        if session.status != SessionStatus.CLOSED:
            raise BusinessRuleViolationError("Can only settle closed sessions")
        
        try:
            db_session = get_db_session()
            
            # Get all session items
            session_items = self.session_item_repository.get_by_session_id(session_id)
            
            settlement_results = []
            
            for session_item in session_items:
                result = self._settle_session_item(session_item, session)
                settlement_results.append(result)
            
            # Update session status to settled
            session.status = SessionStatus.SETTLED
            session.settled_at = datetime.utcnow()
            session.updated_at = datetime.utcnow()
            
            self.session_repository.update(session)
            db_session.commit()
            
            return {
                'session_id': session_id,
                'settled_at': session.settled_at.isoformat(),
                'items_settled': len(settlement_results),
                'results': settlement_results
            }
            
        except Exception as e:
            db_session.rollback()
            raise e
    
    def _settle_session_item(self, session_item, session) -> Dict[str, Any]:
        """Settle individual session item"""
        result = {
            'session_item_id': session_item.id,
            'lot_number': session_item.lot_number,
            'jewelry_item_id': session_item.jewelry_item_id,
            'reserve_met': False,
            'sold': False,
            'winning_bid': None,
            'winner_id': None,
            'payment_created': False,
            'payout_created': False
        }
        
        # Check if there are any bids
        if session_item.bid_count == 0:
            # No bids - mark as unsold
            self._mark_jewelry_unsold(session_item.jewelry_item_id)
            result['status'] = 'no_bids'
            return result
        
        # Check if reserve price was met
        reserve_met = True
        if session_item.reserve_price and session_item.current_highest_bid < session_item.reserve_price:
            reserve_met = False
            self._mark_jewelry_unsold(session_item.jewelry_item_id)
            result['status'] = 'reserve_not_met'
            result['reserve_price'] = float(session_item.reserve_price)
            result['highest_bid'] = float(session_item.current_highest_bid)
            return result
        
        # Reserve met - item is sold
        result['reserve_met'] = True
        result['sold'] = True
        result['winning_bid'] = float(session_item.current_highest_bid)
        result['winner_id'] = session_item.current_winner_id
        
        # Mark winning bid
        self._mark_winning_bid(session_item.id, session_item.current_winner_id)
        
        # Mark jewelry as sold
        self._mark_jewelry_sold(session_item.jewelry_item_id)
        
        # Create payment for buyer
        payment = self._create_buyer_payment(session_item, session)
        if payment:
            result['payment_created'] = True
            result['payment_id'] = payment.id
            result['payment_amount'] = float(payment.amount)
        
        # Create payout for seller
        payout = self._create_seller_payout(session_item, session)
        if payout:
            result['payout_created'] = True
            result['payout_id'] = payout.id
            result['payout_amount'] = float(payout.amount)
        
        result['status'] = 'settled'
        return result
    
    def _mark_winning_bid(self, session_item_id: str, winner_id: str):
        """Mark the winning bid"""
        # Mark the highest bid as winning
        winning_bid = self.bid_repository.get_highest_bid_for_item(session_item_id)
        if winning_bid and winning_bid.bidder_id == winner_id:
            winning_bid.status = BidStatus.WINNING
            self.bid_repository.update(winning_bid)
    
    def _mark_jewelry_sold(self, jewelry_item_id: str):
        """Mark jewelry item as sold"""
        jewelry_item = self.jewelry_repository.get_by_id(jewelry_item_id)
        if jewelry_item:
            jewelry_item.status = JewelryStatus.SOLD
            jewelry_item.updated_at = datetime.utcnow()
            self.jewelry_repository.update(jewelry_item)
    
    def _mark_jewelry_unsold(self, jewelry_item_id: str):
        """Mark jewelry item as unsold"""
        jewelry_item = self.jewelry_repository.get_by_id(jewelry_item_id)
        if jewelry_item:
            jewelry_item.status = JewelryStatus.UNSOLD
            jewelry_item.updated_at = datetime.utcnow()
            self.jewelry_repository.update(jewelry_item)
    
    def _create_buyer_payment(self, session_item, session) -> Optional[Payment]:
        """Create payment record for buyer"""
        # Check if payment already exists
        existing_payment = self.payment_repository.get_by_session_item_id(session_item.id)
        if existing_payment:
            return existing_payment
        
        # Calculate fees
        winning_bid = session_item.current_highest_bid
        buyer_fee = self._calculate_buyer_fee(winning_bid, session.rules)
        total_amount = winning_bid + buyer_fee
        
        # Create payment
        payment = Payment(
            buyer_id=session_item.current_winner_id,
            session_item_id=session_item.id,
            amount=total_amount,
            method=PaymentMethod.CREDIT_CARD,  # Default - will be updated when payment is made
            status=PaymentStatus.PENDING,
            meta={
                'winning_bid': float(winning_bid),
                'buyer_fee': float(buyer_fee),
                'fee_percentage': self._get_buyer_fee_percentage(session.rules),
                'settlement_date': datetime.utcnow().isoformat()
            }
        )
        
        created_payment = self.payment_repository.create(payment)
        return created_payment
    
    def _create_seller_payout(self, session_item, session) -> Optional[Payout]:
        """Create payout record for seller"""
        # Get jewelry item to find seller
        jewelry_item = self.jewelry_repository.get_by_id(session_item.jewelry_item_id)
        if not jewelry_item:
            return None
        
        # Check if payout already exists
        existing_payout = self.payout_repository.get_by_session_item_id(session_item.id)
        if existing_payout:
            return existing_payout
        
        # Calculate payout amount
        winning_bid = session_item.current_highest_bid
        seller_fee = self._calculate_seller_fee(winning_bid, session.rules)
        payout_amount = winning_bid - seller_fee
        
        # Create payout
        payout = Payout(
            seller_id=jewelry_item.owner_user_id,
            session_item_id=session_item.id,
            amount=payout_amount,
            status=PayoutStatus.PENDING,
            meta={
                'winning_bid': float(winning_bid),
                'seller_fee': float(seller_fee),
                'fee_percentage': self._get_seller_fee_percentage(session.rules),
                'settlement_date': datetime.utcnow().isoformat()
            }
        )
        
        created_payout = self.payout_repository.create(payout)
        return created_payout
    
    def _calculate_buyer_fee(self, amount: Decimal, session_rules: Dict[str, Any]) -> Decimal:
        """Calculate buyer fee based on session rules or default fees"""
        # Try to get from session rules first
        if 'buyer_fee_percentage' in session_rules:
            fee_percentage = Decimal(str(session_rules['buyer_fee_percentage']))
        else:
            # Get default fee from database
            default_fee = self.fee_repository.get_active_fee()
            fee_percentage = default_fee.buyer_percentage if default_fee else Decimal('10.0')
        
        min_fee = Decimal(str(session_rules.get('buyer_min_fee', 5.0)))
        max_fee = session_rules.get('buyer_max_fee')
        max_fee = Decimal(str(max_fee)) if max_fee else None
        
        fee = amount * (fee_percentage / 100)
        
        if fee < min_fee:
            fee = min_fee
        
        if max_fee and fee > max_fee:
            fee = max_fee
        
        return fee
    
    def _calculate_seller_fee(self, amount: Decimal, session_rules: Dict[str, Any]) -> Decimal:
        """Calculate seller fee based on session rules or default fees"""
        # Try to get from session rules first
        if 'seller_fee_percentage' in session_rules:
            fee_percentage = Decimal(str(session_rules['seller_fee_percentage']))
        else:
            # Get default fee from database
            default_fee = self.fee_repository.get_active_fee()
            fee_percentage = default_fee.seller_percentage if default_fee else Decimal('15.0')
        
        min_fee = Decimal(str(session_rules.get('seller_min_fee', 10.0)))
        max_fee = session_rules.get('seller_max_fee')
        max_fee = Decimal(str(max_fee)) if max_fee else None
        
        fee = amount * (fee_percentage / 100)
        
        if fee < min_fee:
            fee = min_fee
        
        if max_fee and fee > max_fee:
            fee = max_fee
        
        return fee
    
    def _get_buyer_fee_percentage(self, session_rules: Dict[str, Any]) -> float:
        """Get buyer fee percentage"""
        return float(session_rules.get('buyer_fee_percentage', 10.0))
    
    def _get_seller_fee_percentage(self, session_rules: Dict[str, Any]) -> float:
        """Get seller fee percentage"""
        return float(session_rules.get('seller_fee_percentage', 15.0))
    
    def get_settlement_summary(self, session_id: str) -> Dict[str, Any]:
        """Get settlement summary for a session"""
        session = self.session_repository.get_by_id(session_id)
        if not session:
            raise NotFoundError("Auction session not found")
        
        session_items = self.session_item_repository.get_by_session_id(session_id)
        payments = self.payment_repository.get_by_session_id(session_id)
        payouts = self.payout_repository.get_by_session_id(session_id)
        
        total_sales = sum(float(item.current_highest_bid or 0) for item in session_items if item.current_highest_bid)
        items_sold = len([item for item in session_items if item.current_highest_bid and 
                         (not item.reserve_price or item.current_highest_bid >= item.reserve_price)])
        
        return {
            'session_id': session_id,
            'session_code': session.code,
            'status': session.status.value,
            'settled_at': session.settled_at.isoformat() if session.settled_at else None,
            'total_items': len(session_items),
            'items_sold': items_sold,
            'items_unsold': len(session_items) - items_sold,
            'total_sales_value': total_sales,
            'total_payments': len(payments),
            'total_payouts': len(payouts),
            'pending_payments': len([p for p in payments if p.status == PaymentStatus.PENDING]),
            'pending_payouts': len([p for p in payouts if p.status == PayoutStatus.PENDING])
        }
