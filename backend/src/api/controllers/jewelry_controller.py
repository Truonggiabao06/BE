"""
Jewelry API controller for the Jewelry Auction System
"""
from flask import Blueprint, request, jsonify, current_app
from api.middleware.auth_middleware import jwt_required, member_required, staff_required, get_current_user, get_current_user_role
from services.jewelry_service import JewelryService
from infrastructure.repositories.jewelry_repository import JewelryItemRepository
from infrastructure.repositories.sell_request_repository import SellRequestRepository
from infrastructure.databases.mssql import get_db_session
from domain.enums import JewelryStatus
from domain.exceptions import (
    ValidationError,
    NotFoundError,
    BusinessRuleViolationError,
    AuthorizationError
)

# Create blueprint
jewelry_bp = Blueprint('jewelry', __name__, url_prefix='/api/v1/jewelry')

def get_jewelry_service():
    """Get jewelry service instance"""
    session = get_db_session()
    jewelry_repository = JewelryItemRepository(session)
    sell_request_repository = SellRequestRepository(session)
    return JewelryService(jewelry_repository, sell_request_repository)


@jewelry_bp.route('/sell-requests', methods=['POST'])
@member_required
def submit_sell_request():
    """
    Submit a new sell request
    ---
    tags:
      - Jewelry
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - description
            - photos
          properties:
            title:
              type: string
              example: "Diamond Ring"
            description:
              type: string
              example: "Beautiful 2-carat diamond ring"
            photos:
              type: array
              items:
                type: string
              example: ["photo1.jpg", "photo2.jpg"]
            attributes:
              type: object
              example: {"material": "gold", "weight": "5.2g"}
            weight:
              type: number
              example: 5.2
            seller_notes:
              type: string
              example: "Inherited from grandmother"
    responses:
      201:
        description: Sell request submitted successfully
      400:
        description: Validation error
      401:
        description: Authentication required
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
        user_role = get_current_user_role()
        
        jewelry_service = get_jewelry_service()
        result = jewelry_service.submit_sell_request(user_id, user_role, data)
        
        return jsonify({
            'success': True,
            'message': 'Sell request submitted successfully',
            'data': result
        }), 201
        
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
        current_app.logger.error(f"Submit sell request error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit sell request',
            'code': 'SUBMIT_ERROR'
        }), 500


@jewelry_bp.route('', methods=['POST'])
@staff_required
def create_jewelry_item():
    """
    Create a new jewelry item (STAFF/MANAGER/ADMIN only)
    ---
    tags:
      - Jewelry
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - title
            - description
          properties:
            title:
              type: string
              example: "Diamond Ring"
            description:
              type: string
              example: "Beautiful 2-carat diamond ring"
            photos:
              type: array
              items:
                type: string
              example: ["photo1.jpg", "photo2.jpg"]
            attributes:
              type: object
              example: {"material": "gold", "weight": "5.2g"}
            weight:
              type: number
              example: 5.2
            estimated_price:
              type: number
              example: 1500.00
            reserve_price:
              type: number
              example: 1200.00
    responses:
      201:
        description: Jewelry item created successfully
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
        user_role = get_current_user_role()

        jewelry_service = get_jewelry_service()
        result = jewelry_service.create_jewelry_item(user_id, user_role, data)

        return jsonify({
            'success': True,
            'message': 'Jewelry item created successfully',
            'data': result
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'VALIDATION_ERROR'
        }), 400
    except AuthorizationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'NOT_AUTHORIZED'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Create jewelry item error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create jewelry item',
            'code': 'CREATE_ERROR'
        }), 500


@jewelry_bp.route('/items', methods=['GET'])
def list_jewelry_items():
    """
    List jewelry items
    ---
    tags:
      - Jewelry
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: page_size
        type: integer
        default: 20
      - in: query
        name: status
        type: string
        enum: [PENDING_APPRAISAL, APPRAISED, APPROVED, IN_AUCTION, SOLD, UNSOLD, RETURNED, WITHDRAWN]
      - in: query
        name: search
        type: string
      - in: query
        name: min_price
        type: number
      - in: query
        name: max_price
        type: number
    responses:
      200:
        description: Jewelry items retrieved successfully
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
                pagination:
                  type: object
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)  # Max 100 items per page
        
        # Build filters
        filters = {}
        
        if request.args.get('status'):
            try:
                status = JewelryStatus(request.args.get('status'))
                filters['status'] = status
            except ValueError:
                pass
        
        if request.args.get('search'):
            filters['search'] = request.args.get('search')
        
        if request.args.get('min_price'):
            try:
                filters['min_price'] = float(request.args.get('min_price'))
            except ValueError:
                pass
        
        if request.args.get('max_price'):
            try:
                filters['max_price'] = float(request.args.get('max_price'))
            except ValueError:
                pass
        
        jewelry_service = get_jewelry_service()
        result = jewelry_service.list_jewelry_items(filters, page, page_size)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"List jewelry items error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve jewelry items',
            'code': 'LIST_ERROR'
        }), 500


@jewelry_bp.route('/items/<item_id>', methods=['GET'])
def get_jewelry_item(item_id):
    """
    Get jewelry item by ID
    ---
    tags:
      - Jewelry
    parameters:
      - in: path
        name: item_id
        type: string
        required: true
    responses:
      200:
        description: Jewelry item retrieved successfully
      404:
        description: Jewelry item not found
    """
    try:
        jewelry_service = get_jewelry_service()
        item = jewelry_service.get_jewelry_item(item_id)
        
        if not item:
            return jsonify({
                'success': False,
                'error': 'Jewelry item not found',
                'code': 'ITEM_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'data': item
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get jewelry item error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve jewelry item',
            'code': 'GET_ERROR'
        }), 500


@jewelry_bp.route('/items/code/<code>', methods=['GET'])
def get_jewelry_by_code(code):
    """
    Get jewelry item by code
    ---
    tags:
      - Jewelry
    parameters:
      - in: path
        name: code
        type: string
        required: true
    responses:
      200:
        description: Jewelry item retrieved successfully
      404:
        description: Jewelry item not found
    """
    try:
        jewelry_service = get_jewelry_service()
        item = jewelry_service.get_jewelry_by_code(code)
        
        if not item:
            return jsonify({
                'success': False,
                'error': 'Jewelry item not found',
                'code': 'ITEM_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'data': item
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get jewelry by code error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve jewelry item',
            'code': 'GET_ERROR'
        }), 500


@jewelry_bp.route('/my-items', methods=['GET'])
@member_required
def get_my_jewelry_items():
    """
    Get current user's jewelry items
    ---
    tags:
      - Jewelry
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
        description: User's jewelry items retrieved successfully
      401:
        description: Authentication required
    """
    try:
        user_id = get_current_user()
        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)
        
        jewelry_service = get_jewelry_service()
        result = jewelry_service.get_user_jewelry_items(user_id, page, page_size)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get my jewelry items error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve jewelry items',
            'code': 'GET_MY_ITEMS_ERROR'
        }), 500


@jewelry_bp.route('/items/<item_id>', methods=['PUT'])
@member_required
def update_jewelry_item(item_id):
    """
    Update jewelry item
    ---
    tags:
      - Jewelry
    security:
      - Bearer: []
    parameters:
      - in: path
        name: item_id
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            attributes:
              type: object
            photos:
              type: array
              items:
                type: string
            estimated_price:
              type: number
            reserve_price:
              type: number
    responses:
      200:
        description: Jewelry item updated successfully
      401:
        description: Authentication required
      403:
        description: Not authorized
      404:
        description: Jewelry item not found
    """
    try:
        data = request.get_json() or {}
        user_id = get_current_user()
        user_role = get_current_user_role()
        
        jewelry_service = get_jewelry_service()
        result = jewelry_service.update_jewelry_item(item_id, user_id, user_role, data)
        
        return jsonify({
            'success': True,
            'message': 'Jewelry item updated successfully',
            'data': result
        }), 200
        
    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'ITEM_NOT_FOUND'
        }), 404
    except AuthorizationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'NOT_AUTHORIZED'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Update jewelry item error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update jewelry item',
            'code': 'UPDATE_ERROR'
        }), 500
