import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.domains.users.models import User, RevokedToken
from app.domains.users.schemas import UserCreate, UserResponse
from app.domains.users.service import UserService
from fastapi.security import OAuth2PasswordRequestForm
from app.domains.users.schemas import Token
from app.domains.users.dependencies import get_current_user, oauth2_scheme
from jose import jwt, JWTError
from app.core.config import settings

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


# @router.post(
#     "/logout",
#     status_code=status.HTTP_200_OK,
#     summary="Log out the current user",
# )
# async def logout(current_user: User = Depends(get_current_user)):
#     """
#     Logs out the authenticated user.
#     Because JWTs are stateless, client applications must delete
#     the stored access token from localStorage/storage upon receiving this response.
#     """
#     return {
#         "detail": f"Successfully logged out user {current_user.username}",
#         "action": "clear_local_token",
#     }


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Log out and invalidate current token",
)
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Invalidates the caller's JWT by adding it to the server-side blocklist."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        exp_timestamp = payload.get("exp")
        expires_at = (
            datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if exp_timestamp
            else datetime.utcnow()
        )
    except JWTError:
        expires_at = datetime.utcnow()

    # Save token to blocklist
    revoked_entry = RevokedToken(token=token, expires_at=expires_at)
    db.add(revoked_entry)
    await db.commit()

    return {"detail": "Successfully logged out and token invalidated."}


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