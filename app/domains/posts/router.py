from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.domains.users.models import User
from app.domains.users.dependencies import get_current_user
from app.domains.posts.schemas import PostCreate, PostResponse, PostFeedResponse
from app.domains.posts.service import PostService
from typing import List


router = APIRouter(prefix="/posts", tags=["Posts"])

# @router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
# async def create_post(
#     post_data: PostCreate,
#     current_user: User = Depends(get_current_user), # The Bouncer!
#     db: AsyncSession = Depends(get_db)
# ):
#     service = PostService(db)
#     # We pass the logged-in user's ID directly to the service
#     new_post = await service.create_post(post_data, current_user.id)
#     return new_post


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    # Use File() for the image, and Form() for the caption text
    image: UploadFile = File(...),
    caption: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new post with an actual image file upload."""
    service = PostService(db)
    new_post = await service.create_post_with_image(image, caption, current_user.id)
    return new_post


@router.get("/", response_model=List[PostFeedResponse])
async def get_global_feed(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
    # Notice we removed current_user so even logged-out users can view the global feed (like Instagram's explore page)
):
    service = PostService(db)
    posts = await service.get_feed(limit)
    return posts


@router.get("/feed", response_model=List[PostFeedResponse])
async def get_personalized_timeline(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get posts only from the logged-in user and the people they follow."""
    service = PostService(db)
    posts = await service.get_timeline_feed(current_user.id, limit)
    return posts