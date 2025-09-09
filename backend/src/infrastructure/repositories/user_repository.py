"""
User repository implementation for the Jewelry Auction System
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from domain.repositories.base_repository import IUserRepository
from domain.entities.user import User
from domain.enums import UserRole
from infrastructure.models.user_model import UserModel
from domain.exceptions import NotFoundError, ConflictError


class UserRepository(IUserRepository[User]):
    """User repository implementation"""

    def __init__(self, session: Session):
        super().__init__(session)

    def create(self, entity: User) -> User:
        """Create a new user"""
        # Check if email already exists
        existing = self.session.query(UserModel).filter_by(email=entity.email).first()
        if existing:
            raise ConflictError("Email already exists")

        user_model = UserModel(
            name=entity.name,
            email=entity.email,
            password_hash=entity.password_hash,
            role=entity.role,
            is_active=entity.is_active,
            phone=entity.phone,
            address=entity.address
        )

        self.session.add(user_model)
        self.session.flush()

        # Convert back to domain entity
        return self._to_domain_entity(user_model)

    def get_by_id(self, entity_id: str) -> Optional[User]:
        """Get user by ID"""
        user_model = self.session.query(UserModel).filter_by(id=entity_id).first()
        if not user_model:
            return None
        return self._to_domain_entity(user_model)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_model = self.session.query(UserModel).filter_by(email=email).first()
        if not user_model:
            return None
        return self._to_domain_entity(user_model)

    def get_by_role(self, role: UserRole) -> List[User]:
        """Get users by role"""
        user_models = self.session.query(UserModel).filter_by(role=role).all()
        return [self._to_domain_entity(model) for model in user_models]

    def update(self, entity: User) -> User:
        """Update a user"""
        user_model = self.session.query(UserModel).filter_by(id=entity.id).first()
        if not user_model:
            raise NotFoundError("User not found")

        # Update fields
        user_model.name = entity.name
        user_model.email = entity.email
        user_model.password_hash = entity.password_hash
        user_model.role = entity.role
        user_model.is_active = entity.is_active
        user_model.phone = entity.phone
        user_model.address = entity.address
        user_model.updated_at = entity.updated_at

        self.session.flush()
        return self._to_domain_entity(user_model)

    def delete(self, entity_id: str) -> bool:
        """Delete a user (soft delete by deactivating)"""
        user_model = self.session.query(UserModel).filter_by(id=entity_id).first()
        if not user_model:
            return False

        user_model.is_active = False
        self.session.flush()
        return True

    def list(self, filters: Optional[Dict[str, Any]] = None,
             page: int = 1, page_size: int = 20) -> List[User]:
        """List users with optional filters and pagination"""
        query = self.session.query(UserModel)

        if filters:
            if 'role' in filters:
                query = query.filter(UserModel.role == filters['role'])
            if 'is_active' in filters:
                query = query.filter(UserModel.is_active == filters['is_active'])
            if 'search' in filters:
                search_term = f"%{filters['search']}%"
                query = query.filter(or_(
                    UserModel.name.ilike(search_term),
                    UserModel.email.ilike(search_term)
                ))

        # Apply pagination
        offset = (page - 1) * page_size
        user_models = query.offset(offset).limit(page_size).all()

        return [self._to_domain_entity(model) for model in user_models]

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count users with optional filters"""
        query = self.session.query(UserModel)

        if filters:
            if 'role' in filters:
                query = query.filter(UserModel.role == filters['role'])
            if 'is_active' in filters:
                query = query.filter(UserModel.is_active == filters['is_active'])
            if 'search' in filters:
                search_term = f"%{filters['search']}%"
                query = query.filter(or_(
                    UserModel.name.ilike(search_term),
                    UserModel.email.ilike(search_term)
                ))

        return query.count()

    def _to_domain_entity(self, model: UserModel) -> User:
        """Convert database model to domain entity"""
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
            password_hash=model.password_hash,
            role=model.role,
            is_active=model.is_active,
            phone=model.phone,
            address=model.address,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

