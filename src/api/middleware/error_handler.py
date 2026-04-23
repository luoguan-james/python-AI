"""Centralized error handling middleware."""

from fastapi import Request
from fastapi.responses import JSONResponse

from src.services.exceptions import DomainException


async def domain_exception_handler(request: Request, exc: DomainException):
    """Handle domain-specific exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "message": exc.message, "status_code": exc.status_code},
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_ERROR", "message": "An unexpected error occurred.", "status_code": 500},
    )
