from typing import Optional, List
from src.domain.models.user import User
from src.domain.repositories.user_repo import IUserRepository

class UserRepository(IUserRepository):
    def get_by_id(self, user_id:int) -> Optional[User]: raise NotImplementedError
    def get_by_username(self, username:str) -> Optional[User]: raise NotImplementedError
    def list(self, page:int=1, limit:int=20) -> List[User]: raise NotImplementedError
    def create(self, user:User) -> User: raise NotImplementedError
    def update(self, user:User) -> User: raise NotImplementedError
    def delete(self, user_id:int) -> None: raise NotImplementedError
