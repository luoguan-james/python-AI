"""Controller interface definitions.

Defines abstract base classes and protocols for API controllers,
ensuring consistent contract across all controller implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from fastapi import APIRouter


class BaseController(ABC):
    """Abstract base class for all API controllers.

    All controllers should inherit from this class and implement
    the required methods to ensure consistent routing and behavior.
    """

    @abstractmethod
    def get_router(self) -> APIRouter:
        """Return the FastAPI APIRouter instance for this controller.

        Returns:
            APIRouter: Configured router with all endpoint routes registered.
        """
        ...


class AuthControllerInterface(BaseController):
    """Interface for authentication controller.

    Defines the contract for user authentication endpoints.
    """

    @abstractmethod
    async def login(self, request: Any) -> Dict[str, Any]:
        """Authenticate user and return JWT token.

        Args:
            request: Login request containing username and password.

        Returns:
            Dict containing token and expires_in fields.

        Raises:
            HTTPException: If credentials are invalid (401).
        """
        ...


class UserControllerInterface(BaseController):
    """Interface for user management controller.

    Defines the contract for user CRUD endpoints.
    """

    @abstractmethod
    async def get_user(self, user_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve user by ID.

        Args:
            user_id: The unique identifier of the user.
            current_user: Authenticated user context from middleware.

        Returns:
            Dict containing user details (id, username, email, created_at).

        Raises:
            HTTPException: If user not found (404) or unauthorized (401).
        """
        ...

    @abstractmethod
    async def create_user(self, request: Any) -> Dict[str, Any]:
        """Create a new user.

        Args:
            request: CreateUserRequest containing username, email, and password.

        Returns:
            Dict containing created user details.

        Raises:
            HTTPException: If username already exists (409).
        """
        ...

    @abstractmethod
    async def update_user(self, user_id: int, request: Any, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user.

        Args:
            user_id: The unique identifier of the user to update.
            request: Update request containing fields to modify.
            current_user: Authenticated user context from middleware.

        Returns:
            Dict containing updated user details.

        Raises:
            HTTPException: If user not found (404) or unauthorized (401).
        """
        ...

    @abstractmethod
    async def delete_user(self, user_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user by ID.

        Args:
            user_id: The unique identifier of the user to delete.
            current_user: Authenticated user context from middleware.

        Returns:
            Dict containing confirmation of deletion.

        Raises:
            HTTPException: If user not found (404) or unauthorized (401).
        """
        ...

    @abstractmethod
    async def list_users(
        self, skip: int, limit: int, current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """List users with pagination.

        Args:
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.
            current_user: Authenticated user context from middleware.

        Returns:
            Dict containing list of users and pagination metadata.

        Raises:
            HTTPException: If unauthorized (401).
        """
        ...
"""Controller interface definitions.

Defines abstract base classes and protocols for API controllers,
ensuring consistent contract across all controller implementations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from fastapi import APIRouter


class BaseController(ABC):
    """Abstract base class for all API controllers.

    All controllers should inherit from this class and implement
    the required methods to ensure consistent routing and behavior.
    """

    @abstractmethod
    def get_router(self) -> APIRouter:
        """Return the FastAPI APIRouter instance for this controller.

        Returns:
            APIRouter: Configured router with all endpoint routes registered.
        """
        ...


class AuthControllerInterface(BaseController):
    """Interface for authentication controller.

    Defines the contract for user authentication endpoints.
    """

    @abstractmethod
    async def login(self, request: Any) -> Dict[str, Any]:
        """Authenticate user and return JWT token.

        Args:
            request: Login request containing username and password.

        Returns:
            Dict containing token and expires_in fields.

        Raises:
            HTTPException: If credentials are invalid (401).
        """
        ...


class UserControllerInterface(BaseController):
    """Interface for user management controller.

    Defines the contract for user CRUD endpoints.
    """

    @abstractmethod
    async def get_user(self, user_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve user by ID.

        Args:
            user_id: The unique identifier of the user.
            current_user: Authenticated user context from middleware.

        Returns:
            Dict containing user details (id, username, email, created_at).

        Raises:
            HTTPException: If user not found (404) or unauthorized (401).
        """
        ...

    @abstractmethod
    async def create_user(self, request: Any) -> Dict[str, Any]:
        """Create a new user.

        Args:
            request: CreateUserRequest containing username, email, and password.

        Returns:
            Dict containing created user details.

        Raises:
            HTTPException: If username already exists (409).
        """
        ...

    @abstractmethod
    async def update_user(self, user_id: int, request: Any, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing user.

        Args:
            user_id: The unique identifier of the user to update.
            request: Update request containing fields to modify.
            current_user: Authenticated user context from middleware.

        Returns:
            Dict containing updated user details.

        Raises:
            HTTPException: If user not found (404) or unauthorized (401).
        """
        ...

    @abstractmethod
    async def delete_user(self, user_id: int, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a user by ID.

        Args:
            user_id: The unique identifier of the user to delete.
            current_user: Authenticated user context from middleware.

        Returns:
            Dict containing confirmation of deletion.

        Raises:
            HTTPException: If user not found (404) or unauthorized (401).
        """
        ...

    @abstractmethod
    async def list_users(
        self, skip: int, limit: int, current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """List users with pagination.

        Args:
            skip: Number of records to skip (offset).
            limit: Maximum number of records to return.
            current_user: Authenticated user context from middleware.

        Returns:
            Dict containing list of users and pagination metadata.

        Raises:
            HTTPException: If unauthorized (401).
        """
        ...
