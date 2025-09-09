#!/usr/bin/env python3
"""
Main Flask application for Jewelry Auction System
"""
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from dotenv import load_dotenv

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Load environment variables
load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from config import config_by_name
from infrastructure.databases.mssql import init_mssql, db
from flasgger import Swagger


def create_app():
    """Create Flask application"""
    app = Flask(__name__)

    # Load configuration
    config_name = os.environ.get('APP_ENV', 'development')
    config_class = config_by_name.get(config_name)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app, origins=["*"], allow_headers=["*"], methods=["*"])
    jwt = JWTManager(app)

    # Initialize database
    try:
        init_mssql(app)
        print("✅ SQL Server database initialized successfully!")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

    # Initialize Swagger
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

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Jewelry Auction System API",
            "description": "API for jewelry auction system",
            "version": "1.0.0"
        },
        "basePath": "/api/v1",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
            }
        },
        "security": [
            {
                "Bearer": []
            }
        ]
    }

    swagger = Swagger(app, config=swagger_config, template=swagger_template)

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authentication required'}), 401

    # Handle preflight requests
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({'status': 'ok'})
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add('Access-Control-Allow-Headers', "*")
            response.headers.add('Access-Control-Allow-Methods', "*")
            return response

    # Routes
    @app.route('/')
    def home():
        """
        Home endpoint
        ---
        responses:
          200:
            description: Welcome message
        """
        return jsonify({
            'message': 'Welcome to Jewelry Auction System API',
            'version': '1.0.0',
            'endpoints': {
                'documentation': '/api/docs',
                'health': '/health',
                'auth': '/api/v1/auth',
                'users': '/api/v1/users',
                'jewelry': '/api/v1/jewelry',
                'auctions': '/api/v1/auctions'
            }
        })

    @app.route('/health')
    def health_check():
        """
        Health check endpoint
        ---
        responses:
          200:
            description: Service health status
        """
        try:
            # Test database connection
            result = db.session.execute(db.text("SELECT 1 as test"))
            db_status = "connected"
        except Exception as e:
            db_status = f"error: {str(e)}"

        return jsonify({
            'status': 'healthy',
            'service': 'Jewelry Auction System API',
            'database': db_status,
            'timestamp': datetime.utcnow().isoformat()
        })

    # Auth endpoints are now handled by auth_controller blueprint

    # User endpoints
    @app.route('/api/v1/users/profile', methods=['GET'])
    @jwt_required()
    def get_profile():
        """
        Get user profile
        ---
        security:
          - Bearer: []
        responses:
          200:
            description: User profile
          401:
            description: Authentication required
        """
        current_user = get_jwt_identity()
        return jsonify({
            'email': current_user,
            'profile': {
                'id': 1 if current_user == 'admin@jewelry.com' else 2,
                'email': current_user,
                'role': 'ADMIN' if current_user == 'admin@jewelry.com' else 'MEMBER',
                'name': 'Admin User' if current_user == 'admin@jewelry.com' else 'Test User',
                'created_at': '2024-01-01T00:00:00Z'
            }
        })

    # Jewelry endpoints
    @app.route('/api/v1/jewelry', methods=['GET'])
    def get_jewelry_items():
        """
        Get jewelry items
        ---
        parameters:
          - name: page
            in: query
            type: integer
            default: 1
          - name: limit
            in: query
            type: integer
            default: 20
        responses:
          200:
            description: List of jewelry items
        """
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)

        # Mock data
        jewelry_items = [
            {
                'id': 1,
                'title': 'Diamond Ring',
                'description': 'Beautiful 2-carat diamond ring',
                'category': 'Ring',
                'material': 'Gold',
                'weight': '5.2g',
                'estimated_value': 5000.00,
                'status': 'APPROVED',
                'images': ['ring1.jpg', 'ring2.jpg']
            },
            {
                'id': 2,
                'title': 'Pearl Necklace',
                'description': 'Elegant pearl necklace',
                'category': 'Necklace',
                'material': 'Pearl',
                'weight': '15.8g',
                'estimated_value': 1200.00,
                'status': 'APPROVED',
                'images': ['necklace1.jpg']
            }
        ]

        return jsonify({
            'items': jewelry_items,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': len(jewelry_items),
                'pages': 1
            }
        })

    # Auction endpoints
    @app.route('/api/v1/auctions', methods=['GET'])
    def get_auctions():
        """
        Get auction sessions
        ---
        parameters:
          - name: status
            in: query
            type: string
            enum: [DRAFT, SCHEDULED, OPEN, CLOSED]
        responses:
          200:
            description: List of auction sessions
        """
        status = request.args.get('status')

        # Mock data
        auctions = [
            {
                'id': 1,
                'title': 'Weekly Jewelry Auction #1',
                'description': 'Premium jewelry collection',
                'status': 'SCHEDULED',
                'start_time': '2024-12-30T14:00:00Z',
                'end_time': '2024-12-30T18:00:00Z',
                'total_items': 25,
                'total_estimated_value': 50000.00
            },
            {
                'id': 2,
                'title': 'Holiday Special Auction',
                'description': 'Special holiday jewelry auction',
                'status': 'OPEN',
                'start_time': '2024-12-25T10:00:00Z',
                'end_time': '2024-12-25T16:00:00Z',
                'total_items': 15,
                'total_estimated_value': 30000.00
            }
        ]

        if status:
            auctions = [a for a in auctions if a['status'] == status]

        return jsonify({
            'auctions': auctions,
            'total': len(auctions)
        })

    # Register additional blueprints
    try:
        from api.controllers.auth_controller import auth_bp
        app.register_blueprint(auth_bp)
        print("✅ Auth blueprint registered successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not register auth blueprint: {e}")

    try:
        from api.controllers.sell_request_controller import sell_request_bp
        app.register_blueprint(sell_request_bp)
        print("✅ Sell request blueprint registered successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not register sell request blueprint: {e}")

    try:
        from api.controllers.jewelry_controller import jewelry_bp
        app.register_blueprint(jewelry_bp)
        print("✅ Jewelry blueprint registered successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not register jewelry blueprint: {e}")

    try:
        from api.controllers.auction_controller import auction_bp
        app.register_blueprint(auction_bp)
        print("✅ Auction blueprint registered successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not register auction blueprint: {e}")

    try:
        from api.controllers.bid_controller import bid_bp
        app.register_blueprint(bid_bp)
        print("✅ Bid blueprint registered successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not register bid blueprint: {e}")

    try:
        from api.controllers.upload_controller import upload_bp
        app.register_blueprint(upload_bp)
        print("✅ Upload blueprint registered successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not register upload blueprint: {e}")

    return app


if __name__ == '__main__':
    app = create_app()

    print(f"🚀 Starting Jewelry Auction API...")
    print(f"📚 API Documentation: http://127.0.0.1:5000/api/docs")
    print(f"🔗 Health Check: http://127.0.0.1:5000/health")
    print(f"🔐 Login: POST http://127.0.0.1:5000/api/v1/auth/login")
    print(f"\n📝 Test credentials:")
    print(f"   Admin: admin@jewelry.com / admin123")
    print(f"   User:  user@jewelry.com / user123")

    app.run(host='127.0.0.1', port=5000, debug=True)