#!/usr/bin/env python3
"""
Database initialization script for the Jewelry Auction System
"""
import os
import sys
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from infrastructure.databases.base import Base
from infrastructure.models import *  # Import all models
from domain.enums import UserRole
from infrastructure.services.auth_service import AuthService

# Load environment variables
load_dotenv()

def create_database_if_not_exists(db_url: str):
    """Create database if it doesn't exist (for MySQL)"""
    if 'mysql' in db_url:
        # Extract database name and connection without database
        parts = db_url.split('/')
        db_name = parts[-1]
        base_url = '/'.join(parts[:-1])
        
        # Connect without specifying database
        engine = create_engine(base_url)
        with engine.connect() as conn:
            # Check if database exists
            result = conn.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
            if not result.fetchone():
                # Create database
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"Created database: {db_name}")
            else:
                print(f"Database {db_name} already exists")

def init_database():
    """Initialize database with tables and seed data"""
    db_url = os.environ.get('DB_URL') or os.environ.get('DATABASE_URI')
    
    if not db_url:
        print("Error: DB_URL or DATABASE_URI environment variable not set")
        return False
    
    print(f"Initializing database: {db_url}")
    
    try:
        # Create database if it doesn't exist (MySQL only)
        create_database_if_not_exists(db_url)
        
        # Create engine and tables
        engine = create_engine(db_url)
        
        # Drop all tables (for fresh start)
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Seed initial data
        print("Seeding initial data...")
        seed_data(engine)
        
        print("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False

def seed_data(engine):
    """Seed initial data"""
    from sqlalchemy.orm import sessionmaker
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create admin user
        admin_password_hash = AuthService.hash_password("Admin123!")
        admin_user = UserModel(
            name="System Administrator",
            email="admin@jewelryauction.com",
            password_hash=admin_password_hash,
            role=UserRole.ADMIN,
            is_active=True,
            email_verified=True,
            email_verified_at=datetime.utcnow()
        )
        session.add(admin_user)
        
        # Create manager user
        manager_password_hash = AuthService.hash_password("Manager123!")
        manager_user = UserModel(
            name="Auction Manager",
            email="manager@jewelryauction.com",
            password_hash=manager_password_hash,
            role=UserRole.MANAGER,
            is_active=True,
            email_verified=True,
            email_verified_at=datetime.utcnow()
        )
        session.add(manager_user)
        
        # Create staff user
        staff_password_hash = AuthService.hash_password("Staff123!")
        staff_user = UserModel(
            name="Auction Staff",
            email="staff@jewelryauction.com",
            password_hash=staff_password_hash,
            role=UserRole.STAFF,
            is_active=True,
            email_verified=True,
            email_verified_at=datetime.utcnow()
        )
        session.add(staff_user)
        
        # Create demo member user
        member_password_hash = AuthService.hash_password("Member123!")
        member_user = UserModel(
            name="Demo Member",
            email="member@jewelryauction.com",
            password_hash=member_password_hash,
            role=UserRole.MEMBER,
            is_active=True,
            email_verified=True,
            email_verified_at=datetime.utcnow()
        )
        session.add(member_user)
        
        # Create default transaction fee structure
        default_fee = TransactionFeeModel(
            name="Standard Fee Structure",
            description="Default fee structure for all transactions",
            buyer_percentage=10.0,  # 10% buyer premium
            seller_percentage=5.0,   # 5% seller commission
            min_fee=1.00,
            max_fee=1000.00,
            is_active=True
        )
        session.add(default_fee)
        
        # Create sample policies
        terms_policy = PolicyModel(
            slug="terms-of-service",
            title="Terms of Service",
            content="Terms of service content goes here...",
            is_published=True,
            published_at=datetime.utcnow()
        )
        session.add(terms_policy)
        
        privacy_policy = PolicyModel(
            slug="privacy-policy",
            title="Privacy Policy",
            content="Privacy policy content goes here...",
            is_published=True,
            published_at=datetime.utcnow()
        )
        session.add(privacy_policy)
        
        # Commit all changes
        session.commit()
        
        print("Seed data created successfully!")
        print("\nDefault users created:")
        print("- Admin: admin@jewelryauction.com / Admin123!")
        print("- Manager: manager@jewelryauction.com / Manager123!")
        print("- Staff: staff@jewelryauction.com / Staff123!")
        print("- Member: member@jewelryauction.com / Member123!")
        
    except Exception as e:
        session.rollback()
        print(f"Error seeding data: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    print("Jewelry Auction System - Database Initialization")
    print("=" * 50)
    
    if init_database():
        print("\n✅ Database initialization completed successfully!")
        print("\nYou can now start the application with: python run.py")
    else:
        print("\n❌ Database initialization failed!")
        sys.exit(1)
