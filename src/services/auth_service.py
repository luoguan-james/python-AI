"""Authentication service."""

from typing import Optional

from src.repositories.user_repository import UserRepository
from src.services.exceptions import AuthenticationError


class AuthService:
    """Handles user authentication."""

    def __init__(self):
        self.user_repo = UserRepository()

    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Validate credentials and return token data."""
        user = self.user_repo.find_by_username(username)
        if user is None:
            raise AuthenticationError("User not found")

        # Placeholder: replace with proper password hashing
        if password != "password":
            raise AuthenticationError("Invalid password")

        # Placeholder: replace with actual JWT generation
        return {
            "token": "valid-token",
            "expires_in": 3600,
        }
