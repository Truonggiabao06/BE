"""
MySQL database configuration and initialization
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
import pymysql

# Install PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()


def init_mysql(app: Flask) -> None:
    """Initialize MySQL database with Flask app"""

    # Database configuration
    db_url = os.getenv('DB_URL', 'mysql+pymysql://jewelry_user:jewelry_password@localhost:3307/jewelry_auction')

    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = os.getenv('DEBUG', 'false').lower() == 'true'

    # Connection pool settings
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'poolclass': QueuePool,
        'pool_size': int(os.getenv('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', 20)),
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', 3600)),
        'pool_pre_ping': True,
        'connect_args': {
            'charset': 'utf8mb4',
            'connect_timeout': 60,
            'read_timeout': 60,
            'write_timeout': 60,
        }
    }

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)

    # Import all models to ensure they are registered
    from infrastructure.models import (
        user_model, jewelry_model, auction_model,
        payment_model, notification_model
    )

    print(f"✅ MySQL database initialized: {db_url}")


def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        db_url = os.getenv('DB_URL', 'mysql+pymysql://jewelry_user:jewelry_password@localhost:3307/jewelry_auction')

        # Parse database URL to get connection details
        from urllib.parse import urlparse
        parsed = urlparse(db_url)

        # Create connection to MySQL server (without database)
        server_url = f"{parsed.scheme}://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}"
        engine = create_engine(server_url)

        database_name = parsed.path.lstrip('/')

        # Create database if not exists
        with engine.connect() as conn:
            conn.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"✅ Database '{database_name}' created or already exists")

    except Exception as e:
        print(f"❌ Error creating database: {e}")


def get_db():
    """Get database instance"""
    return db