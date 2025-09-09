"""
Database configuration for the Jewelry Auction System
Supports MySQL, PostgreSQL, and SQLite
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from infrastructure.databases.base import Base

# Database configuration - will be initialized in init_mssql
engine = None
session = None

# Flask-SQLAlchemy instance
db = SQLAlchemy()
migrate = Migrate()

def init_mssql(app):
    """Initialize database with Flask app"""
    global engine, session

    # Get database URI from app config
    database_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"Initializing raw SQLAlchemy with URI: {database_uri}")

    # Initialize raw SQLAlchemy engine and session
    engine = create_engine(database_uri, echo=app.config.get('DEBUG', False))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = scoped_session(SessionLocal)

    print(f"Raw SQLAlchemy initialized - Engine: {engine}, Session: {session}")

    # Configure Flask-SQLAlchemy
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Create tables if they don't exist (for development)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print(f"Warning: Could not create tables: {e}")

def get_db_session():
    """Get database session"""
    # For now, return Flask-SQLAlchemy session as fallback
    return db.session

def close_db_session():
    """Close database session"""
    session.remove()