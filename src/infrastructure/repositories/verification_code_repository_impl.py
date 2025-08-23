from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_
from datetime import datetime, timedelta, timezone
from src.domain.models.verification_code import VerificationCode, VerificationCodeType, VerificationCodeStatus
from src.domain.repositories.verification_code_repo import IVerificationCodeRepository
from src.infrastructure.models.verification_code_model import VerificationCodeModel

class VerificationCodeRepository(IVerificationCodeRepository):
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, code_id: int) -> Optional[VerificationCode]:
        """Get verification code by ID"""
        try:
            code_model = self.session.query(VerificationCodeModel).filter(VerificationCodeModel.id == code_id).first()
            if code_model:
                return self._model_to_domain(code_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting verification code by ID: {str(e)}")
    
    def get_active_code(self, email: str, code_type: VerificationCodeType) -> Optional[VerificationCode]:
        """Get active verification code for email and type"""
        try:
            code_model = (self.session.query(VerificationCodeModel)
                         .filter(and_(
                             VerificationCodeModel.email == email,
                             VerificationCodeModel.code_type == code_type.value,
                             VerificationCodeModel.status == 'active',
                             VerificationCodeModel.expires_at > datetime.now(timezone.utc)
                         ))
                         .order_by(VerificationCodeModel.created_at.desc())
                         .first())
            if code_model:
                return self._model_to_domain(code_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting active verification code: {str(e)}")
    
    def create(self, verification_code: VerificationCode) -> VerificationCode:
        """Create new verification code"""
        try:
            code_model = self._domain_to_model(verification_code)
            self.session.add(code_model)
            self.session.commit()
            self.session.refresh(code_model)
            return self._model_to_domain(code_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error creating verification code: {str(e)}")
    
    def update(self, verification_code: VerificationCode) -> VerificationCode:
        """Update existing verification code"""
        try:
            code_model = self.session.query(VerificationCodeModel).filter(VerificationCodeModel.id == verification_code.id).first()
            if not code_model:
                raise Exception(f"Verification code with ID {verification_code.id} not found")
            
            # Update fields
            code_model.user_id = verification_code.user_id
            code_model.email = verification_code.email
            code_model.code = verification_code.code
            code_model.code_type = verification_code.code_type.value
            code_model.status = verification_code.status.value
            code_model.expires_at = verification_code.expires_at
            code_model.used_at = verification_code.used_at
            code_model.attempts = verification_code.attempts
            code_model.max_attempts = verification_code.max_attempts
            code_model.is_used = verification_code.is_used
            code_model.updated_at = datetime.now(timezone.utc)
            
            self.session.commit()
            self.session.refresh(code_model)
            return self._model_to_domain(code_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error updating verification code: {str(e)}")
    
    def delete(self, code_id: int) -> None:
        """Delete verification code by ID"""
        try:
            code_model = self.session.query(VerificationCodeModel).filter(VerificationCodeModel.id == code_id).first()
            if not code_model:
                raise Exception(f"Verification code with ID {code_id} not found")
            
            self.session.delete(code_model)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error deleting verification code: {str(e)}")
    
    def get_by_email_and_code(self, email: str, code: str, code_type: VerificationCodeType) -> Optional[VerificationCode]:
        """Get verification code by email, code value, and type"""
        try:
            code_model = (self.session.query(VerificationCodeModel)
                         .filter(and_(
                             VerificationCodeModel.email == email,
                             VerificationCodeModel.code == code,
                             VerificationCodeModel.code_type == code_type.value
                         ))
                         .order_by(VerificationCodeModel.created_at.desc())
                         .first())
            if code_model:
                return self._model_to_domain(code_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting verification code by email and code: {str(e)}")
    
    def expire_old_codes(self, email: str, code_type: VerificationCodeType) -> None:
        """Expire all old active codes for email and type"""
        try:
            self.session.query(VerificationCodeModel).filter(and_(
                VerificationCodeModel.email == email,
                VerificationCodeModel.code_type == code_type.value,
                VerificationCodeModel.status == 'active'
            )).update({
                'status': 'expired',
                'updated_at': datetime.now(timezone.utc)
            })
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error expiring old codes: {str(e)}")
    
    def cleanup_expired_codes(self) -> int:
        """Clean up expired verification codes and return count of deleted codes"""
        try:
            # Delete codes that are expired or older than 24 hours
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
            
            deleted_count = self.session.query(VerificationCodeModel).filter(or_(
                VerificationCodeModel.expires_at < datetime.now(timezone.utc),
                VerificationCodeModel.created_at < cutoff_time
            )).delete()
            
            self.session.commit()
            return deleted_count
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error cleaning up expired codes: {str(e)}")
    
    def get_user_codes(self, user_id: int, code_type: Optional[VerificationCodeType] = None) -> List[VerificationCode]:
        """Get verification codes for a user, optionally filtered by type"""
        try:
            query = self.session.query(VerificationCodeModel).filter(VerificationCodeModel.user_id == user_id)
            
            if code_type:
                query = query.filter(VerificationCodeModel.code_type == code_type.value)
            
            code_models = query.order_by(VerificationCodeModel.created_at.desc()).all()
            return [self._model_to_domain(model) for model in code_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting user codes: {str(e)}")
    
    def _model_to_domain(self, model: VerificationCodeModel) -> VerificationCode:
        """Convert VerificationCodeModel to VerificationCode domain object"""
        return VerificationCode(
            id=model.id,
            user_id=model.user_id,
            email=model.email,
            code=model.code,
            code_type=VerificationCodeType(model.code_type),
            status=VerificationCodeStatus(model.status),
            expires_at=model.expires_at,
            is_used=model.is_used,
            used_at=model.used_at,
            attempts=model.attempts,
            max_attempts=model.max_attempts,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
    
    def _domain_to_model(self, domain: VerificationCode) -> VerificationCodeModel:
        """Convert VerificationCode domain object to VerificationCodeModel"""
        return VerificationCodeModel(
            id=domain.id,
            user_id=domain.user_id,
            email=domain.email,
            code=domain.code,
            code_type=domain.code_type.value,
            status=domain.status.value,
            expires_at=domain.expires_at,
            is_used=domain.is_used,
            used_at=domain.used_at,
            attempts=domain.attempts,
            max_attempts=domain.max_attempts,
            created_at=domain.created_at,
            updated_at=domain.updated_at
        )
