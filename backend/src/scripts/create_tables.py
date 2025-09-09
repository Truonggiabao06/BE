#!/usr/bin/env python3
"""
Create all tables script for the Jewelry Auction System
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from config import config_by_name
from infrastructure.databases.mssql import db
from infrastructure.databases.base import Base

# Import all models to ensure they are registered
from infrastructure.models import *


def create_app():
    """Create Flask app for database operations"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = os.environ.get('APP_ENV', 'development')
    config_class = config_by_name.get(config_name)
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    return app


def create_all_tables():
    """Create all tables in the database"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Creating all tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ All tables created successfully!")
            
            # List created tables
            from sqlalchemy import text
            result = db.session.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"))
            tables = [row[0] for row in result]
            
            print(f"\n📋 Created tables ({len(tables)}):")
            for table in sorted(tables):
                print(f"  - {table}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {str(e)}")
            return False


if __name__ == "__main__":
    print("Creating all tables...")
    success = create_all_tables()
    
    if success:
        print("\n✅ Database tables created successfully!")
    else:
        print("\n❌ Failed to create tables")
        sys.exit(1)
