from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from src.domain.models.user import User, UserRole, UserStatus
from src.domain.repositories.user_repo import IUserRepository
from src.infrastructure.models.user_model import UserModel
from datetime import datetime

class UserRepository(IUserRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            user_model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
            if user_model:
                return self._model_to_domain(user_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting user by ID: {str(e)}")

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by email (username)"""
        try:
            user_model = self.session.query(UserModel).filter(UserModel.email == username).first()
            if user_model:
                return self._model_to_domain(user_model)
            return None
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error getting user by username: {str(e)}")

    def list(self, page: int = 1, limit: int = 20) -> List[User]:
        """Get paginated list of users"""
        try:
            offset = (page - 1) * limit
            user_models = self.session.query(UserModel).order_by(UserModel.id).offset(offset).limit(limit).all()
            return [self._model_to_domain(model) for model in user_models]
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error listing users: {str(e)}")

    def create(self, user: User) -> User:
        """Create new user"""
        try:
            user_model = self._domain_to_model(user)
            self.session.add(user_model)
            self.session.commit()
            self.session.refresh(user_model)
            return self._model_to_domain(user_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error creating user: {str(e)}")

    def update(self, user: User) -> User:
        """Update existing user"""
        try:
            user_model = self.session.query(UserModel).filter(UserModel.id == user.id).first()
            if not user_model:
                raise Exception(f"User with ID {user.id} not found")

            # Update fields
            user_model.first_name = user.first_name
            user_model.last_name = user.last_name
            user_model.email = user.email
            user_model.phone_number = user.phone_number
            user_model.password_hash = user.password_hash
            user_model.role = user.role.value
            user_model.status = user.status.value
            user_model.bio = user.bio
            user_model.image_url = user.image_url
            user_model.address = user.address
            user_model.is_email_verified = user.is_email_verified
            user_model.updated_at = datetime.utcnow()

            self.session.commit()
            self.session.refresh(user_model)
            return self._model_to_domain(user_model)
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error updating user: {str(e)}")

    def delete(self, user_id: int) -> None:
        """Delete user by ID"""
        try:
            user_model = self.session.query(UserModel).filter(UserModel.id == user_id).first()
            if not user_model:
                raise Exception(f"User with ID {user_id} not found")

            self.session.delete(user_model)
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise Exception(f"Error deleting user: {str(e)}")

    def _model_to_domain(self, model: UserModel) -> User:
        """Convert UserModel to User domain object"""
        return User(
            id=model.id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            phone_number=model.phone_number,
            password_hash=model.password_hash,
            role=UserRole(model.role),
            status=UserStatus(model.status),
            bio=model.bio,
            image_url=model.image_url,
            address=model.address,
            is_email_verified=model.is_email_verified,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _domain_to_model(self, domain: User) -> UserModel:
        """Convert User domain object to UserModel"""
        return UserModel(
            id=domain.id,
            first_name=domain.first_name,
            last_name=domain.last_name,
            email=domain.email,
            phone_number=domain.phone_number,
            password_hash=domain.password_hash,
            role=domain.role.value,
            status=domain.status.value,
            bio=domain.bio,
            image_url=domain.image_url,
            address=domain.address,
            is_email_verified=domain.is_email_verified,
            created_at=domain.created_at,
            updated_at=domain.updated_at
        )
