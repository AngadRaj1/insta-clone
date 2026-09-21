from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.domains.users.models import User
from app.domains.users.dependencies import get_current_user
from app.domains.posts.schemas import PostCreate, PostResponse, PostFeedResponse
from app.domains.posts.service import PostService
from typing import List
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from app.domains.posts.models import Post
from app.domains.interactions.models import Like, Comment


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


# @router.get("/", response_model=List[PostFeedResponse])
# async def get_global_feed(
#     limit: int = 20,
#     db: AsyncSession = Depends(get_db)
#     # Notice we removed current_user so even logged-out users can view the global feed (like Instagram's explore page)
# ):
#     service = PostService(db)
#     posts = await service.get_feed(limit)
#     return posts


@router.get("/", response_model=List[PostResponse])
async def get_posts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. Build the advanced SQLAlchemy query
    query = (
        select(
            Post,
            func.count(Like.id.distinct()).label("likes_count"),
            func.count(Comment.id.distinct()).label("comments_count"),
        )
        .outerjoin(Like, Like.post_id == Post.id)
        .outerjoin(Comment, Comment.post_id == Post.id)
        .options(selectinload(Post.owner)) # Ensure the user data loads
        .group_by(Post.id)
        .order_by(Post.created_at.desc())
    )

    result = await db.execute(query)
    rows = result.all()

    # 2. Format the data to match your PostResponse Pydantic schema
    formatted_posts = []
    for post, likes_count, comments_count in rows:
        # Check if the current user's ID exists in the likes for this post
        # (A quick DB call to check the specific like status)
        like_check = await db.execute(
            select(Like).where(Like.post_id == post.id, Like.user_id == current_user.id)
        )
        is_liked = like_check.scalar_one_or_none() is not None

        # Convert the SQLAlchemy model to a dictionary
        post_data = post.__dict__.copy()
        post_data["owner"] = post.owner
        post_data["likes_count"] = likes_count
        post_data["comments_count"] = comments_count
        post_data["is_liked"] = is_liked
        
        formatted_posts.append(post_data)

    return formatted_posts

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