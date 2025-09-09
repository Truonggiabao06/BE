"""
Domain constants for the Jewelry Auction System
"""

# Default pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# File upload limits
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
MAX_PHOTOS_PER_ITEM = 10
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Auction settings
MIN_BID_INCREMENT = 1.00
DEFAULT_SESSION_DURATION_HOURS = 2
MAX_SESSION_DURATION_HOURS = 24
MIN_RESERVE_PRICE = 1.00

# User settings
MIN_PASSWORD_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_MINUTES = 15

# Business rules
DEFAULT_BUYER_FEE_PERCENTAGE = 10.0  # 10%
DEFAULT_SELLER_FEE_PERCENTAGE = 5.0  # 5%
MIN_TRANSACTION_FEE = 1.00
MAX_TRANSACTION_FEE = 1000.00

# Notification settings
NOTIFICATION_RETENTION_DAYS = 90
MAX_NOTIFICATIONS_PER_USER = 1000

# Session codes
SESSION_CODE_PREFIX = "AUC"
SESSION_CODE_LENGTH = 8

# Jewelry codes
JEWELRY_CODE_PREFIX = "JWL"
JEWELRY_CODE_LENGTH = 10

# Payment settings
PAYMENT_TIMEOUT_HOURS = 48
PAYOUT_PROCESSING_DAYS = 7

# Email templates
EMAIL_TEMPLATES = {
    'WELCOME': 'welcome.html',
    'SELL_REQUEST_SUBMITTED': 'sell_request_submitted.html',
    'SELL_REQUEST_APPROVED': 'sell_request_approved.html',
    'AUCTION_STARTING': 'auction_starting.html',
    'BID_PLACED': 'bid_placed.html',
    'AUCTION_WON': 'auction_won.html',
    'PAYMENT_REQUIRED': 'payment_required.html',
    'PAYMENT_CONFIRMED': 'payment_confirmed.html',
    'ITEM_SHIPPED': 'item_shipped.html'
}

# API rate limiting
API_RATE_LIMIT_PER_MINUTE = 60
API_RATE_LIMIT_PER_HOUR = 1000

# Cache settings
CACHE_TTL_SECONDS = 300  # 5 minutes
CACHE_TTL_LONG_SECONDS = 3600  # 1 hour

# Audit log retention
AUDIT_LOG_RETENTION_DAYS = 365

API_VERSION = "v1"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Add more constants as needed for your application.