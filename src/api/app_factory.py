from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import Config
from src.api.controllers.auth_controller import AuthController, auth_bp
from src.api.controllers.auction_item_controller import AuctionItemController, auction_item_bp
from src.api.controllers.auction_session_controller import AuctionSessionController, auction_session_bp
from src.api.controllers.bid_controller import BidController, bid_bp
from src.api.controllers.payment_controller import PaymentController, payment_bp
from src.api.controllers.staff_controller import StaffController, staff_bp
from src.api.controllers.manager_controller import ManagerController, manager_bp
from src.api.controllers.dashboard_controller import DashboardController, dashboard_bp
from src.api.controllers.notification_controller import NotificationController, notification_bp
from src.api.middleware.auth_middleware import AuthMiddleware

# Import services and repositories
from src.infrastructure.services.auth_service_impl import AuthService
from src.infrastructure.services.mock_email_service import MockEmailService
from src.infrastructure.repositories.user_repository_impl import UserRepository
from src.infrastructure.repositories.verification_code_repository_impl import VerificationCodeRepository
from src.infrastructure.repositories.auction_item_repository_impl import AuctionItemRepository
from src.infrastructure.repositories.auction_session_repository_impl import AuctionSessionRepository
from src.infrastructure.repositories.bid_repository_impl import BidRepository
from src.infrastructure.repositories.payment_repository_impl import PaymentRepository
from src.infrastructure.repositories.fee_config_repository_impl import FeeConfigRepository
from src.infrastructure.repositories.notification_repository_impl import NotificationRepository
from src.infrastructure.repositories.user_repository_impl import UserRepository

def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable CORS - Allow all origins for development
    CORS(app,
         origins="*",
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Initialize database
    engine = create_engine(app.config['DATABASE_URI'])
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Initialize services
    def get_session():
        return SessionLocal()
    
    def get_auth_service():
        session = get_session()
        user_repo = UserRepository(session)
        verification_repo = VerificationCodeRepository(session)
        email_service = MockEmailService()
        
        return AuthService(
            user_repository=user_repo,
            verification_code_repository=verification_repo,
            email_service=email_service,
            jwt_secret=app.config.get('JWT_SECRET_KEY', 'your-secret-key'),
            jwt_expiry_hours=24
        )
    
    # Initialize controllers
    auth_service = get_auth_service()
    auth_controller = AuthController(auth_service)

    # Initialize auction item controller
    def get_auction_item_service():
        session = get_session()
        return AuctionItemRepository(session)

    auction_item_service = get_auction_item_service()
    auction_item_controller = AuctionItemController(auction_item_service)

    # Initialize auction session controller
    def get_auction_session_service():
        session = get_session()
        return AuctionSessionRepository(session)

    auction_session_service = get_auction_session_service()
    auction_session_controller = AuctionSessionController(auction_session_service, auction_item_service)

    # Initialize bid controller
    def get_bid_service():
        session = get_session()
        return BidRepository(session)

    bid_service = get_bid_service()
    bid_controller = BidController(bid_service, auction_session_service, auction_item_service)

    # Initialize payment controller
    def get_payment_service():
        session = get_session()
        return PaymentRepository(session)

    payment_service = get_payment_service()
    payment_controller = PaymentController(payment_service, auction_session_service, bid_service)

    # Initialize staff controller
    staff_controller = StaffController(auction_item_service)

    # Initialize manager controller
    def get_fee_config_service():
        session = get_session()
        return FeeConfigRepository(session)

    fee_config_service = get_fee_config_service()
    manager_controller = ManagerController(auction_item_service, fee_config_service)

    # Initialize dashboard controller
    def get_user_service():
        session = get_session()
        return UserRepository(session)

    user_service = get_user_service()
    dashboard_controller = DashboardController(auction_item_service, auction_session_service, payment_service, user_service)

    # Initialize notification controller
    def get_notification_service():
        session = get_session()
        return NotificationRepository(session)

    notification_service = get_notification_service()
    notification_controller = NotificationController(notification_service)

    # Initialize middleware
    auth_middleware = AuthMiddleware(app)
    
    # Initialize Swagger with Flasgger - Very simple configuration
    swagger = Swagger(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(auction_item_bp)
    app.register_blueprint(auction_session_bp)
    app.register_blueprint(bid_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(notification_bp)
    
    # Simple docs endpoint for testing
    @app.route('/api-docs')
    def api_docs():
        """Simple API documentation"""
        return '''
        <html>
        <head><title>Jewelry Auction System API</title></head>
        <body>
            <h1>Jewelry Auction System API</h1>
            <h2>Available Endpoints:</h2>
            <ul>
                <li><strong>GET /api</strong> - API information</li>
                <li><strong>POST /api/auth/register</strong> - Register new user</li>
                <li><strong>POST /api/auth/login</strong> - Login user</li>
                <li><strong>GET /api/auction-items</strong> - Get all auction items</li>
                <li><strong>POST /api/auction-items</strong> - Create auction item (requires auth)</li>
                <li><strong>GET /api/auction-sessions</strong> - Get all auction sessions</li>
                <li><strong>POST /api/bids</strong> - Place a bid (requires auth)</li>
                <li><strong>GET /health</strong> - Health check</li>
            </ul>
            <p><a href="/api">Test API endpoint</a></p>
            <p><a href="/docs">Swagger UI Documentation</a></p>
        </body>
        </html>
        '''

    # Serve frontend demo page
    @app.route('/')
    def index():
        """Serve the frontend demo page"""
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend_demo')
        return send_from_directory(frontend_dir, 'index.html')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {"status": "healthy", "message": "Auction System API is running"}, 200

    # API info endpoint
    @app.route('/api')
    def api_info():
        return {
            "name": "Jewelry Auction System API",
            "version": "1.0.0",
            "description": "REST API for Jewelry Auction System",
            "documentation": {
                "swagger_ui": "/docs",
                "swagger_json": "/apispec.json",
                "api_docs": "/api-docs"
            },
            "endpoints": {
                "auth": "/api/auth",
                "auction_items": "/api/auction-items",
                "auction_sessions": "/api/auction-sessions",
                "bids": "/api/bids",
                "payments": "/api/payments",
                "staff": "/api/staff",
                "manager": "/api/manager",
                "dashboard": "/api/dashboard",
                "notifications": "/api/notifications",
                "health": "/health"
            }
        }, 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        # Check if request expects JSON
        if request.is_json or 'application/json' in request.headers.get('Accept', ''):
            return {
                "success": False,
                "message": "Endpoint not found",
                "data": None
            }, 404
        # For HTML requests, let Flask handle it normally
        return error
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {
            "success": False,
            "message": "Method not allowed",
            "data": None
        }, 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            "success": False,
            "message": "Internal server error",
            "data": None
        }, 500
    
    return app
