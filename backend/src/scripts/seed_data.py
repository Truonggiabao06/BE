#!/usr/bin/env python3
"""
Database seeder for the Jewelry Auction System
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from config import config_by_name
from infrastructure.databases.mssql import db
from infrastructure.models import *
from infrastructure.services.auth_service import AuthService
from domain.enums import UserRole, JewelryStatus, SessionStatus, PaymentStatus
import uuid


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


def seed_roles():
    """Seed default roles"""
    print("Seeding roles...")
    
    roles_data = [
        {'code': 'GUEST', 'name': 'Guest User', 'description': 'Unregistered user with limited access'},
        {'code': 'MEMBER', 'name': 'Member', 'description': 'Registered user who can buy and sell'},
        {'code': 'STAFF', 'name': 'Staff', 'description': 'Staff member who can manage auctions'},
        {'code': 'MANAGER', 'name': 'Manager', 'description': 'Manager who can approve items and sessions'},
        {'code': 'ADMIN', 'name': 'Administrator', 'description': 'System administrator with full access'}
    ]
    
    for role_data in roles_data:
        existing_role = RoleModel.query.filter_by(code=role_data['code']).first()
        if not existing_role:
            role = RoleModel(
                id=str(uuid.uuid4()),
                code=role_data['code'],
                name=role_data['name'],
                description=role_data['description'],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(role)
    
    db.session.commit()
    print("✓ Roles seeded successfully")


def seed_admin_user():
    """Seed default admin user"""
    print("Seeding admin user...")
    
    admin_email = "admin@jewelryauction.com"
    existing_admin = UserModel.query.filter_by(email=admin_email).first()
    
    if not existing_admin:
        admin_password = "Admin123!@#"  # Change this in production
        password_hash = AuthService.hash_password(admin_password)
        
        admin = UserModel(
            id=str(uuid.uuid4()),
            name="System Administrator",
            email=admin_email,
            password_hash=password_hash,
            role=UserRole.ADMIN,
            is_active=True,
            email_verified=True,
            email_verified_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
        
        print(f"✓ Admin user created: {admin_email} / {admin_password}")
    else:
        print("✓ Admin user already exists")


def seed_transaction_fees():
    """Seed default transaction fees"""
    print("Seeding transaction fees...")
    
    fees_data = [
        {
            'name': 'Standard Auction Fee',
            'description': 'Standard fee structure for jewelry auctions',
            'buyer_percentage': Decimal('10.00'),  # 10% buyer premium
            'seller_percentage': Decimal('15.00'),  # 15% seller commission
            'min_fee': Decimal('5.00'),
            'max_fee': Decimal('1000.00'),
            'is_active': True
        },
        {
            'name': 'Premium Auction Fee',
            'description': 'Premium fee structure for high-value items',
            'buyer_percentage': Decimal('8.00'),   # 8% buyer premium
            'seller_percentage': Decimal('12.00'),  # 12% seller commission
            'min_fee': Decimal('10.00'),
            'max_fee': Decimal('2000.00'),
            'is_active': False
        }
    ]
    
    for fee_data in fees_data:
        existing_fee = TransactionFeeModel.query.filter_by(name=fee_data['name']).first()
        if not existing_fee:
            fee = TransactionFeeModel(
                id=str(uuid.uuid4()),
                name=fee_data['name'],
                description=fee_data['description'],
                buyer_percentage=fee_data['buyer_percentage'],
                seller_percentage=fee_data['seller_percentage'],
                min_fee=fee_data['min_fee'],
                max_fee=fee_data['max_fee'],
                is_active=fee_data['is_active'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(fee)
    
    db.session.commit()
    print("✓ Transaction fees seeded successfully")


def seed_demo_users():
    """Seed demo users for testing"""
    print("Seeding demo users...")
    
    demo_users = [
        {
            'name': 'John Seller',
            'email': 'seller@example.com',
            'password': 'Seller123!',
            'role': UserRole.MEMBER,
            'phone': '+1234567890',
            'address': '123 Main St, City, State 12345'
        },
        {
            'name': 'Jane Buyer',
            'email': 'buyer@example.com',
            'password': 'Buyer123!',
            'role': UserRole.MEMBER,
            'phone': '+1234567891',
            'address': '456 Oak Ave, City, State 12345'
        },
        {
            'name': 'Staff Member',
            'email': 'staff@jewelryauction.com',
            'password': 'Staff123!',
            'role': UserRole.STAFF,
            'phone': '+1234567892',
            'address': '789 Pine St, City, State 12345'
        },
        {
            'name': 'Manager User',
            'email': 'manager@jewelryauction.com',
            'password': 'Manager123!',
            'role': UserRole.MANAGER,
            'phone': '+1234567893',
            'address': '321 Elm St, City, State 12345'
        }
    ]
    
    for user_data in demo_users:
        existing_user = UserModel.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            password_hash = AuthService.hash_password(user_data['password'])
            
            user = UserModel(
                id=str(uuid.uuid4()),
                name=user_data['name'],
                email=user_data['email'],
                password_hash=password_hash,
                role=user_data['role'],
                is_active=True,
                phone=user_data['phone'],
                address=user_data['address'],
                email_verified=True,
                email_verified_at=datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(user)
    
    db.session.commit()
    print("✓ Demo users seeded successfully")


def seed_demo_jewelry():
    """Seed demo jewelry items"""
    print("Seeding demo jewelry...")
    
    # Get seller user
    seller = UserModel.query.filter_by(email='seller@example.com').first()
    if not seller:
        print("⚠ Seller user not found, skipping jewelry seeding")
        return
    
    jewelry_items = [
        {
            'code': 'JW001',
            'title': 'Vintage Diamond Ring',
            'description': 'Beautiful vintage diamond ring with 2 carat center stone',
            'attributes': {
                'metal': 'White Gold',
                'stone': 'Diamond',
                'carat': '2.0',
                'clarity': 'VS1',
                'color': 'G'
            },
            'weight': Decimal('15.5'),
            'photos': ['https://example.com/ring1.jpg', 'https://example.com/ring2.jpg'],
            'estimated_price': Decimal('5000.00'),
            'reserve_price': Decimal('4000.00')
        },
        {
            'code': 'JW002',
            'title': 'Pearl Necklace',
            'description': 'Elegant freshwater pearl necklace, 18 inches',
            'attributes': {
                'type': 'Freshwater Pearls',
                'length': '18 inches',
                'clasp': 'Gold'
            },
            'weight': Decimal('25.0'),
            'photos': ['https://example.com/necklace1.jpg'],
            'estimated_price': Decimal('800.00'),
            'reserve_price': Decimal('600.00')
        },
        {
            'code': 'JW003',
            'title': 'Emerald Earrings',
            'description': 'Stunning emerald earrings with diamond accents',
            'attributes': {
                'stone': 'Emerald',
                'accent_stones': 'Diamonds',
                'metal': 'Yellow Gold'
            },
            'weight': Decimal('8.2'),
            'photos': ['https://example.com/earrings1.jpg'],
            'estimated_price': Decimal('2500.00'),
            'reserve_price': Decimal('2000.00')
        }
    ]
    
    for item_data in jewelry_items:
        existing_item = JewelryItemModel.query.filter_by(code=item_data['code']).first()
        if not existing_item:
            jewelry = JewelryItemModel(
                id=str(uuid.uuid4()),
                code=item_data['code'],
                title=item_data['title'],
                description=item_data['description'],
                attributes=item_data['attributes'],
                weight=item_data['weight'],
                photos=item_data['photos'],
                owner_user_id=seller.id,
                status=JewelryStatus.APPROVED,  # Pre-approved for demo
                estimated_price=item_data['estimated_price'],
                reserve_price=item_data['reserve_price'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(jewelry)
    
    db.session.commit()
    print("✓ Demo jewelry seeded successfully")


def seed_demo_auction_session():
    """Seed demo auction session"""
    print("Seeding demo auction session...")
    
    # Get staff user
    staff = UserModel.query.filter_by(email='staff@jewelryauction.com').first()
    if not staff:
        print("⚠ Staff user not found, skipping auction session seeding")
        return
    
    existing_session = AuctionSessionModel.query.filter_by(code='AUC001').first()
    if not existing_session:
        # Create session for next week
        start_time = datetime.utcnow() + timedelta(days=7)
        end_time = start_time + timedelta(hours=4)
        
        session = AuctionSessionModel(
            id=str(uuid.uuid4()),
            code='AUC001',
            name='Weekly Jewelry Auction',
            description='Weekly auction featuring fine jewelry and collectibles',
            start_at=start_time,
            end_at=end_time,
            status=SessionStatus.SCHEDULED,
            assigned_staff_id=staff.id,
            rules={
                'anti_sniping_enabled': True,
                'anti_sniping_trigger_seconds': 60,
                'anti_sniping_extension_seconds': 300,
                'buyer_fee_percentage': 10.0,
                'seller_fee_percentage': 15.0
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(session)
        db.session.commit()
        
        # Add jewelry items to session
        jewelry_items = JewelryItemModel.query.filter_by(status=JewelryStatus.APPROVED).all()
        for i, jewelry in enumerate(jewelry_items[:3], 1):  # Add first 3 items
            session_item = SessionItemModel(
                id=str(uuid.uuid4()),
                session_id=session.id,
                jewelry_item_id=jewelry.id,
                reserve_price=jewelry.reserve_price,
                start_price=jewelry.reserve_price * Decimal('0.5'),  # Start at 50% of reserve
                step_price=Decimal('50.00'),
                lot_number=i,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(session_item)
            
            # Update jewelry status
            jewelry.status = JewelryStatus.IN_AUCTION
            jewelry.updated_at = datetime.utcnow()
        
        db.session.commit()
        print("✓ Demo auction session seeded successfully")
    else:
        print("✓ Demo auction session already exists")


def seed_policies():
    """Seed default policies"""
    print("Seeding policies...")
    
    policies = [
        {
            'slug': 'terms-of-service',
            'title': 'Terms of Service',
            'content': '''
# Terms of Service

Welcome to our Jewelry Auction System. By using our service, you agree to these terms.

## 1. Account Registration
- Users must provide accurate information
- One account per person
- Users are responsible for account security

## 2. Bidding Rules
- All bids are binding
- Bidders must be enrolled in auction sessions
- Anti-sniping rules may extend auction times

## 3. Payment Terms
- Winners must pay within 7 days
- Payment includes buyer's premium
- Accepted payment methods: Credit card, bank transfer

## 4. Seller Terms
- Items must be accurately described
- Seller's commission applies to all sales
- Items not meeting reserve will be returned

For questions, contact support@jewelryauction.com
            ''',
            'is_published': True
        },
        {
            'slug': 'privacy-policy',
            'title': 'Privacy Policy',
            'content': '''
# Privacy Policy

We respect your privacy and are committed to protecting your personal data.

## Information We Collect
- Account information (name, email, address)
- Bidding and transaction history
- Communication records

## How We Use Information
- To provide auction services
- To process payments
- To communicate about auctions

## Data Security
- We use industry-standard encryption
- Access is limited to authorized personnel
- Regular security audits are conducted

Contact us at privacy@jewelryauction.com for questions.
            ''',
            'is_published': True
        }
    ]
    
    for policy_data in policies:
        existing_policy = PolicyModel.query.filter_by(slug=policy_data['slug']).first()
        if not existing_policy:
            policy = PolicyModel(
                id=str(uuid.uuid4()),
                slug=policy_data['slug'],
                title=policy_data['title'],
                content=policy_data['content'].strip(),
                is_published=policy_data['is_published'],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                published_at=datetime.utcnow() if policy_data['is_published'] else None
            )
            db.session.add(policy)
    
    db.session.commit()
    print("✓ Policies seeded successfully")


def main():
    """Main seeding function"""
    print("Starting database seeding...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create tables if they don't exist
            db.create_all()
            
            # Seed data in order
            seed_roles()
            seed_admin_user()
            seed_transaction_fees()
            seed_demo_users()
            seed_demo_jewelry()
            seed_demo_auction_session()
            seed_policies()
            
            print("\n✅ Database seeding completed successfully!")
            print("\nDemo accounts created:")
            print("- Admin: admin@jewelryauction.com / Admin123!@#")
            print("- Staff: staff@jewelryauction.com / Staff123!")
            print("- Manager: manager@jewelryauction.com / Manager123!")
            print("- Seller: seller@example.com / Seller123!")
            print("- Buyer: buyer@example.com / Buyer123!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {str(e)}")
            db.session.rollback()
            sys.exit(1)


if __name__ == "__main__":
    main()
