"""Domain-specific exceptions."""


class DomainException(Exception):
    """Base exception for domain errors."""

    def __init__(self, message: str, status_code: int = 400, error_code: str = "DOMAIN_ERROR"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class AuthenticationError(DomainException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR")
