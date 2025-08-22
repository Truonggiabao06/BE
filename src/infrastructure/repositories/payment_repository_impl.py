from typing import Optional
from src.domain.models.payment import Payment
from src.domain.repositories.payment_repo import IPaymentRepository

class PaymentRepository(IPaymentRepository):
    def get(self, payment_id:int) -> Optional[Payment]: raise NotImplementedError
    def get_by_order(self, order_id:int) -> Optional[Payment]: raise NotImplementedError
    def create(self, payment:Payment) -> Payment: raise NotImplementedError
    def update(self, payment:Payment) -> Payment: raise NotImplementedError
