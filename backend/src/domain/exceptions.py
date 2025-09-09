"""
Custom exceptions for the Jewelry Auction System
"""


class JewelryAuctionException(Exception):
    """Base exception for jewelry auction system"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(JewelryAuctionException):
    """Raised when validation fails"""
    pass


class AuthenticationError(JewelryAuctionException):
    """Raised when authentication fails"""
    pass


class AuthorizationError(JewelryAuctionException):
    """Raised when user lacks required permissions"""
    pass


class NotFoundError(JewelryAuctionException):
    """Raised when requested resource is not found"""
    pass


class ConflictError(JewelryAuctionException):
    """Raised when operation conflicts with current state"""
    pass


class BusinessRuleViolationError(JewelryAuctionException):
    """Raised when business rule is violated"""
    pass


class InvalidStateTransitionError(BusinessRuleViolationError):
    """Raised when invalid state transition is attempted"""
    pass


class BiddingError(BusinessRuleViolationError):
    """Raised when bidding operation fails"""
    pass


class PaymentError(JewelryAuctionException):
    """Raised when payment operation fails"""
    pass


class FileUploadError(JewelryAuctionException):
    """Raised when file upload fails"""
    pass


class ExternalServiceError(JewelryAuctionException):
    """Raised when external service call fails"""
    pass


class DatabaseError(JewelryAuctionException):
    """Raised when database operation fails"""
    pass


class ConfigurationError(JewelryAuctionException):
    """Raised when configuration is invalid"""
    pass


class ConcurrencyError(JewelryAuctionException):
    """Raised when concurrent access causes conflicts"""
    pass


# Specific business exceptions
class AuctionNotOpenError(BiddingError):
    """Raised when trying to bid on closed auction"""
    def __init__(self):
        super().__init__("Auction is not open for bidding", "AUCTION_NOT_OPEN")


class InsufficientBidError(BiddingError):
    """Raised when bid amount is insufficient"""
    def __init__(self, minimum_bid: float):
        super().__init__(f"Bid must be at least {minimum_bid}", "INSUFFICIENT_BID")


class ReservePriceNotMetError(BiddingError):
    """Raised when bid doesn't meet reserve price"""
    def __init__(self, reserve_price: float):
        super().__init__(f"Bid must meet reserve price of {reserve_price}", "RESERVE_NOT_MET")


class UserNotEnrolledError(BiddingError):
    """Raised when user is not enrolled in auction session"""
    def __init__(self):
        super().__init__("User must be enrolled to bid in this session", "USER_NOT_ENROLLED")


class ItemNotAvailableError(ConflictError):
    """Raised when jewelry item is not available for operation"""
    def __init__(self, item_status: str):
        super().__init__(f"Item is not available (status: {item_status})", "ITEM_NOT_AVAILABLE")


class SessionNotActiveError(ConflictError):
    """Raised when session is not in active state"""
    def __init__(self, session_status: str):
        super().__init__(f"Session is not active (status: {session_status})", "SESSION_NOT_ACTIVE")


class DuplicateEmailError(ConflictError):
    """Raised when email already exists"""
    def __init__(self):
        super().__init__("Email address already exists", "DUPLICATE_EMAIL")


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid"""
    def __init__(self):
        super().__init__("Invalid email or password", "INVALID_CREDENTIALS")


class AccountDeactivatedError(AuthenticationError):
    """Raised when account is deactivated"""
    def __init__(self):
        super().__init__("Account has been deactivated", "ACCOUNT_DEACTIVATED")


class TokenExpiredError(AuthenticationError):
    """Raised when JWT token is expired"""
    def __init__(self):
        super().__init__("Token has expired", "TOKEN_EXPIRED")


class InsufficientPermissionsError(AuthorizationError):
    """Raised when user lacks required permissions"""
    def __init__(self, required_role: str):
        super().__init__(f"Requires {required_role} role or higher", "INSUFFICIENT_PERMISSIONS")


# Keep backward compatibility with existing exceptions
CustomException = JewelryAuctionException
NotFoundException = NotFoundError
ValidationException = ValidationError
UnauthorizedException = AuthorizationError
ConflictException = ConflictError