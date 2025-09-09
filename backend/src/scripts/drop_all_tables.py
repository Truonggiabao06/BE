#!/usr/bin/env python3
"""
Drop all tables script for the Jewelry Auction System
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from config import config_by_name
from infrastructure.databases.mssql import db
from sqlalchemy import text


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


def drop_all_tables():
    """Drop all tables in the database"""
    app = create_app()

    with app.app_context():
        try:
            # First, drop all foreign key constraints
            print("Dropping foreign key constraints...")
            db.session.execute(text("""
                DECLARE @sql NVARCHAR(MAX) = N'';
                SELECT @sql = @sql + N'ALTER TABLE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(OBJECT_NAME(parent_object_id)) +
                              N' DROP CONSTRAINT ' + QUOTENAME(name) + N';' + CHAR(13)
                FROM sys.foreign_keys;
                EXEC sp_executesql @sql;
            """))
            db.session.commit()
            print("✅ Foreign key constraints dropped")

            # Then drop all tables
            print("Dropping all tables...")
            db.session.execute(text("""
                DECLARE @sql NVARCHAR(MAX) = N'';
                SELECT @sql = @sql + N'DROP TABLE ' + QUOTENAME(SCHEMA_NAME(schema_id)) + N'.' + QUOTENAME(name) + N';' + CHAR(13)
                FROM sys.tables;
                EXEC sp_executesql @sql;
            """))
            db.session.commit()

            print("✅ All tables dropped successfully!")
            return True

        except Exception as e:
            print(f"❌ Error dropping tables: {str(e)}")
            db.session.rollback()
            return False


if __name__ == "__main__":
    print("Dropping all tables...")
    success = drop_all_tables()
    
    if success:
        print("\n✅ All tables dropped successfully!")
        print("You can now run 'flask db upgrade' to create fresh tables")
    else:
        print("\n❌ Failed to drop tables")
        sys.exit(1)
