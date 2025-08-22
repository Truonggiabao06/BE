# Adapters package
# Contains adapters for external services and third-party integrations

from .payments import BasePayment, FakePayment, StripePayment

__all__ = [
    'BasePayment',
    'FakePayment', 
    'StripePayment'
]
