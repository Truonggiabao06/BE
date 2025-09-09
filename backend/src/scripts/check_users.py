#!/usr/bin/env python3
"""
Check users in database
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from config import config_by_name
from infrastructure.databases.mssql import db
from infrastructure.models import UserModel
from werkzeug.security import check_password_hash


def create_app():
    """Create Flask app"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = os.environ.get('APP_ENV', 'development')
    config_class = config_by_name.get(config_name)
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    return app


def main():
    """Check users"""
    app = create_app()
    
    with app.app_context():
        users = UserModel.query.all()
        
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"- {user.email} ({user.role.value}) - Active: {user.is_active}")
            
            # Test password
            if user.email == 'admin@example.com':
                is_valid = check_password_hash(user.password_hash, 'Admin@123')
                print(f"  Password check: {'✅ Valid' if is_valid else '❌ Invalid'}")


if __name__ == "__main__":
    main()
