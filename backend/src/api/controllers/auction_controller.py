"""
Auction API controller for the Jewelry Auction System
"""
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError as MarshmallowValidationError
from api.middleware.auth_middleware import jwt_required, staff_required, manager_required, get_current_user, get_current_user_role
from services.auction_service import AuctionService
from services.bidding_service import BiddingService
from services.settlement_service import SettlementService
from infrastructure.repositories.auction_repository import AuctionSessionRepository, SessionItemRepository, EnrollmentRepository
from infrastructure.repositories.jewelry_repository import JewelryItemRepository
from infrastructure.repositories.bid_repository import BidRepository
from infrastructure.repositories.payment_repository import PaymentRepository, PayoutRepository, TransactionFeeRepository
from infrastructure.databases.mssql import get_db_session
from domain.exceptions import (
    ValidationError,
    NotFoundError,
    BusinessRuleViolationError,
    AuthorizationError
)
from decimal import Decimal
import uuid

# Create blueprint
auction_bp = Blueprint('auction', __name__, url_prefix='/api/v1/auctions')

def get_auction_service():
    """Get auction service instance"""
    session = get_db_session()
    session_repo = AuctionSessionRepository(session)
    session_item_repo = SessionItemRepository(session)
    enrollment_repo = EnrollmentRepository(session)
    jewelry_repo = JewelryItemRepository(session)
    return AuctionService(session_repo, session_item_repo, enrollment_repo, jewelry_repo)

def get_bidding_service():
    """Get bidding service instance"""
    session = get_db_session()
    bid_repo = BidRepository(session)
    session_repo = AuctionSessionRepository(session)
    session_item_repo = SessionItemRepository(session)
    enrollment_repo = EnrollmentRepository(session)
    return BiddingService(bid_repo, session_repo, session_item_repo, enrollment_repo)

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


@auction_bp.route('', methods=['POST'])
@staff_required
def create_auction_session():
    """
    Create a new auction session
    ---
    tags:
      - Auctions
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: "Monthly Jewelry Auction"
            description:
              type: string
              example: "Premium jewelry collection"
            start_at:
              type: string
              format: date-time
              example: "2024-01-15T10:00:00Z"
            end_at:
              type: string
              format: date-time
              example: "2024-01-15T18:00:00Z"
            assigned_staff_id:
              type: string
              example: "staff-uuid"
            rules:
              type: object
              example: {"anti_sniping_enabled": true}
    responses:
      201:
        description: Auction session created successfully
      400:
        description: Invalid input data
      401:
        description: Authentication required
      403:
        description: Insufficient permissions
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        user_role = get_current_user_role()
        auction_service = get_auction_service()
        
        result = auction_service.create_auction_session(user_role, data)
        
        return jsonify({
            'success': True,
            'data': result
        }), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except BusinessRuleViolationError as e:
        return jsonify({'error': str(e)}), 400
    except AuthorizationError as e:
        return jsonify({'error': str(e)}), 403
    except Exception as e:
        current_app.logger.error(f"Error creating auction session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auction_bp.route('', methods=['GET'])
def list_auction_sessions():
    """
    List auction sessions
    ---
    tags:
      - Auctions
    parameters:
      - in: query
        name: status
        type: string
        enum: [DRAFT, SCHEDULED, OPEN, PAUSED, CLOSED, SETTLED, CANCELED]
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
        description: List of auction sessions
    """
    try:
        # Get query parameters
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # Build filters
        filters = {}
        if status:
            filters['status'] = status
        
        auction_service = get_auction_service()
        result = auction_service.list_auction_sessions(filters, page, page_size)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error listing auction sessions: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auction_bp.route('/<session_id>', methods=['GET'])
def get_auction_session(session_id):
    """
    Get auction session by ID
    ---
    tags:
      - Auctions
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
    responses:
      200:
        description: Auction session details
      404:
        description: Session not found
    """
    try:
        auction_service = get_auction_service()
        result = auction_service.get_auction_session(session_id)
        
        if not result:
            return jsonify({'error': 'Auction session not found'}), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting auction session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auction_bp.route('/<session_id>/schedule', methods=['POST'])
@manager_required
def schedule_session(session_id):
    """
    Schedule an auction session
    ---
    tags:
      - Auctions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
    responses:
      200:
        description: Session scheduled successfully
      400:
        description: Cannot schedule session
      403:
        description: Insufficient permissions
      404:
        description: Session not found
    """
    try:
        user_role = get_current_user_role()
        auction_service = get_auction_service()
        
        result = auction_service.schedule_session(session_id, user_role)
        
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
        current_app.logger.error(f"Error scheduling session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auction_bp.route('/<session_id>/open', methods=['POST'])
@staff_required
def open_session(session_id):
    """
    Open an auction session for bidding
    ---
    tags:
      - Auctions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
    responses:
      200:
        description: Session opened successfully
      400:
        description: Cannot open session
      403:
        description: Insufficient permissions
      404:
        description: Session not found
    """
    try:
        user_role = get_current_user_role()
        auction_service = get_auction_service()
        
        result = auction_service.open_session(session_id, user_role)
        
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
        current_app.logger.error(f"Error opening session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auction_bp.route('/<session_id>/close', methods=['POST'])
@staff_required
def close_session(session_id):
    """
    Close an auction session
    ---
    tags:
      - Auctions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
    responses:
      200:
        description: Session closed successfully
      400:
        description: Cannot close session
      403:
        description: Insufficient permissions
      404:
        description: Session not found
    """
    try:
        user_role = get_current_user_role()
        auction_service = get_auction_service()
        
        result = auction_service.close_session(session_id, user_role)
        
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
        current_app.logger.error(f"Error closing session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auction_bp.route('/<session_id>/items', methods=['GET'])
def get_session_items(session_id):
    """
    Get items in an auction session
    ---
    tags:
      - Auctions
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
    responses:
      200:
        description: List of session items
      404:
        description: Session not found
    """
    try:
        auction_service = get_auction_service()
        result = auction_service.get_session_items(session_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting session items: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auction_bp.route('/<session_id>/enroll', methods=['POST'])
@jwt_required
def enroll_in_session(session_id):
    """
    Enroll user in auction session
    ---
    tags:
      - Auctions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
    responses:
      200:
        description: Enrollment successful
      400:
        description: Cannot enroll in session
      401:
        description: Authentication required
      404:
        description: Session not found
    """
    try:
        user_id = get_current_user()
        auction_service = get_auction_service()
        
        result = auction_service.enroll_user_in_session(session_id, user_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except BusinessRuleViolationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error enrolling in session: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auction_bp.route('/sessions', methods=['POST'])
@manager_required
def create_session():
    """
    Create a new auction session (MANAGER only)
    ---
    tags:
      - Auctions
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: "Weekly Jewelry Auction #1"
            description:
              type: string
              example: "Weekly auction featuring premium jewelry items"
            start_at:
              type: string
              format: date-time
              example: "2024-01-15T10:00:00Z"
            end_at:
              type: string
              format: date-time
              example: "2024-01-15T18:00:00Z"
    responses:
      201:
        description: Session created successfully
      400:
        description: Validation error
      401:
        description: Authentication required
      403:
        description: Insufficient permissions
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required',
                'code': 'MISSING_BODY'
            }), 400

        user_id = get_current_user()

        auction_service = get_auction_service()
        result = auction_service.create_session(user_id, data)

        return jsonify({
            'success': True,
            'message': 'Session created successfully',
            'data': result
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Create session error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create session',
            'code': 'CREATE_ERROR'
        }), 500


@auction_bp.route('/sessions/<session_id>/items', methods=['POST'])
@manager_required
def assign_items_to_session(session_id):
    """
    Assign jewelry items to auction session (MANAGER only)
    ---
    tags:
      - Auctions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - jewelry_item_ids
          properties:
            jewelry_item_ids:
              type: array
              items:
                type: string
              example: ["item1-id", "item2-id"]
            start_prices:
              type: object
              example: {"item1-id": 100.00, "item2-id": 200.00}
            step_prices:
              type: object
              example: {"item1-id": 10.00, "item2-id": 20.00}
    responses:
      200:
        description: Items assigned successfully
      400:
        description: Validation error
      404:
        description: Session not found
      403:
        description: Insufficient permissions
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is required',
                'code': 'MISSING_BODY'
            }), 400

        user_id = get_current_user()

        auction_service = get_auction_service()
        result = auction_service.assign_items_to_session(session_id, user_id, data)

        return jsonify({
            'success': True,
            'message': 'Items assigned to session successfully',
            'data': result
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'SESSION_NOT_FOUND'
        }), 404
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Assign items to session error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to assign items to session',
            'code': 'ASSIGN_ERROR'
        }), 500


@auction_bp.route('/sessions/<session_id>/open', methods=['POST'])
@manager_required
def open_session_manager(session_id):
    """
    Open an auction session (MANAGER only)
    ---
    tags:
      - Auctions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
    responses:
      200:
        description: Session opened successfully
      400:
        description: Cannot open session
      404:
        description: Session not found
      403:
        description: Insufficient permissions
    """
    try:
        user_id = get_current_user()

        auction_service = get_auction_service()
        result = auction_service.open_session(session_id, user_id)

        return jsonify({
            'success': True,
            'message': 'Session opened successfully',
            'data': result
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'SESSION_NOT_FOUND'
        }), 404
    except BusinessRuleViolationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'BUSINESS_RULE_VIOLATION'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Open session error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to open session',
            'code': 'OPEN_ERROR'
        }), 500


@auction_bp.route('/sessions/<session_id>/close', methods=['POST'])
@manager_required
def close_session_manager(session_id):
    """
    Close an auction session and determine winners (MANAGER only)
    ---
    tags:
      - Auctions
    security:
      - Bearer: []
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
    responses:
      200:
        description: Session closed successfully
      400:
        description: Cannot close session
      404:
        description: Session not found
      403:
        description: Insufficient permissions
    """
    try:
        user_id = get_current_user()

        auction_service = get_auction_service()
        result = auction_service.close_session(session_id, user_id)

        return jsonify({
            'success': True,
            'message': 'Session closed successfully',
            'data': result
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'SESSION_NOT_FOUND'
        }), 404
    except BusinessRuleViolationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'BUSINESS_RULE_VIOLATION'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Close session error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to close session',
            'code': 'CLOSE_ERROR'
        }), 500
