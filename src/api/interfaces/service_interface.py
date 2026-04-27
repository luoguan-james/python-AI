"""Service layer interface definitions.

This module defines abstract base classes and protocols for the service layer,
ensuring consistent contracts between API controllers and service implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable

from src.models.user import User


class AuthServiceInterface(ABC):
    """Interface for authentication service."""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user with username and password.

        Args:
            username: The user's username.
            password: The user's password.

        Returns:
            A dict containing 'token' and 'expires_in' if authentication succeeds,
            None if credentials are invalid.
        """
        ...


class UserServiceInterface(ABC):
    """Interface for user management service."""

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The User object if found, None otherwise.
        """
        ...

    @abstractmethod
    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user.

        Args:
            username: The desired username.
            email: The user's email address.
            password: The user's password (will be hashed).

        Returns:
            The newly created User object.

        Raises:
            ValueError: If the username or email already exists.
        """
        ...


@runtime_checkable
class ServiceFactory(Protocol):
    """Protocol for service factory implementations."""

    def create_auth_service(self) -> AuthServiceInterface:
        """Create an authentication service instance."""
        ...

    def create_user_service(self) -> UserServiceInterface:
        """Create a user service instance."""
        ...
"""Service layer interface definitions.

This module defines abstract base classes and protocols for the service layer,
ensuring consistent contracts between API controllers and service implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable

from src.models.user import User


class AuthServiceInterface(ABC):
    """Interface for authentication service."""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user with username and password.

        Args:
            username: The user's username.
            password: The user's password.

        Returns:
            A dict containing 'token' and 'expires_in' if authentication succeeds,
            None if credentials are invalid.
        """
        ...


class UserServiceInterface(ABC):
    """Interface for user management service."""

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The User object if found, None otherwise.
        """
        ...

    @abstractmethod
    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user.

        Args:
            username: The desired username.
            email: The user's email address.
            password: The user's password (will be hashed).

        Returns:
            The newly created User object.

        Raises:
            ValueError: If the username or email already exists.
        """
        ...


@runtime_checkable
class ServiceFactory(Protocol):
    """Protocol for service factory implementations."""

    def create_auth_service(self) -> AuthServiceInterface:
        """Create an authentication service instance."""
        ...

    def create_user_service(self) -> UserServiceInterface:
        """Create a user service instance."""
        ...
"""Service layer interface definitions.

This module defines abstract base classes and protocols for the service layer,
ensuring consistent contracts between API controllers and service implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable

from src.models.user import User


class AuthServiceInterface(ABC):
    """Interface for authentication service."""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user with username and password.

        Args:
            username: The user's username.
            password: The user's password.

        Returns:
            A dict containing 'token' and 'expires_in' if authentication succeeds,
            None if credentials are invalid.
        """
        ...


class UserServiceInterface(ABC):
    """Interface for user management service."""

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The User object if found, None otherwise.
        """
        ...

    @abstractmethod
    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user.

        Args:
            username: The desired username.
            email: The user's email address.
            password: The user's password (will be hashed).

        Returns:
            The newly created User object.

        Raises:
            ValueError: If the username or email already exists.
        """
        ...


@runtime_checkable
class ServiceFactory(Protocol):
    """Protocol for service factory implementations."""

    def create_auth_service(self) -> AuthServiceInterface:
        """Create an authentication service instance."""
        ...

    def create_user_service(self) -> UserServiceInterface:
        """Create a user service instance."""
        ...
"""Service layer interface definitions.

This module defines abstract base classes and protocols for the service layer,
ensuring consistent contracts between API controllers and service implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable

from src.models.user import User


class AuthServiceInterface(ABC):
    """Interface for authentication service."""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user with username and password.

        Args:
            username: The user's username.
            password: The user's password.

        Returns:
            A dict containing 'token' and 'expires_in' if authentication succeeds,
            None if credentials are invalid.
        """
        ...


class UserServiceInterface(ABC):
    """Interface for user management service."""

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The User object if found, None otherwise.
        """
        ...

    @abstractmethod
    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user.

        Args:
            username: The desired username.
            email: The user's email address.
            password: The user's password (will be hashed).

        Returns:
            The newly created User object.

        Raises:
            ValueError: If the username or email already exists.
        """
        ...


@runtime_checkable
class ServiceFactory(Protocol):
    """Protocol for service factory implementations."""

    def create_auth_service(self) -> AuthServiceInterface:
        """Create an authentication service instance."""
        ...

    def create_user_service(self) -> UserServiceInterface:
        """Create a user service instance."""
        ...
"""Service layer interface definitions.

This module defines abstract base classes and protocols for the service layer,
ensuring consistent contracts between API controllers and service implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Protocol, runtime_checkable

from src.models.user import User


class AuthServiceInterface(ABC):
    """Interface for authentication service."""

    @abstractmethod
    def authenticate(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user with username and password.

        Args:
            username: The user's username.
            password: The user's password.

        Returns:
            A dict containing 'token' and 'expires_in' if authentication succeeds,
            None if credentials are invalid.
        """
        ...


class UserServiceInterface(ABC):
    """Interface for user management service."""

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            user_id: The unique identifier of the user.

        Returns:
            The User object if found, None otherwise.
        """
        ...

    @abstractmethod
    def create_user(self, username: str, email: str, password: str) -> User:
        """Create a new user.

        Args:
            username: The desired username.
            email: The user's email address.
            password: The user's password (will be hashed).

        Returns:
            The newly created User object.

        Raises:
            ValueError: If the username or email already exists.
        """
        ...


@runtime_checkable
class ServiceFactory(Protocol):
    """Protocol for service factory implementations."""

    def create_auth_service(self) -> AuthServiceInterface:
        """Create an authentication service instance."""
        ...

    def create_user_service(self) -> UserServiceInterface:
        """Create a user service instance."""
        ...
