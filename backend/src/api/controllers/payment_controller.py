"""
Payment API controller for the Jewelry Auction System
"""
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError as MarshmallowValidationError
from api.middleware.auth_middleware import jwt_required, staff_required, get_current_user
from services.payment_service import PaymentService
from services.settlement_service import SettlementService
from infrastructure.repositories.payment_repository import PaymentRepository, PayoutRepository, RefundRepository, TransactionFeeRepository
from infrastructure.repositories.auction_repository import AuctionSessionRepository, SessionItemRepository
from infrastructure.repositories.jewelry_repository import JewelryItemRepository
from infrastructure.repositories.bid_repository import BidRepository
from infrastructure.databases.mssql import get_db_session
from domain.enums import PaymentMethod
from domain.exceptions import (
    ValidationError,
    NotFoundError,
    BusinessRuleViolationError,
    AuthorizationError
)
from decimal import Decimal

# Create blueprint
payment_bp = Blueprint('payments', __name__, url_prefix='/api/v1/payments')

def get_payment_service():
    """Get payment service instance"""
    session = get_db_session()
    payment_repo = PaymentRepository(session)
    payout_repo = PayoutRepository(session)
    refund_repo = RefundRepository(session)
    session_item_repo = SessionItemRepository(session)
    session_repo = AuctionSessionRepository(session)
    fee_repo = TransactionFeeRepository(session)
    return PaymentService(payment_repo, payout_repo, refund_repo, session_item_repo, session_repo, fee_repo)

def get_settlement_service():
    """Get settlement service instance"""
    session = get_db_session()
    session_repo = AuctionSessionRepository(session)
    session_item_repo = SessionItemRepository(session)
    bid_repo = BidRepository(session)
    payment_repo = PaymentRepository(session)
    payout_repo = PayoutRepository(session)
    jewelry_repo = JewelryItemRepository(session)
    fee_repo = TransactionFeeRepository(session)
    return SettlementService(session_repo, session_item_repo, bid_repo, payment_repo, payout_repo, jewelry_repo, fee_repo)


@payment_bp.route('', methods=['POST'])
@jwt_required
def create_payment():
    """
    Create payment for winning bid
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - session_item_id
            - payment_method
          properties:
            session_item_id:
              type: string
              example: "item-uuid"
            payment_method:
              type: string
              enum: [CREDIT_CARD, DEBIT_CARD, BANK_TRANSFER, DIGITAL_WALLET, CASH]
              example: "CREDIT_CARD"
    responses:
      201:
        description: Payment created successfully
      400:
        description: Invalid payment data
      401:
        description: Authentication required
      404:
        description: Session item not found
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate required fields
        required_fields = ['session_item_id', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        user_id = get_current_user()
        session_item_id = data['session_item_id']
        payment_method = PaymentMethod(data['payment_method'])
        
        payment_service = get_payment_service()
        result = payment_service.create_payment(session_item_id, user_id, payment_method)
        
        return jsonify({
            'success': True,
            'data': result
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessRuleViolationError as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': 'Invalid payment method'}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@payment_bp.route('/<payment_id>/process', methods=['POST'])
@jwt_required
def process_payment(payment_id):
    """
    Process payment through gateway
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: payment_id
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            card_number:
              type: string
              example: "4111111111111111"
            expiry_month:
              type: integer
              example: 12
            expiry_year:
              type: integer
              example: 2025
            cvv:
              type: string
              example: "123"
            cardholder_name:
              type: string
              example: "John Doe"
    responses:
      200:
        description: Payment processed successfully
      400:
        description: Invalid payment details
      401:
        description: Authentication required
      404:
        description: Payment not found
    """
    try:
        data = request.get_json() or {}
        
        payment_service = get_payment_service()
        result = payment_service.process_payment(payment_id, data)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessRuleViolationError as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        current_app.logger.error(f"Error processing payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@payment_bp.route('/<payment_id>', methods=['GET'])
@jwt_required
def get_payment(payment_id):
    """
    Get payment details
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: payment_id
        type: string
        required: true
    responses:
      200:
        description: Payment details
      401:
        description: Authentication required
      404:
        description: Payment not found
    """
    try:
        payment_service = get_payment_service()
        result = payment_service.get_payment(payment_id)
        
        if not result:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting payment: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@payment_bp.route('/my-payments', methods=['GET'])
@jwt_required
def get_my_payments():
    """
    Get current user's payments
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: page_size
        type: integer
        default: 20
    responses:
      200:
        description: List of user's payments
      401:
        description: Authentication required
    """
    try:
        user_id = get_current_user()
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        payment_service = get_payment_service()
        result = payment_service.get_user_payments(user_id, page, page_size)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user payments: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@payment_bp.route('/<payment_id>/refund', methods=['POST'])
@staff_required
def create_refund(payment_id):
    """
    Create refund for payment
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: payment_id
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - reason
          properties:
            reason:
              type: string
              example: "Item damaged during shipping"
            amount:
              type: number
              format: decimal
              example: 1500.00
              description: "Partial refund amount (optional, defaults to full amount)"
    responses:
      201:
        description: Refund created successfully
      400:
        description: Invalid refund data
      401:
        description: Authentication required
      403:
        description: Insufficient permissions
      404:
        description: Payment not found
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        if 'reason' not in data:
            return jsonify({'error': 'Reason is required'}), 400
        
        reason = data['reason']
        amount = None
        if 'amount' in data:
            amount = Decimal(str(data['amount']))
        
        payment_service = get_payment_service()
        result = payment_service.create_refund(payment_id, reason, amount)
        
        return jsonify({
            'success': True,
            'data': result
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessRuleViolationError as e:
        return jsonify({'error': str(e)}), 400
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except ValueError as e:
        return jsonify({'error': 'Invalid amount format'}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating refund: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@payment_bp.route('/payouts/my-payouts', methods=['GET'])
@jwt_required
def get_my_payouts():
    """
    Get current user's payouts
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: page_size
        type: integer
        default: 20
    responses:
      200:
        description: List of user's payouts
      401:
        description: Authentication required
    """
    try:
        user_id = get_current_user()
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        payment_service = get_payment_service()
        result = payment_service.get_user_payouts(user_id, page, page_size)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user payouts: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@payment_bp.route('/sessions/<session_id>/settle', methods=['POST'])
@staff_required
def settle_session(session_id):
    """
    Settle auction session (create payments and payouts)
    ---
    tags:
      - Payments
    security:
      - Bearer: []
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
    responses:
      200:
        description: Session settled successfully
      400:
        description: Cannot settle session
      401:
        description: Authentication required
      403:
        description: Insufficient permissions
      404:
        description: Session not found
    """
    try:
        from domain.enums import UserRole
        from api.middleware.auth_middleware import get_current_user_role
        
        user_role = get_current_user_role()
        settlement_service = get_settlement_service()
        
        result = settlement_service.settle_session(session_id, user_role)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except BusinessRuleViolationError as e:
        return jsonify({'error': str(e)}), 400
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Error settling session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
