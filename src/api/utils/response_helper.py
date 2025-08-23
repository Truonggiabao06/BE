from flask import jsonify
from typing import Any, Dict, Optional, Union

def success_response(message: str = "Success", data: Optional[Any] = None, status_code: int = 200):
    """Create a standardized success response"""
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), status_code

def error_response(message: Union[str, Dict], status_code: int = 400):
    """Create a standardized error response"""
    if isinstance(message, dict):
        response = {
            "success": False,
            **message
        }
    else:
        response = {
            "success": False,
            "message": message,
            "data": None
        }
    return jsonify(response), status_code

def validation_error_response(message: str, errors: Optional[Dict] = None):
    """Create a validation error response"""
    response = {
        "success": False,
        "message": message,
        "errors": errors,
        "data": None
    }
    return jsonify(response), 422

def not_found_response(message: str = "Resource not found"):
    """Create a not found response"""
    response = {
        "success": False,
        "message": message,
        "data": None
    }
    return jsonify(response), 404

def unauthorized_response(message: str = "Unauthorized"):
    """Create an unauthorized response"""
    response = {
        "success": False,
        "message": message,
        "data": None
    }
    return jsonify(response), 401

def forbidden_response(message: str = "Forbidden"):
    """Create a forbidden response"""
    response = {
        "success": False,
        "message": message,
        "data": None
    }
    return jsonify(response), 403

def internal_server_error_response(message: str = "Internal server error"):
    """Create an internal server error response"""
    response = {
        "success": False,
        "message": message,
        "data": None
    }
    return jsonify(response), 500

def paginated_response(data: list, page: int, limit: int, total: int, message: str = "Success"):
    """Create a paginated response"""
    response = {
        "success": True,
        "message": message,
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit,  # Ceiling division
            "has_next": page * limit < total,
            "has_prev": page > 1
        }
    }
    return jsonify(response), 200
