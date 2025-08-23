from src.infrastructure.databases.mssql import init_mssql

# Import all models to ensure they are registered with SQLAlchemy
from src.infrastructure.models import (
    user_model,
    auction_item_model,
    auction_session_model,
    bid_model,
    payment_model,
    verification_code_model
)

def init_db(app):
    init_mssql(app)

from src.infrastructure.databases.mssql import Base