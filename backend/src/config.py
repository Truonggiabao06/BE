# Configuration settings for the Jewelry Auction System

import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jewelry-auction-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    TESTING = os.environ.get('TESTING', 'False').lower() in ['true', '1']

    # Database Configuration
    DB_URL = os.environ.get('DB_URL') or 'mssql+pyodbc://sa:Giabao06%40@localhost:1433/jewelry_auction?driver=ODBC+Driver+17+for+SQL+Server'
    DATABASE_URI = DB_URL  # Keep backward compatibility
    SQLALCHEMY_DATABASE_URI = DB_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    JWT_ALGORITHM = 'HS256'

    # Application Environment
    APP_ENV = os.environ.get('APP_ENV', 'development')

    # CORS Configuration
    CORS_HEADERS = 'Content-Type'
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']

    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Email Configuration (stubs for now)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DB_URL = os.environ.get('DB_URL') or 'mssql+pyodbc://sa:Giabao06%40@localhost:1433/jewelry_auction_dev?driver=ODBC+Driver+17+for+SQL+Server'
    SQLALCHEMY_DATABASE_URI = DB_URL
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Longer for development


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DB_URL = os.environ.get('DB_URL') or 'sqlite:///test_jewelry_auction.db'
    SQLALCHEMY_DATABASE_URI = DB_URL
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)  # Short for testing
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    DB_URL = os.environ.get('DB_URL') or 'mssql+pyodbc://sa:Giabao06%40@prod-host:1433/jewelry_auction_prod?driver=ODBC+Driver+17+for+SQL+Server'
    SQLALCHEMY_DATABASE_URI = DB_URL
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


class SwaggerConfig:
    """Swagger configuration for Jewelry Auction API."""
    template = {
        "swagger": "2.0",
        "info": {
            "title": "Jewelry Auction System API",
            "description": "RESTful API for managing jewelry auctions, bidding, and transactions",
            "version": "1.0.0",
            "contact": {
                "name": "Jewelry Auction System",
                "email": "support@jewelryauction.com"
            }
        },
        "basePath": "/api/v1",
        "schemes": [
            "http",
            "https"
        ],
        "consumes": [
            "application/json"
        ],
        "produces": [
            "application/json"
        ],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        }
    }

    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/api/docs"
    }


# Configuration mapping
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}