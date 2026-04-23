"""User service."""

from typing import Optional

from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.exceptions import DomainException


class UserService:
    """Handles user-related business logic."""

    def __init__(self):
        self.user_repo = UserRepository()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID."""
        return self.user_repo.find_by_id(user_id)

    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user."""
        existing = self.user_repo.find_by_username(username)
        if existing:
            raise DomainException(
                message="Username already exists",
                status_code=409,
                error_code="USERNAME_CONFLICT",
            )
        # Placeholder: hash password before saving
        user = User(username=username, email=email, password_hash=password)
        return self.user_repo.save(user)
