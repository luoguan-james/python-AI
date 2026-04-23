"""User controller."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.services.user_service import UserService
from src.api.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: str


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: dict = Depends(get_current_user)):
    """Retrieve user by ID."""
    service = UserService()
    user = service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(
        id=user.id, username=user.username,
        email=user.email, created_at=user.created_at.isoformat()
    )


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(request: CreateUserRequest):
    """Create a new user."""
    service = UserService()
    user = service.create_user(request.username, request.email, request.password)
    return UserResponse(
        id=user.id, username=user.username, email=user.email, created_at=user.created_at.isoformat()
    )
