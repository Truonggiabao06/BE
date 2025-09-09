"""
Sell Request API controller for the Jewelry Auction System
"""
from flask import Blueprint, request, jsonify, current_app
from marshmallow import ValidationError as MarshmallowValidationError
from api.middleware.auth_middleware import jwt_required, member_required, staff_required, manager_required, get_current_user, get_current_user_role
from services.jewelry_service import JewelryService
from infrastructure.repositories.jewelry_repository import JewelryItemRepository
from infrastructure.repositories.sell_request_repository import SellRequestRepository
from infrastructure.databases.mssql import get_db_session
from domain.enums import SellRequestStatus, UserRole
from domain.exceptions import (
    ValidationError,
    NotFoundError,
    BusinessRuleViolationError,
    AuthorizationError
)

# Create blueprint
sell_request_bp = Blueprint('sell_requests', __name__, url_prefix='/api/v1/sell-requests')

def get_jewelry_service():
    """Get jewelry service instance"""
    session = get_db_session()
    jewelry_repository = JewelryItemRepository(session)
    sell_request_repository = SellRequestRepository(session)
    return JewelryService(jewelry_repository, sell_request_repository)


@sell_request_bp.route('', methods=['POST'])
@member_required
def create_sell_request():
    """
    Create a new sell request
    ---
    tags:
      - Sell Requests
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
        description: Sell request created successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
              properties:
                id:
                  type: string
                status:
                  type: string
                jewelry_item:
                  type: object
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
            'message': 'Sell request created successfully',
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
        current_app.logger.error(f"Create sell request error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create sell request',
            'code': 'CREATE_ERROR'
        }), 500


@sell_request_bp.route('', methods=['GET'])
@staff_required
def list_sell_requests():
    """
    List sell requests with filtering
    ---
    tags:
      - Sell Requests
    security:
      - Bearer: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: limit
        type: integer
        default: 20
      - in: query
        name: status
        type: string
        enum: [SUBMITTED, PRELIM_APPRAISED, RECEIVED, FINAL_APPRAISED, MANAGER_APPROVED, SELLER_ACCEPTED, ASSIGNED_TO_SESSION, REJECTED]
    responses:
      200:
        description: Sell requests retrieved successfully
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
    """
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = min(int(request.args.get('limit', 20)), 100)  # Max 100 items per page
        
        # Build filters
        filters = {}
        
        if request.args.get('status'):
            try:
                status = SellRequestStatus(request.args.get('status'))
                filters['status'] = status
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid status value',
                    'code': 'INVALID_STATUS'
                }), 400
        
        jewelry_service = get_jewelry_service()
        result = jewelry_service.list_sell_requests(filters, page, limit)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"List sell requests error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve sell requests',
            'code': 'LIST_ERROR'
        }), 500


@sell_request_bp.route('/<request_id>/final-approve', methods=['POST'])
@manager_required
def final_approve_sell_request(request_id):
    """
    Final approve a sell request (MANAGER only)
    ---
    tags:
      - Sell Requests
    security:
      - Bearer: []
    parameters:
      - in: path
        name: request_id
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            manager_notes:
              type: string
              example: "Approved for auction"
    responses:
      200:
        description: Sell request approved successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            data:
              type: object
      404:
        description: Sell request not found
      403:
        description: Not authorized or invalid status
    """
    try:
        data = request.get_json() or {}
        user_id = get_current_user()

        jewelry_service = get_jewelry_service()
        result = jewelry_service.final_approve_sell_request(
            request_id,
            user_id,
            data.get('manager_notes', '')
        )

        return jsonify({
            'success': True,
            'message': 'Sell request approved successfully',
            'data': result
        }), 200

    except NotFoundError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'REQUEST_NOT_FOUND'
        }), 404
    except BusinessRuleViolationError as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'code': 'BUSINESS_RULE_VIOLATION'
        }), 403
    except Exception as e:
        current_app.logger.error(f"Final approve sell request error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to approve sell request',
            'code': 'APPROVE_ERROR'
        }), 500
