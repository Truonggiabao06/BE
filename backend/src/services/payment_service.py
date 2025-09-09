"""
Payment service for the Jewelry Auction System
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from domain.entities.payment import Payment
from domain.entities.payout import Payout
from domain.entities.refund import Refund
from domain.enums import PaymentStatus, PayoutStatus, PaymentMethod, SessionStatus
from domain.exceptions import (
    ValidationError, 
    NotFoundError, 
    BusinessRuleViolationError,
    AuthorizationError
)
from domain.business_rules import PaymentRules
from domain.repositories.base_repository import (
    IPaymentRepository,
    IPayoutRepository,
    IRefundRepository,
    ISessionItemRepository,
    IAuctionSessionRepository,
    ITransactionFeeRepository
)
from infrastructure.services.payment_gateway import PaymentGatewayService
import uuid


class PaymentService:
    """Payment processing service"""
    
    def __init__(self, 
                 payment_repository: IPaymentRepository,
                 payout_repository: IPayoutRepository,
                 refund_repository: IRefundRepository,
                 session_item_repository: ISessionItemRepository,
                 session_repository: IAuctionSessionRepository,
                 fee_repository: ITransactionFeeRepository):
        self.payment_repository = payment_repository
        self.payout_repository = payout_repository
        self.refund_repository = refund_repository
        self.session_item_repository = session_item_repository
        self.session_repository = session_repository
        self.fee_repository = fee_repository
        self.gateway = PaymentGatewayService()
    
    def create_payment(self, session_item_id: str, buyer_id: str, payment_method: PaymentMethod) -> Dict[str, Any]:
        """Create payment for winning bid"""
        session_item = self.session_item_repository.get_by_id(session_item_id)
        if not session_item:
            raise NotFoundError("Session item not found")
        
        # Check if buyer is the winner
        if session_item.current_winner_id != buyer_id:
            raise BusinessRuleViolationError("Only the winning bidder can make payment")
        
        # Check if session is closed
        session = self.session_repository.get_by_id(session_item.session_id)
        if session.status != SessionStatus.CLOSED:
            raise BusinessRuleViolationError("Payment can only be made after auction is closed")
        
        # Check if payment already exists
        existing_payment = self.payment_repository.get_by_session_item_id(session_item_id)
        if existing_payment:
            return self._payment_to_dict(existing_payment)
        
        # Calculate total amount including fees
        winning_bid = session_item.current_highest_bid
        buyer_fee = self._calculate_buyer_fee(winning_bid, session.rules)
        total_amount = winning_bid + buyer_fee
        
        # Create payment
        payment = Payment(
            buyer_id=buyer_id,
            session_item_id=session_item_id,
            amount=total_amount,
            method=payment_method,
            status=PaymentStatus.PENDING,
            meta={
                'winning_bid': float(winning_bid),
                'buyer_fee': float(buyer_fee),
                'fee_percentage': self._get_buyer_fee_percentage(session.rules)
            }
        )
        
        created_payment = self.payment_repository.create(payment)
        self.payment_repository.commit()
        
        return self._payment_to_dict(created_payment)
    
    def process_payment(self, payment_id: str, payment_details: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment through gateway"""
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise NotFoundError("Payment not found")
        
        if payment.status != PaymentStatus.PENDING:
            raise BusinessRuleViolationError("Payment is not in pending status")
        
        try:
            # Update status to processing
            payment.status = PaymentStatus.PROCESSING
            payment.updated_at = datetime.utcnow()
            self.payment_repository.update(payment)
            self.payment_repository.commit()
            
            # Process through gateway
            gateway_response = self.gateway.process_payment(
                amount=payment.amount,
                method=payment.method,
                details=payment_details
            )
            
            if gateway_response['success']:
                # Payment successful
                payment.status = PaymentStatus.COMPLETED
                payment.paid_at = datetime.utcnow()
                payment.gateway_transaction_id = gateway_response.get('transaction_id')
                payment.gateway_response = gateway_response
                
                # Create corresponding payout
                self._create_seller_payout(payment)
                
            else:
                # Payment failed
                payment.status = PaymentStatus.FAILED
                payment.gateway_response = gateway_response
            
            payment.updated_at = datetime.utcnow()
            updated_payment = self.payment_repository.update(payment)
            self.payment_repository.commit()
            
            return self._payment_to_dict(updated_payment)
            
        except Exception as e:
            # Mark payment as failed
            payment.status = PaymentStatus.FAILED
            payment.gateway_response = {'error': str(e)}
            payment.updated_at = datetime.utcnow()
            self.payment_repository.update(payment)
            self.payment_repository.commit()
            raise e
    
    def get_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment by ID"""
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            return None
        
        return self._payment_to_dict(payment)
    
    def get_user_payments(self, user_id: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get payments by user"""
        filters = {'buyer_id': user_id}
        payments = self.payment_repository.list(filters, page, page_size)
        total_count = self.payment_repository.count(filters)
        
        return {
            'items': [self._payment_to_dict(payment) for payment in payments],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
    
    def create_refund(self, payment_id: str, reason: str, amount: Optional[Decimal] = None) -> Dict[str, Any]:
        """Create refund for payment"""
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            raise NotFoundError("Payment not found")
        
        if payment.status != PaymentStatus.COMPLETED:
            raise BusinessRuleViolationError("Can only refund completed payments")
        
        # Use full payment amount if not specified
        refund_amount = amount or payment.amount
        
        # Validate refund amount
        if refund_amount > payment.amount:
            raise ValidationError("Refund amount cannot exceed payment amount")
        
        # Check if refund already exists
        existing_refund = self.refund_repository.get_by_payment_id(payment_id)
        if existing_refund:
            raise BusinessRuleViolationError("Refund already exists for this payment")
        
        # Create refund
        refund = Refund(
            payment_id=payment_id,
            amount=refund_amount,
            reason=reason,
            status=PaymentStatus.PENDING
        )
        
        created_refund = self.refund_repository.create(refund)
        self.refund_repository.commit()
        
        return self._refund_to_dict(created_refund)
    
    def process_refund(self, refund_id: str) -> Dict[str, Any]:
        """Process refund through gateway"""
        refund = self.refund_repository.get_by_id(refund_id)
        if not refund:
            raise NotFoundError("Refund not found")
        
        if refund.status != PaymentStatus.PENDING:
            raise BusinessRuleViolationError("Refund is not in pending status")
        
        payment = self.payment_repository.get_by_id(refund.payment_id)
        if not payment:
            raise NotFoundError("Original payment not found")
        
        try:
            # Update status to processing
            refund.status = PaymentStatus.PROCESSING
            refund.updated_at = datetime.utcnow()
            self.refund_repository.update(refund)
            self.refund_repository.commit()
            
            # Process through gateway
            gateway_response = self.gateway.process_refund(
                original_transaction_id=payment.gateway_transaction_id,
                amount=refund.amount
            )
            
            if gateway_response['success']:
                # Refund successful
                refund.status = PaymentStatus.REFUNDED
                refund.refunded_at = datetime.utcnow()
                refund.gateway_refund_id = gateway_response.get('refund_id')
                
                # Update original payment status
                payment.status = PaymentStatus.REFUNDED
                payment.updated_at = datetime.utcnow()
                self.payment_repository.update(payment)
                
            else:
                # Refund failed
                refund.status = PaymentStatus.FAILED
            
            refund.gateway_response = gateway_response
            refund.updated_at = datetime.utcnow()
            updated_refund = self.refund_repository.update(refund)
            self.refund_repository.commit()
            
            return self._refund_to_dict(updated_refund)
            
        except Exception as e:
            # Mark refund as failed
            refund.status = PaymentStatus.FAILED
            refund.gateway_response = {'error': str(e)}
            refund.updated_at = datetime.utcnow()
            self.refund_repository.update(refund)
            self.refund_repository.commit()
            raise e
    
    def get_payout(self, payout_id: str) -> Optional[Dict[str, Any]]:
        """Get payout by ID"""
        payout = self.payout_repository.get_by_id(payout_id)
        if not payout:
            return None
        
        return self._payout_to_dict(payout)
    
    def get_user_payouts(self, user_id: str, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """Get payouts by user"""
        filters = {'seller_id': user_id}
        payouts = self.payout_repository.list(filters, page, page_size)
        total_count = self.payout_repository.count(filters)
        
        return {
            'items': [self._payout_to_dict(payout) for payout in payouts],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
    
    def _create_seller_payout(self, payment: Payment):
        """Create payout for seller when payment is completed"""
        session_item = self.session_item_repository.get_by_id(payment.session_item_id)
        session = self.session_repository.get_by_id(session_item.session_id)
        
        # Get jewelry item to find seller
        # This would need to be implemented based on your repository structure
        
        winning_bid = session_item.current_highest_bid
        seller_fee = self._calculate_seller_fee(winning_bid, session.rules)
        payout_amount = winning_bid - seller_fee
        
        payout = Payout(
            seller_id=session_item.jewelry_item.owner_user_id,  # This needs proper relationship
            session_item_id=payment.session_item_id,
            amount=payout_amount,
            status=PayoutStatus.PENDING,
            meta={
                'winning_bid': float(winning_bid),
                'seller_fee': float(seller_fee),
                'fee_percentage': self._get_seller_fee_percentage(session.rules)
            }
        )
        
        self.payout_repository.create(payout)
    
    def _calculate_buyer_fee(self, amount: Decimal, session_rules: Dict[str, Any]) -> Decimal:
        """Calculate buyer fee"""
        # Get fee configuration from session rules or default
        fee_percentage = session_rules.get('buyer_fee_percentage', Decimal('10.0'))  # 10% default
        min_fee = session_rules.get('buyer_min_fee', Decimal('5.0'))
        max_fee = session_rules.get('buyer_max_fee')
        
        fee = amount * (fee_percentage / 100)
        
        if fee < min_fee:
            fee = min_fee
        
        if max_fee and fee > max_fee:
            fee = max_fee
        
        return fee
    
    def _calculate_seller_fee(self, amount: Decimal, session_rules: Dict[str, Any]) -> Decimal:
        """Calculate seller fee"""
        # Get fee configuration from session rules or default
        fee_percentage = session_rules.get('seller_fee_percentage', Decimal('15.0'))  # 15% default
        min_fee = session_rules.get('seller_min_fee', Decimal('10.0'))
        max_fee = session_rules.get('seller_max_fee')
        
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
    
    def _payment_to_dict(self, payment: Payment) -> Dict[str, Any]:
        """Convert payment to dictionary"""
        return {
            'id': payment.id,
            'buyer_id': payment.buyer_id,
            'session_item_id': payment.session_item_id,
            'amount': float(payment.amount),
            'method': payment.method.value,
            'status': payment.status.value,
            'gateway_transaction_id': payment.gateway_transaction_id,
            'gateway_response': payment.gateway_response,
            'created_at': payment.created_at.isoformat() if payment.created_at else None,
            'updated_at': payment.updated_at.isoformat() if payment.updated_at else None,
            'paid_at': payment.paid_at.isoformat() if payment.paid_at else None,
            'meta': payment.meta
        }
    
    def _payout_to_dict(self, payout: Payout) -> Dict[str, Any]:
        """Convert payout to dictionary"""
        return {
            'id': payout.id,
            'seller_id': payout.seller_id,
            'session_item_id': payout.session_item_id,
            'amount': float(payout.amount),
            'status': payout.status.value,
            'bank_account_info': payout.bank_account_info,
            'created_at': payout.created_at.isoformat() if payout.created_at else None,
            'updated_at': payout.updated_at.isoformat() if payout.updated_at else None,
            'paid_at': payout.paid_at.isoformat() if payout.paid_at else None,
            'meta': payout.meta
        }
    
    def _refund_to_dict(self, refund: Refund) -> Dict[str, Any]:
        """Convert refund to dictionary"""
        return {
            'id': refund.id,
            'payment_id': refund.payment_id,
            'amount': float(refund.amount),
            'reason': refund.reason,
            'status': refund.status.value,
            'gateway_refund_id': refund.gateway_refund_id,
            'gateway_response': refund.gateway_response,
            'created_at': refund.created_at.isoformat() if refund.created_at else None,
            'updated_at': refund.updated_at.isoformat() if refund.updated_at else None,
            'refunded_at': refund.refunded_at.isoformat() if refund.refunded_at else None,
            'meta': refund.meta
        }
