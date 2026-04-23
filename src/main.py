"""Application entry point."""

from fastapi import FastAPI

from src.api.controllers.auth_controller import router as auth_router
from src.api.controllers.user_controller import router as user_router
from src.api.middleware.error_handler import domain_exception_handler, generic_exception_handler
from src.services.exceptions import DomainException

app = FastAPI(title="Project API", version="1.0.0")

# Register routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")

# Register exception handlers
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
