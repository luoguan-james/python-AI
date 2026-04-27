"""DTO (Data Transfer Object) interface definitions.

This module defines abstract base classes and protocols for all DTOs
used in the API layer, ensuring consistent request/response contracts.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel


class BaseRequestDTO(ABC, BaseModel):
    """Abstract base class for all request DTOs.

    Provides common validation and serialization contracts.
    """

    @abstractmethod
    def to_domain(self) -> Dict[str, Any]:
        """Convert the request DTO to a domain model dictionary."""
        ...

    class Config:
        """Pydantic configuration."""
        extra = "forbid"  # Reject unknown fields by default


class BaseResponseDTO(ABC, BaseModel):
    """Abstract base class for all response DTOs.

    Provides common serialization contracts for API responses.
    """

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert the response DTO to a dictionary."""
        ...


class PaginatedResponseDTO(BaseResponseDTO):
    """Generic paginated response DTO.

    Attributes:
        items: List of response items.
        total: Total number of items.
        page: Current page number.
        page_size: Number of items per page.
        total_pages: Total number of pages.
    """

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
        }


class ErrorResponseDTO(BaseResponseDTO):
    """Standard error response DTO.

    Attributes:
        error: Error code string.
        message: Human-readable error message.
        status_code: HTTP status code.
        details: Optional additional error details.
    """

    error: str
    message: str
    status_code: int
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "error": self.error,
            "message": self.message,
            "status_code": self.status_code,
        }
        if self.details:
            result["details"] = self.details
        return result
