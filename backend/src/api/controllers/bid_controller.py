"""
Bidding API controller for the Jewelry Auction System
"""
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError as MarshmallowValidationError
from api.middleware.auth_middleware import jwt_required, get_current_user
from services.bidding_service import BiddingService
from infrastructure.repositories.bid_repository import BidRepository
from infrastructure.repositories.auction_repository import AuctionSessionRepository, SessionItemRepository, EnrollmentRepository
from infrastructure.databases.mssql import get_db_session
from domain.exceptions import (
    ValidationError,
    NotFoundError,
    BusinessRuleViolationError,
    ConcurrencyError
)
from decimal import Decimal
import uuid

# Create blueprint
bid_bp = Blueprint('bids', __name__, url_prefix='/api/v1/bids')

def get_bidding_service():
    """Get bidding service instance"""
    session = get_db_session()
    bid_repo = BidRepository(session)
    session_repo = AuctionSessionRepository(session)
    session_item_repo = SessionItemRepository(session)
    enrollment_repo = EnrollmentRepository(session)
    return BiddingService(bid_repo, session_repo, session_item_repo, enrollment_repo)


@bid_bp.route('', methods=['POST'])
@jwt_required
def place_bid():
    """
    Place a bid on an auction item
    ---
    tags:
      - Bidding
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - session_id
            - session_item_id
            - amount
          properties:
            session_id:
              type: string
              example: "session-uuid"
            session_item_id:
              type: string
              example: "item-uuid"
            amount:
              type: number
              format: decimal
              example: 1500.00
            idempotency_key:
              type: string
              example: "unique-key-123"
      - in: header
        name: Idempotency-Key
        type: string
        description: Optional idempotency key to prevent duplicate bids
    responses:
      201:
        description: Bid placed successfully
      400:
        description: Invalid bid data or business rule violation
      401:
        description: Authentication required
      404:
        description: Session or item not found
      409:
        description: Concurrent bid conflict
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Validate required fields
        required_fields = ['session_id', 'session_item_id', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        user_id = get_current_user()
        session_id = data['session_id']
        session_item_id = data['session_item_id']
        amount = Decimal(str(data['amount']))
        
        # Get idempotency key from header or body
        idempotency_key = request.headers.get('Idempotency-Key') or data.get('idempotency_key')
        
        bidding_service = get_bidding_service()
        result = bidding_service.place_bid(
            session_id=session_id,
            session_item_id=session_item_id,
            bidder_id=user_id,
            amount=amount,
            idempotency_key=idempotency_key
        )
        
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
    except ConcurrencyError as e:
        return jsonify({'error': str(e)}), 409
    except ValueError as e:
        return jsonify({'error': 'Invalid amount format'}), 400
    except Exception as e:
        current_app.logger.error(f"Error placing bid: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bid_bp.route('/<bid_id>', methods=['GET'])
@jwt_required
def get_bid(bid_id):
    """
    Get bid details
    ---
    tags:
      - Bidding
    security:
      - Bearer: []
    parameters:
      - in: path
        name: bid_id
        type: string
        required: true
    responses:
      200:
        description: Bid details
      401:
        description: Authentication required
      404:
        description: Bid not found
    """
    try:
        bidding_service = get_bidding_service()
        result = bidding_service.get_bid(bid_id)
        
        if not result:
            return jsonify({'error': 'Bid not found'}), 404
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting bid: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bid_bp.route('/sessions/<session_id>', methods=['GET'])
def get_session_bids(session_id):
    """
    Get all bids for a session
    ---
    tags:
      - Bidding
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: page_size
        type: integer
        default: 50
    responses:
      200:
        description: List of bids for the session
      404:
        description: Session not found
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        bidding_service = get_bidding_service()
        result = bidding_service.get_session_bids(session_id, page, page_size)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting session bids: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bid_bp.route('/items/<session_item_id>', methods=['GET'])
def get_session_item_bids(session_item_id):
    """
    Get all bids for a specific session item
    ---
    tags:
      - Bidding
    parameters:
      - in: path
        name: session_item_id
        type: string
        required: true
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: page_size
        type: integer
        default: 50
    responses:
      200:
        description: List of bids for the session item
      404:
        description: Session item not found
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        bidding_service = get_bidding_service()
        result = bidding_service.get_session_item_bids(session_item_id, page, page_size)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting session item bids: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bid_bp.route('/items/<session_item_id>/highest', methods=['GET'])
def get_highest_bid(session_item_id):
    """
    Get current highest bid for a session item
    ---
    tags:
      - Bidding
    parameters:
      - in: path
        name: session_item_id
        type: string
        required: true
    responses:
      200:
        description: Current highest bid
      404:
        description: No bids found for this item
    """
    try:
        bidding_service = get_bidding_service()
        result = bidding_service.get_current_highest_bid(session_item_id)
        
        if not result:
            return jsonify({
                'success': True,
                'data': None,
                'message': 'No bids placed yet'
            })
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting highest bid: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bid_bp.route('/items/<session_item_id>/history', methods=['GET'])
def get_bid_history(session_item_id):
    """
    Get bid history for a session item
    ---
    tags:
      - Bidding
    parameters:
      - in: path
        name: session_item_id
        type: string
        required: true
      - in: query
        name: limit
        type: integer
        default: 10
        description: Number of recent bids to return
    responses:
      200:
        description: Bid history for the item
    """
    try:
        limit = int(request.args.get('limit', 10))
        
        bidding_service = get_bidding_service()
        result = bidding_service.get_bid_history(session_item_id, limit)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting bid history: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bid_bp.route('/my-bids', methods=['GET'])
@jwt_required
def get_my_bids():
    """
    Get current user's bids
    ---
    tags:
      - Bidding
    security:
      - Bearer: []
    parameters:
      - in: query
        name: session_id
        type: string
        description: Filter by specific session
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: page_size
        type: integer
        default: 50
    responses:
      200:
        description: List of user's bids
      401:
        description: Authentication required
    """
    try:
        user_id = get_current_user()
        session_id = request.args.get('session_id')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        
        bidding_service = get_bidding_service()
        result = bidding_service.get_user_bids(user_id, session_id, page, page_size)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user bids: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@bid_bp.route('/sessions/<session_id>/items/<item_id>/bids', methods=['GET'])
def get_session_item_bids_detailed(session_id, item_id):
    """
    Get bids for a specific session item
    ---
    tags:
      - Bidding
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
      - in: path
        name: item_id
        type: string
        required: true
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: limit
        type: integer
        default: 20
    responses:
      200:
        description: Bids retrieved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
              properties:
                items:
                  type: array
                  items:
                    type: object
                total:
                  type: integer
                page:
                  type: integer
                limit:
                  type: integer
      404:
        description: Session or item not found
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 items per page

        bidding_service = get_bidding_service()
        result = bidding_service.get_session_item_bids(session_id, item_id, page, limit)

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'NOT_FOUND'
        }), 404
    except Exception as e:
        current_app.logger.error(f"Get session item bids error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve bids',
            'code': 'GET_BIDS_ERROR'
        }), 500


@bid_bp.route('/sessions/<session_id>/items/<item_id>/bids', methods=['POST'])
@jwt_required
def place_session_item_bid(session_id, item_id):
    """
    Place a bid on a specific session item
    ---
    tags:
      - Bidding
    security:
      - Bearer: []
    parameters:
      - in: path
        name: session_id
        type: string
        required: true
      - in: path
        name: item_id
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - amount
          properties:
            amount:
              type: number
              example: 150.00
    responses:
      201:
        description: Bid placed successfully
      400:
        description: Invalid bid amount or session not open
      401:
        description: Authentication required
      404:
        description: Session or item not found
    """
    try:
        data = request.get_json()

        if not data or 'amount' not in data:
            return jsonify({
                'success': False,
                'error': 'Bid amount is required',
                'code': 'MISSING_AMOUNT'
            }), 400

        user_id = get_current_user()
        amount = Decimal(str(data['amount']))

        bidding_service = get_bidding_service()
        result = bidding_service.place_session_item_bid(session_id, item_id, user_id, amount)

        return jsonify({
            'success': True,
            'message': 'Bid placed successfully',
            'data': result
        }), 201

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'NOT_FOUND'
        }), 404
    except BusinessRuleViolationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'BUSINESS_RULE_VIOLATION'
        }), 400
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except Exception as e:
        current_app.logger.error(f"Place session item bid error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to place bid',
            'code': 'PLACE_BID_ERROR'
        }), 500
