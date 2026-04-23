"""User domain model."""

from datetime import datetime
from dataclasses import dataclass


@dataclass
class User:
    """Represents a user in the system."""

    id: int = 0
    username: str = ""
    email: str = ""
    password_hash: str = ""
    created_at: datetime = None

    def __post_init__(self):
        self.created_at = self.created_at or datetime.utcnow()
