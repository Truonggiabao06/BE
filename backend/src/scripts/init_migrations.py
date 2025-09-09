#!/usr/bin/env python3
"""
Initialize database migrations for the Jewelry Auction System
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from config import config_by_name
from infrastructure.databases.mssql import db
from infrastructure.models import *  # Import all models


def create_app():
    """Create Flask app for migration"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = os.environ.get('APP_ENV', 'development')
    config_class = config_by_name.get(config_name)
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    return app


def init_migrations():
    """Initialize migrations"""
    app = create_app()
    migrate_obj = Migrate(app, db)
    
    with app.app_context():
        try:
            # Initialize migration repository
            init()
            print("✓ Migration repository initialized")
            
            # Create initial migration
            migrate(message="Initial migration - Jewelry Auction System")
            print("✓ Initial migration created")
            
            # Apply migrations
            upgrade()
            print("✓ Migrations applied successfully")
            
        except Exception as e:
            print(f"Error during migration initialization: {e}")
            return False
    
    return True


if __name__ == "__main__":
    print("Initializing database migrations...")
    success = init_migrations()
    
    if success:
        print("\n✓ Database migrations initialized successfully!")
        print("You can now use:")
        print("  flask db migrate -m 'description'  # Create new migration")
        print("  flask db upgrade                   # Apply migrations")
        print("  flask db downgrade                 # Rollback migrations")
    else:
        print("\n✗ Failed to initialize migrations")
        sys.exit(1)
