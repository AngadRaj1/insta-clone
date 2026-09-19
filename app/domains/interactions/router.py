import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.domains.users.models import User
from app.domains.users.dependencies import get_current_user
from app.domains.interactions.schemas import CommentCreate, CommentResponse, CommentWithAuthorResponse
from app.domains.interactions.service import InteractionService



# We nest these under the /posts prefix for RESTful URLs
router = APIRouter(prefix="/posts", tags=["Interactions"])

@router.post("/{post_id}/like")
async def toggle_like(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Like or unlike a post (taps heart icon)"""
    service = InteractionService(db)
    return await service.toggle_like(current_user.id, post_id)

@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    post_id: uuid.UUID,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Leave a comment on a post"""
    service = InteractionService(db)
    return await service.create_comment(current_user.id, post_id, comment_data.text)

@router.get("/{post_id}/comments", response_model=List[CommentWithAuthorResponse])
async def get_comments(
    post_id: uuid.UUID,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Fetch all comments for a specific post"""
    service = InteractionService(db)
    return await service.get_post_comments(post_id, limit)