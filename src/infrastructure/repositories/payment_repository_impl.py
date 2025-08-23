from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.domain.models.payment import Payment, PaymentStatus, PaymentMethod
from src.domain.repositories.payment_repo import IPaymentRepository
from src.infrastructure.models.payment_model import PaymentModel
from datetime import datetime

class PaymentRepository(IPaymentRepository):
    def __init__(self, session: Session):
        self.session = session

    def get(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        try:
            payment_model = self.session.query(PaymentModel).filter(PaymentModel.id == payment_id).first()
            if payment_model:
                return self._model_to_domain(payment_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting payment by ID: {str(e)}")

    def get_by_order(self, order_id: int) -> Optional[Payment]:
        """Get payment by winning bid ID (order_id)"""
        try:
            payment_model = self.session.query(PaymentModel).filter(PaymentModel.winning_bid_id == order_id).first()
            if payment_model:
                return self._model_to_domain(payment_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting payment by order: {str(e)}")

    def create(self, payment: Payment) -> Payment:
        """Create new payment"""
        try:
            payment_model = self._domain_to_model(payment)
            self.session.add(payment_model)
            self.session.commit()
            self.session.refresh(payment_model)
            return self._model_to_domain(payment_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error creating payment: {str(e)}")

    def update(self, payment: Payment) -> Payment:
        """Update existing payment"""
        try:
            payment_model = self.session.query(PaymentModel).filter(PaymentModel.id == payment.id).first()
            if not payment_model:
                raise Exception(f"Payment with ID {payment.id} not found")

            # Update fields
            payment_model.auction_item_id = payment.auction_item_id
            payment_model.winning_bid_id = payment.winning_bid_id
            payment_model.buyer_id = payment.buyer_id
            payment_model.seller_id = payment.seller_id
            payment_model.amount = payment.amount
            payment_model.service_fee = payment.service_fee
            payment_model.seller_fee = payment.seller_fee
            payment_model.net_amount = payment.net_amount
            payment_model.payment_method = payment.payment_method
            payment_model.status = payment.status
            payment_model.gateway_transaction_id = payment.gateway_transaction_id
            payment_model.gateway_response = payment.gateway_response
            payment_model.payment_deadline = payment.payment_deadline
            payment_model.paid_at = payment.paid_at
            payment_model.failed_reason = payment.failed_reason
            payment_model.refund_reason = payment.refund_reason
            payment_model.refunded_at = payment.refunded_at
            payment_model.updated_at = datetime.utcnow()

            self.session.commit()
            self.session.refresh(payment_model)
            return self._model_to_domain(payment_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error updating payment: {str(e)}")

    def get_by_buyer(self, buyer_id: int) -> List[Payment]:
        """Get payments by buyer ID"""
        try:
            payment_models = (self.session.query(PaymentModel)
                             .filter(PaymentModel.buyer_id == buyer_id)
                             .order_by(PaymentModel.created_at.desc()).all())
            return [self._model_to_domain(model) for model in payment_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting payments by buyer: {str(e)}")

    def get_by_seller(self, seller_id: int) -> List[Payment]:
        """Get payments by seller ID"""
        try:
            payment_models = (self.session.query(PaymentModel)
                             .filter(PaymentModel.seller_id == seller_id)
                             .order_by(PaymentModel.created_at.desc()).all())
            return [self._model_to_domain(model) for model in payment_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting payments by seller: {str(e)}")

    def get_pending_payments(self) -> List[Payment]:
        """Get all pending payments"""
        try:
            payment_models = (self.session.query(PaymentModel)
                             .filter(PaymentModel.status == PaymentStatus.PENDING)
                             .order_by(PaymentModel.payment_deadline).all())
            return [self._model_to_domain(model) for model in payment_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting pending payments: {str(e)}")

    def _model_to_domain(self, model: PaymentModel) -> Payment:
        """Convert PaymentModel to Payment domain object"""
        return Payment(
            id=model.id,
            auction_item_id=model.auction_item_id,
            winning_bid_id=model.winning_bid_id,
            buyer_id=model.buyer_id,
            seller_id=model.seller_id,
            amount=model.amount,
            service_fee=model.service_fee,
            seller_fee=model.seller_fee,
            net_amount=model.net_amount,
            payment_method=model.payment_method,
            status=model.status,
            gateway_transaction_id=model.gateway_transaction_id,
            gateway_response=model.gateway_response,
            payment_deadline=model.payment_deadline,
            paid_at=model.paid_at,
            failed_reason=model.failed_reason,
            refund_reason=model.refund_reason,
            refunded_at=model.refunded_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _domain_to_model(self, domain: Payment) -> PaymentModel:
        """Convert Payment domain object to PaymentModel"""
        return PaymentModel(
            id=domain.id,
            auction_item_id=domain.auction_item_id,
            winning_bid_id=domain.winning_bid_id,
            buyer_id=domain.buyer_id,
            seller_id=domain.seller_id,
            amount=domain.amount,
            service_fee=domain.service_fee,
            seller_fee=domain.seller_fee,
            net_amount=domain.net_amount,
            payment_method=domain.payment_method,
            status=domain.status,
            gateway_transaction_id=domain.gateway_transaction_id,
            gateway_response=domain.gateway_response,
            payment_deadline=domain.payment_deadline,
            paid_at=domain.paid_at,
            failed_reason=domain.failed_reason,
            refund_reason=domain.refund_reason,
            refunded_at=domain.refunded_at,
            created_at=domain.created_at,
            updated_at=domain.updated_at
        )
