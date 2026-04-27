"""API interfaces package.

This package defines abstract interfaces (protocols) for the API layer,
enforcing contracts between components and enabling dependency injection.
"""

from src.api.interfaces.controller_interface import (
    AuthControllerInterface,
    UserControllerInterface,
)
from src.api.interfaces.service_interface import (
    AuthServiceInterface,
    UserServiceInterface,
)
from src.api.interfaces.middleware_interface import (
    AuthMiddlewareInterface,
    ErrorHandlerInterface,
)
from src.api.interfaces.repository_interface import (
    UserRepositoryInterface,
)
from src.api.interfaces.dto_interface import (
    LoginRequestInterface,
    LoginResponseInterface,
    CreateUserRequestInterface,
    UserResponseInterface,
)

__all__ = [
    "AuthControllerInterface",
    "UserControllerInterface",
    "AuthServiceInterface",
    "UserServiceInterface",
    "AuthMiddlewareInterface",
    "ErrorHandlerInterface",
    "UserRepositoryInterface",
    "LoginRequestInterface",
    "LoginResponseInterface",
    "CreateUserRequestInterface",
    "UserResponseInterface",
]
"""API interfaces package.

This package defines abstract interfaces (protocols) for the API layer,
enforcing contracts between components and enabling dependency injection.
"""

from src.api.interfaces.controller_interface import (
    AuthControllerInterface,
    UserControllerInterface,
)
from src.api.interfaces.service_interface import (
    AuthServiceInterface,
    UserServiceInterface,
)
from src.api.interfaces.middleware_interface import (
    AuthMiddlewareInterface,
    ErrorHandlerInterface,
)
from src.api.interfaces.repository_interface import (
    UserRepositoryInterface,
)
from src.api.interfaces.dto_interface import (
    LoginRequestInterface,
    LoginResponseInterface,
    CreateUserRequestInterface,
    UserResponseInterface,
)

__all__ = [
    "AuthControllerInterface",
    "UserControllerInterface",
    "AuthServiceInterface",
    "UserServiceInterface",
    "AuthMiddlewareInterface",
    "ErrorHandlerInterface",
    "UserRepositoryInterface",
    "LoginRequestInterface",
    "LoginResponseInterface",
    "CreateUserRequestInterface",
    "UserResponseInterface",
]
