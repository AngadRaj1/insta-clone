import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.domains.users.models import User
from app.domains.users.schemas import UserCreate, UserResponse
from app.domains.users.service import UserService
from fastapi.security import OAuth2PasswordRequestForm
from app.domains.users.schemas import Token
from app.domains.users.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    new_user = await service.register_user(user_data)
    return new_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    
    # Note: OAuth2PasswordRequestForm uses 'username' by default, 
    # but we can instruct the user to type their email into that field.
    token = await service.authenticate_user(
        email=form_data.username, 
        password=form_data.password
    )
    return token


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get the currently logged-in user's profile. 
    This route is protected by the get_current_user dependency!
    """
    return current_user


@router.post("/{target_user_id}/follow")
async def follow_user(
    target_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Follow another user"""
    service = UserService(db)
    return await service.follow_user(current_user.id, target_user_id)

@router.delete("/{target_user_id}/follow")
async def unfollow_user(
    target_user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unfollow a user"""
    service = UserService(db)
    return await service.unfollow_user(current_user.id, target_user_id)