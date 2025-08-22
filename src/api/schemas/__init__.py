# API Schemas package
# Contains Marshmallow schemas for request/response validation and serialization

from .todo import TodoRequestSchema, TodoResponseSchema
from .user import UserRequestSchema, UserResponseSchema
from .auth import LoginRequestSchema, LoginResponseSchema, RegisterRequestSchema
from .common import PaginationSchema, ErrorResponseSchema

__all__ = [
    'TodoRequestSchema',
    'TodoResponseSchema', 
    'UserRequestSchema',
    'UserResponseSchema',
    'LoginRequestSchema',
    'LoginResponseSchema',
    'RegisterRequestSchema',
    'PaginationSchema',
    'ErrorResponseSchema'
]
