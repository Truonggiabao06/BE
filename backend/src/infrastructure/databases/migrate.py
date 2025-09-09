"""
Database migration setup for the Jewelry Auction System
"""
from flask_migrate import Migrate
from infrastructure.databases.base import Base


def init_migrate(app, db):
    """Initialize Flask-Migrate"""
    migrate = Migrate(app, db)
    return migrate


def create_all_tables(engine):
    """Create all tables (for development/testing)"""
    Base.metadata.create_all(bind=engine)


def drop_all_tables(engine):
    """Drop all tables (for development/testing)"""
    Base.metadata.drop_all(bind=engine)
