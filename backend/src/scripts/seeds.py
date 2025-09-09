#!/usr/bin/env python3
"""
Seed data script for the Jewelry Auction System
"""
import os
import sys
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from config import config_by_name
from infrastructure.databases.mssql import db
from infrastructure.models import *
from domain.enums import UserRole, JewelryStatus, SellRequestStatus, SessionStatus
from infrastructure.services.auth_service import AuthService


def create_app():
    """Create Flask app for seeding"""
    app = Flask(__name__)
    
    # Load configuration
    config_name = os.environ.get('APP_ENV', 'development')
    config_class = config_by_name.get(config_name)
    app.config.from_object(config_class)
    
    # Initialize database
    db.init_app(app)
    
    return app


def seed_users():
    """Seed admin and member users"""
    print("Seeding users...")
    
    # Admin user
    admin = UserModel.query.filter_by(email='admin@example.com').first()
    if not admin:
        admin = UserModel(
            name='Admin User',
            email='admin@example.com',
            password_hash=AuthService.hash_password('Admin@123'),
            role=UserRole.ADMIN,
            is_active=True,
            phone='+1234567890',
            address='123 Admin Street, Admin City'
        )
        db.session.add(admin)
        print("✅ Created admin user: admin@example.com / Admin@123")
    
    # Member user
    member = UserModel.query.filter_by(email='member@example.com').first()
    if not member:
        member = UserModel(
            name='Member User',
            email='member@example.com',
            password_hash=AuthService.hash_password('Member@123'),
            role=UserRole.MEMBER,
            is_active=True,
            phone='+1234567891',
            address='456 Member Street, Member City'
        )
        db.session.add(member)
        print("✅ Created member user: member@example.com / Member@123")
    
    # Staff user
    staff = UserModel.query.filter_by(email='staff@example.com').first()
    if not staff:
        staff = UserModel(
            name='Staff User',
            email='staff@example.com',
            password_hash=AuthService.hash_password('Staff@123'),
            role=UserRole.STAFF,
            is_active=True,
            phone='+1234567892',
            address='789 Staff Street, Staff City'
        )
        db.session.add(staff)
        print("✅ Created staff user: staff@example.com / Staff@123")
    
    # Manager user
    manager = UserModel.query.filter_by(email='manager@example.com').first()
    if not manager:
        manager = UserModel(
            name='Manager User',
            email='manager@example.com',
            password_hash=AuthService.hash_password('Manager@123'),
            role=UserRole.MANAGER,
            is_active=True,
            phone='+1234567893',
            address='101 Manager Street, Manager City'
        )
        db.session.add(manager)
        print("✅ Created manager user: manager@example.com / Manager@123")
    
    db.session.commit()


def seed_jewelry_items():
    """Seed sample jewelry items"""
    print("Seeding jewelry items...")
    
    member = UserModel.query.filter_by(email='member@example.com').first()
    if not member:
        print("❌ Member user not found, skipping jewelry items")
        return
    
    # Diamond Ring
    ring = JewelryItemModel.query.filter_by(code='JWL001').first()
    if not ring:
        ring = JewelryItemModel(
            code='JWL001',
            title='Diamond Engagement Ring',
            description='Beautiful 2-carat diamond engagement ring with platinum band',
            attributes={
                'material': 'Platinum',
                'stone': 'Diamond',
                'carat': '2.0',
                'cut': 'Round Brilliant',
                'clarity': 'VS1',
                'color': 'G'
            },
            weight=Decimal('8.5'),
            photos=['ring1.jpg', 'ring2.jpg', 'ring3.jpg'],
            owner_user_id=member.id,
            status=JewelryStatus.APPROVED,
            estimated_price=Decimal('15000.00'),
            reserve_price=Decimal('12000.00')
        )
        db.session.add(ring)
        print("✅ Created jewelry item: Diamond Engagement Ring")
    
    # Pearl Necklace
    necklace = JewelryItemModel.query.filter_by(code='JWL002').first()
    if not necklace:
        necklace = JewelryItemModel(
            code='JWL002',
            title='Vintage Pearl Necklace',
            description='Elegant vintage pearl necklace with gold clasp',
            attributes={
                'material': 'Gold',
                'stone': 'Pearl',
                'length': '18 inches',
                'pearl_size': '8-9mm',
                'origin': 'Cultured'
            },
            weight=Decimal('25.3'),
            photos=['necklace1.jpg', 'necklace2.jpg'],
            owner_user_id=member.id,
            status=JewelryStatus.APPROVED,
            estimated_price=Decimal('3500.00'),
            reserve_price=Decimal('2800.00')
        )
        db.session.add(necklace)
        print("✅ Created jewelry item: Vintage Pearl Necklace")
    
    db.session.commit()


def seed_sell_requests():
    """Seed sample sell requests"""
    print("Seeding sell requests...")
    
    member = UserModel.query.filter_by(email='member@example.com').first()
    ring = JewelryItemModel.query.filter_by(code='JWL001').first()
    
    if not member or not ring:
        print("❌ Required data not found, skipping sell requests")
        return
    
    # Sell request for diamond ring
    sell_request = SellRequestModel.query.filter_by(jewelry_item_id=ring.id).first()
    if not sell_request:
        sell_request = SellRequestModel(
            seller_id=member.id,
            jewelry_item_id=ring.id,
            status=SellRequestStatus.MANAGER_APPROVED,
            notes='Initial sell request for diamond ring',
            seller_notes='Inherited from grandmother, excellent condition',
            staff_notes='Verified authenticity and condition',
            manager_notes='Approved for auction',
            submitted_at=datetime.utcnow() - timedelta(days=7),
            appraised_at=datetime.utcnow() - timedelta(days=5),
            approved_at=datetime.utcnow() - timedelta(days=2)
        )
        db.session.add(sell_request)
        print("✅ Created sell request for diamond ring")
    
    db.session.commit()


def seed_auction_session():
    """Seed sample auction session"""
    print("Seeding auction session...")
    
    manager = UserModel.query.filter_by(email='manager@example.com').first()
    ring = JewelryItemModel.query.filter_by(code='JWL001').first()
    
    if not manager or not ring:
        print("❌ Required data not found, skipping auction session")
        return
    
    # Auction session
    session = AuctionSessionModel.query.filter_by(code='AUC001').first()
    if not session:
        session = AuctionSessionModel(
            code='AUC001',
            name='Weekly Jewelry Auction #1',
            description='Premium jewelry collection featuring diamonds and pearls',
            start_at=datetime.utcnow() + timedelta(days=1),
            end_at=datetime.utcnow() + timedelta(days=1, hours=4),
            status=SessionStatus.DRAFT,
            assigned_staff_id=manager.id,
            rules={
                'bid_increment': 100,
                'registration_required': True,
                'preview_hours': 2
            }
        )
        db.session.add(session)
        db.session.commit()
        
        # Session item
        session_item = SessionItemModel(
            session_id=session.id,
            jewelry_item_id=ring.id,
            reserve_price=ring.reserve_price,
            start_price=Decimal('1000.00'),
            step_price=Decimal('100.00'),
            lot_number=1
        )
        db.session.add(session_item)
        print("✅ Created auction session: Weekly Jewelry Auction #1")
    
    db.session.commit()


def main():
    """Main seeding function"""
    app = create_app()
    
    with app.app_context():
        try:
            print("🌱 Starting database seeding...")
            
            seed_users()
            seed_jewelry_items()
            seed_sell_requests()
            seed_auction_session()
            
            print("\n✅ Database seeding completed successfully!")
            print("\n🔐 Demo accounts:")
            print("- Admin: admin@example.com / Admin@123")
            print("- Member: member@example.com / Member@123")
            print("- Staff: staff@example.com / Staff@123")
            print("- Manager: manager@example.com / Manager@123")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            db.session.rollback()
            sys.exit(1)


if __name__ == "__main__":
    main()
