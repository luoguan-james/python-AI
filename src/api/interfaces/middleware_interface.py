"""Middleware interface definitions for the API layer."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import JSONResponse


class AuthMiddlewareInterface(ABC):
    """Interface for authentication middleware."""

    @abstractmethod
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token and return user payload.

        Args:
            token: The JWT token string.

        Returns:
            Dict containing user information (e.g., user_id, username).

        Raises:
            HTTPException: If token is invalid or expired.
        """
        ...

    @abstractmethod
    async def get_current_user(self, credentials: Any) -> Dict[str, Any]:
        """Extract and validate current user from request credentials.

        Args:
            credentials: The HTTP authorization credentials.

        Returns:
            Dict containing authenticated user information.
        """
        ...


class ErrorHandlerInterface(ABC):
    """Interface for error handling middleware."""

    @abstractmethod
    async def handle_domain_exception(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle domain-specific exceptions.

        Args:
            request: The incoming HTTP request.
            exc: The domain exception instance.

        Returns:
            JSONResponse with appropriate error status and message.
        """
        ...

    @abstractmethod
    async def handle_generic_exception(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected/generic exceptions.

        Args:
            request: The incoming HTTP request.
            exc: The exception instance.

        Returns:
            JSONResponse with 500 status and generic error message.
        """
        ...

    @abstractmethod
    def get_exception_handlers(self) -> Dict[type, Any]:
        """Return mapping of exception types to handler functions.

        Returns:
            Dict mapping exception classes to their handler callables.
        """
        ...
"""Middleware interface definitions for the API layer."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import JSONResponse


class AuthMiddlewareInterface(ABC):
    """Interface for authentication middleware."""

    @abstractmethod
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate a JWT token and return user payload.

        Args:
            token: The JWT token string.

        Returns:
            Dict containing user information (e.g., user_id, username).

        Raises:
            HTTPException: If token is invalid or expired.
        """
        ...

    @abstractmethod
    async def get_current_user(self, credentials: Any) -> Dict[str, Any]:
        """Extract and validate current user from request credentials.

        Args:
            credentials: The HTTP authorization credentials.

        Returns:
            Dict containing authenticated user information.
        """
        ...


class ErrorHandlerInterface(ABC):
    """Interface for error handling middleware."""

    @abstractmethod
    async def handle_domain_exception(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle domain-specific exceptions.

        Args:
            request: The incoming HTTP request.
            exc: The domain exception instance.

        Returns:
            JSONResponse with appropriate error status and message.
        """
        ...

    @abstractmethod
    async def handle_generic_exception(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected/generic exceptions.

        Args:
            request: The incoming HTTP request.
            exc: The exception instance.

        Returns:
            JSONResponse with 500 status and generic error message.
        """
        ...

    @abstractmethod
    def get_exception_handlers(self) -> Dict[type, Any]:
        """Return mapping of exception types to handler functions.

        Returns:
            Dict mapping exception classes to their handler callables.
        """
        ...
