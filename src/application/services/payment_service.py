"""
Payment Service - Business logic for payment processing
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from enum import Enum

from src.domain.models.payment import Payment, PaymentStatus, PaymentMethod
from src.domain.models.auction_session import AuctionSession, SessionStatus
from src.domain.models.bid import Bid, BidStatus
from src.domain.models.user import User, UserRole
from src.domain.repositories.payment_repo import IPaymentRepository
from src.domain.repositories.auction_session_repo import IAuctionSessionRepository
from src.domain.repositories.bid_repo import IBidRepository
from src.domain.repositories.user_repo import IUserRepository

logger = logging.getLogger(__name__)

class PaymentService:
    """Service for payment business logic"""
    
    def __init__(self, 
                 payment_repo: IPaymentRepository,
                 auction_session_repo: IAuctionSessionRepository,
                 bid_repo: IBidRepository,
                 user_repo: IUserRepository):
        self.payment_repo = payment_repo
        self.auction_session_repo = auction_session_repo
        self.bid_repo = bid_repo
        self.user_repo = user_repo
        
        # Payment configuration
        self.PLATFORM_FEE_RATE = 0.05  # 5% platform fee
        self.PAYMENT_PROCESSING_FEES = {
            PaymentMethod.BANK_TRANSFER: 0.01,    # 1%
            PaymentMethod.E_WALLET: 0.015,        # 1.5%
            PaymentMethod.CREDIT_CARD: 0.025,     # 2.5%
            PaymentMethod.CASH_DEPOSIT: 0.005,    # 0.5%
            PaymentMethod.CRYPTO: 0.03            # 3%
        }
    
    def create_payment_for_winner(self, session_id: int, winner: User) -> Dict[str, Any]:
        """Create payment for auction winner"""
        try:
            # Get auction session
            session = self.auction_session_repo.get(session_id)
            if not session:
                raise ValueError("Không tìm thấy phiên đấu giá")
            
            if session.status != SessionStatus.COMPLETED:
                raise ValueError("Phiên đấu giá chưa kết thúc")
            
            if session.winner_id != winner.id:
                raise ValueError("Bạn không phải người thắng đấu giá")
            
            # Check if payment already exists
            existing_payments = self.payment_repo.get_by_session_and_user(session_id, winner.id)
            if existing_payments:
                active_payment = next((p for p in existing_payments if p.status != PaymentStatus.CANCELLED), None)
                if active_payment:
                    raise ValueError("Đã có thanh toán cho phiên đấu giá này")
            
            # Get winning bid
            winning_bid = self.bid_repo.get_by_session(session_id, page=1, limit=1000)
            winning_bid = max([bid for bid in winning_bid if bid.status == BidStatus.ACTIVE], 
                            key=lambda x: x.amount, default=None)
            
            if not winning_bid or winning_bid.bidder_id != winner.id:
                raise ValueError("Không tìm thấy lượt đặt giá thắng")
            
            # Calculate payment details
            bid_amount = winning_bid.amount
            payment_details = self.calculate_payment_breakdown(bid_amount, PaymentMethod.BANK_TRANSFER)
            
            # Create payment record
            payment = Payment(
                session_id=session_id,
                payer_id=winner.id,
                amount=bid_amount,
                platform_fee=payment_details['platform_fee'],
                payment_fee=payment_details['payment_fee'],
                total_amount=payment_details['total_amount'],
                method=PaymentMethod.BANK_TRANSFER,  # Default method
                status=PaymentStatus.PENDING,
                due_date=datetime.now(timezone.utc) + timedelta(days=3),  # 3 days to pay
                created_at=datetime.now(timezone.utc)
            )
            
            created_payment = self.payment_repo.create(payment)
            
            result = {
                "payment": created_payment,
                "payment_details": payment_details,
                "due_date": payment.due_date,
                "instructions": self._get_payment_instructions(PaymentMethod.BANK_TRANSFER)
            }
            
            logger.info(f"Created payment {created_payment.id} for winner {winner.id} in session {session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Create payment for winner error: {str(e)}")
            raise
    
    def calculate_payment_breakdown(self, bid_amount: float, payment_method: PaymentMethod) -> Dict[str, Any]:
        """Calculate detailed payment breakdown"""
        try:
            # Platform fee (paid by buyer)
            platform_fee = bid_amount * self.PLATFORM_FEE_RATE
            
            # Payment processing fee
            processing_fee_rate = self.PAYMENT_PROCESSING_FEES.get(payment_method, 0.02)
            payment_fee = bid_amount * processing_fee_rate
            
            # Total amount buyer pays
            total_amount = bid_amount + platform_fee + payment_fee
            
            # Amount seller receives (bid amount minus platform fee)
            seller_amount = bid_amount - platform_fee
            
            return {
                "bid_amount": bid_amount,
                "platform_fee": platform_fee,
                "payment_fee": payment_fee,
                "total_amount": total_amount,
                "seller_amount": seller_amount,
                "platform_fee_rate": self.PLATFORM_FEE_RATE,
                "payment_fee_rate": processing_fee_rate,
                "breakdown": {
                    "item_price": bid_amount,
                    "platform_fee": f"{platform_fee:,.0f} VND ({self.PLATFORM_FEE_RATE*100}%)",
                    "payment_processing": f"{payment_fee:,.0f} VND ({processing_fee_rate*100}%)",
                    "total_to_pay": f"{total_amount:,.0f} VND",
                    "seller_receives": f"{seller_amount:,.0f} VND"
                }
            }
            
        except Exception as e:
            logger.error(f"Calculate payment breakdown error: {str(e)}")
            raise
    
    def process_payment_confirmation(self, payment_id: int, admin: User, confirmation_data: Dict[str, Any]) -> Payment:
        """Process payment confirmation by admin"""
        try:
            if admin.role != UserRole.ADMIN:
                raise ValueError("Chỉ admin mới có thể xác nhận thanh toán")
            
            payment = self.payment_repo.get(payment_id)
            if not payment:
                raise ValueError("Không tìm thấy thanh toán")
            
            if payment.status != PaymentStatus.PENDING:
                raise ValueError("Chỉ có thể xác nhận thanh toán đang chờ")
            
            # Update payment status
            payment.status = PaymentStatus.COMPLETED
            payment.confirmed_by = admin.id
            payment.confirmed_at = datetime.now(timezone.utc)
            payment.transaction_id = confirmation_data.get('transaction_id')
            payment.notes = confirmation_data.get('notes', '')
            
            updated_payment = self.payment_repo.update(payment)
            
            # Update auction session payment status
            session = self.auction_session_repo.get(payment.session_id)
            if session:
                session.payment_completed = True
                self.auction_session_repo.update(session)
            
            logger.info(f"Confirmed payment {payment_id} by admin {admin.id}")
            return updated_payment
            
        except Exception as e:
            logger.error(f"Process payment confirmation error: {str(e)}")
            raise
    
    def calculate_seller_payout(self, session_id: int) -> Dict[str, Any]:
        """Calculate payout amount for seller"""
        try:
            session = self.auction_session_repo.get(session_id)
            if not session:
                raise ValueError("Không tìm thấy phiên đấu giá")
            
            if session.status != SessionStatus.COMPLETED:
                raise ValueError("Phiên đấu giá chưa kết thúc")
            
            if not session.winner_id or not session.final_price:
                return {
                    "payout_amount": 0,
                    "platform_fee": 0,
                    "final_price": 0,
                    "status": "no_winner"
                }
            
            # Get payment record
            payments = self.payment_repo.get_by_session_and_user(session_id, session.winner_id)
            completed_payment = next((p for p in payments if p.status == PaymentStatus.COMPLETED), None)
            
            if not completed_payment:
                return {
                    "payout_amount": 0,
                    "platform_fee": session.final_price * self.PLATFORM_FEE_RATE,
                    "final_price": session.final_price,
                    "status": "payment_pending"
                }
            
            # Calculate seller payout (final price minus platform fee)
            platform_fee = session.final_price * self.PLATFORM_FEE_RATE
            payout_amount = session.final_price - platform_fee
            
            return {
                "payout_amount": payout_amount,
                "platform_fee": platform_fee,
                "final_price": session.final_price,
                "payment_completed_at": completed_payment.confirmed_at,
                "status": "ready_for_payout"
            }
            
        except Exception as e:
            logger.error(f"Calculate seller payout error: {str(e)}")
            raise
    
    def process_refund(self, payment_id: int, admin: User, refund_reason: str) -> Dict[str, Any]:
        """Process refund for a payment"""
        try:
            if admin.role != UserRole.ADMIN:
                raise ValueError("Chỉ admin mới có thể xử lý hoàn tiền")
            
            payment = self.payment_repo.get(payment_id)
            if not payment:
                raise ValueError("Không tìm thấy thanh toán")
            
            if payment.status not in [PaymentStatus.COMPLETED, PaymentStatus.PENDING]:
                raise ValueError("Chỉ có thể hoàn tiền cho thanh toán đã hoàn thành hoặc đang chờ")
            
            # Create refund record
            refund_amount = payment.total_amount if payment.status == PaymentStatus.COMPLETED else 0
            
            # Update payment status
            payment.status = PaymentStatus.REFUNDED
            payment.refund_amount = refund_amount
            payment.refund_reason = refund_reason
            payment.refunded_by = admin.id
            payment.refunded_at = datetime.now(timezone.utc)
            
            updated_payment = self.payment_repo.update(payment)
            
            result = {
                "payment": updated_payment,
                "refund_amount": refund_amount,
                "refund_reason": refund_reason,
                "refunded_at": payment.refunded_at
            }
            
            logger.info(f"Processed refund for payment {payment_id}, amount: {refund_amount}")
            return result
            
        except Exception as e:
            logger.error(f"Process refund error: {str(e)}")
            raise
    
    def get_payment_statistics(self, start_date: datetime = None, end_date: datetime = None) -> Dict[str, Any]:
        """Get payment statistics for a date range"""
        try:
            if not start_date:
                start_date = datetime.now(timezone.utc) - timedelta(days=30)
            if not end_date:
                end_date = datetime.now(timezone.utc)
            
            # Get all payments in date range
            all_payments = self.payment_repo.get_by_date_range(start_date, end_date)
            
            if not all_payments:
                return {
                    "total_payments": 0,
                    "total_amount": 0,
                    "total_fees": 0,
                    "completed_payments": 0,
                    "pending_payments": 0,
                    "refunded_payments": 0,
                    "average_payment": 0,
                    "payment_methods": {}
                }
            
            # Categorize payments
            completed = [p for p in all_payments if p.status == PaymentStatus.COMPLETED]
            pending = [p for p in all_payments if p.status == PaymentStatus.PENDING]
            refunded = [p for p in all_payments if p.status == PaymentStatus.REFUNDED]
            
            # Calculate totals
            total_amount = sum(p.amount for p in completed)
            total_fees = sum(p.platform_fee + p.payment_fee for p in completed)
            
            # Payment method breakdown
            method_stats = {}
            for payment in completed:
                method = payment.method.value
                if method not in method_stats:
                    method_stats[method] = {"count": 0, "amount": 0}
                method_stats[method]["count"] += 1
                method_stats[method]["amount"] += payment.amount
            
            stats = {
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "total_payments": len(all_payments),
                "total_amount": total_amount,
                "total_fees": total_fees,
                "completed_payments": len(completed),
                "pending_payments": len(pending),
                "refunded_payments": len(refunded),
                "average_payment": total_amount / len(completed) if completed else 0,
                "payment_methods": method_stats,
                "success_rate": (len(completed) / len(all_payments) * 100) if all_payments else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Get payment statistics error: {str(e)}")
            raise
    
    def check_overdue_payments(self) -> List[Dict[str, Any]]:
        """Check for overdue payments"""
        try:
            now = datetime.now(timezone.utc)
            
            # Get all pending payments
            all_payments = self.payment_repo.get_by_status(PaymentStatus.PENDING)
            overdue_payments = [p for p in all_payments if p.due_date and p.due_date < now]
            
            overdue_list = []
            for payment in overdue_payments:
                # Get session and user info
                session = self.auction_session_repo.get(payment.session_id)
                user = self.user_repo.get(payment.payer_id)
                
                days_overdue = (now - payment.due_date).days
                
                overdue_info = {
                    "payment_id": payment.id,
                    "session_id": payment.session_id,
                    "session_title": session.title if session else "Unknown",
                    "payer": {
                        "id": user.id if user else payment.payer_id,
                        "name": user.full_name if user else "Unknown",
                        "email": user.email if user else "Unknown"
                    },
                    "amount": payment.total_amount,
                    "due_date": payment.due_date.isoformat(),
                    "days_overdue": days_overdue,
                    "created_at": payment.created_at.isoformat()
                }
                
                overdue_list.append(overdue_info)
            
            return overdue_list
            
        except Exception as e:
            logger.error(f"Check overdue payments error: {str(e)}")
            return []
    
    def _get_payment_instructions(self, payment_method: PaymentMethod) -> Dict[str, Any]:
        """Get payment instructions for different methods"""
        instructions = {
            PaymentMethod.BANK_TRANSFER: {
                "title": "Chuyển khoản ngân hàng",
                "steps": [
                    "Đăng nhập vào ứng dụng ngân hàng của bạn",
                    "Chọn chuyển khoản trong nước",
                    "Nhập thông tin tài khoản nhận (sẽ được cung cấp)",
                    "Nhập số tiền chính xác",
                    "Nhập nội dung chuyển khoản: 'AUCTION-[PAYMENT_ID]'",
                    "Xác nhận và thực hiện chuyển khoản",
                    "Chụp ảnh biên lai và gửi cho admin"
                ],
                "processing_time": "1-2 ngày làm việc",
                "notes": "Vui lòng giữ lại biên lai để đối chiếu"
            },
            PaymentMethod.E_WALLET: {
                "title": "Ví điện tử",
                "steps": [
                    "Mở ứng dụng ví điện tử (MoMo, ZaloPay, ViettelPay)",
                    "Chọn chức năng chuyển tiền",
                    "Quét mã QR hoặc nhập số điện thoại nhận",
                    "Nhập số tiền chính xác",
                    "Nhập nội dung: 'AUCTION-[PAYMENT_ID]'",
                    "Xác nhận thanh toán",
                    "Chụp ảnh màn hình thành công"
                ],
                "processing_time": "Tức thì",
                "notes": "Thanh toán được xử lý ngay lập tức"
            },
            PaymentMethod.CASH_DEPOSIT: {
                "title": "Nộp tiền mặt",
                "steps": [
                    "Đến văn phòng hoặc đại lý của chúng tôi",
                    "Mang theo CMND/CCCD và thông tin thanh toán",
                    "Nộp tiền mặt cho nhân viên",
                    "Nhận biên lai xác nhận",
                    "Chờ xác nhận từ hệ thống"
                ],
                "processing_time": "Tức thì sau khi xác nhận",
                "notes": "Vui lòng mang theo giấy tờ tùy thân"
            }
        }
        
        return instructions.get(payment_method, {
            "title": "Phương thức thanh toán",
            "steps": ["Vui lòng liên hệ admin để được hướng dẫn"],
            "processing_time": "Liên hệ admin",
            "notes": "Phương thức thanh toán đặc biệt"
        })
