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


class LoginRequestInterface(BaseRequestDTO):
    """Interface for login request DTO.

    Attributes:
        username: User's username.
        password: User's password.
    """

    username: str
    password: str

    def to_domain(self) -> Dict[str, Any]:
        return {"username": self.username, "password": self.password}


class LoginResponseInterface(BaseResponseDTO):
    """Interface for login response DTO.

    Attributes:
        token: JWT token.
        expires_in: Token expiration time in seconds.
    """

    token: str
    expires_in: int

    def to_dict(self) -> Dict[str, Any]:
        return {"token": self.token, "expires_in": self.expires_in}


class CreateUserRequestInterface(BaseRequestDTO):
    """Interface for create user request DTO.

    Attributes:
        username: User's username.
        email: User's email address.
        password: User's password.
    """

    username: str
    email: str
    password: str

    def to_domain(self) -> Dict[str, Any]:
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
        }


class UserResponseInterface(BaseResponseDTO):
    """Interface for user response DTO.

    Attributes:
        id: User's unique identifier.
        username: User's username.
        email: User's email address.
        created_at: User creation timestamp.
    """

    id: int
    username: str
    email: str
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
        }
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
