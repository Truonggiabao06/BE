#!/usr/bin/env python3
"""
Database migration script for auction system tables.
This script creates all the necessary tables for the jewelry auction system.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from src.config import Config
from infrastructure.databases.base import Base

# Import all models to ensure they are registered
from infrastructure.models.user_model import UserModel
from infrastructure.models.auction_item_model import AuctionItemModel
from infrastructure.models.auction_session_model import AuctionSessionModel
from infrastructure.models.bid_model import BidModel
from infrastructure.models.payment_model import PaymentModel

def create_tables():
    """Create all auction system tables"""
    print("🚀 Starting database migration for auction system...")
    
    # Create database engine
    engine = create_engine(Config.DATABASE_URI)
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Create all tables
        print("📊 Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # List created tables
        with engine.connect() as conn:
            if 'mssql' in Config.DATABASE_URI.lower():
                # SQL Server query
                result = conn.execute(text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_TYPE = 'BASE TABLE' 
                    AND TABLE_SCHEMA = 'dbo'
                    ORDER BY TABLE_NAME
                """))
            else:
                # Generic SQL query
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """))
            
            tables = [row[0] for row in result]
            print(f"\n📋 Created tables ({len(tables)}):")
            for table in tables:
                print(f"   • {table}")
        
        print("\n🎉 Database migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        raise

def drop_tables():
    """Drop all auction system tables (use with caution!)"""
    print("⚠️  WARNING: This will drop all auction system tables!")
    confirm = input("Are you sure? Type 'yes' to continue: ")
    
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled")
        return
    
    engine = create_engine(Config.DATABASE_URI)
    
    try:
        print("🗑️  Dropping tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully!")
        
    except Exception as e:
        print(f"❌ Error during table drop: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Auction system database migration")
    parser.add_argument("--drop", action="store_true", help="Drop all tables (dangerous!)")
    parser.add_argument("--create", action="store_true", help="Create all tables")
    
    args = parser.parse_args()
    
    if args.drop:
        drop_tables()
    elif args.create:
        create_tables()
    else:
        # Default action: create tables
        create_tables()
