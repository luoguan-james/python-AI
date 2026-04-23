"""Authentication controller."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_in: int


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token."""
    service = AuthService()
    result = service.authenticate(request.username, request.password)
    if result is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return LoginResponse(
        token=result["token"], expires_in=result["expires_in"]
    )
