"""User repository for database operations."""

from typing import Optional

from src.models.user import User


class UserRepository:
    """Repository for User entity."""

    def __init__(self):
        # Placeholder: replace with actual database session
        self._storage: dict[int, User] = {}
        self._next_id = 1

    def find_by_id(self, user_id: int) -> Optional[User]:
        """Find user by primary key."""
        return self._storage.get(user_id)

    def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username."""
        for user in self._storage.values():
            if user.username == username:
                return user
        return None

    def save(self, user: User) -> User:
        """Persist a new user."""
        user.id = self._next_id
        self._next_id += 1
        self._storage[user.id] = user
        return user

    def delete(self, user_id: int) -> bool:
        """Delete user by ID."""
        return self._storage.pop(user_id, None) is not None
