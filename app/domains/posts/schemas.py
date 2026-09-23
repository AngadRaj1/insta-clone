from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from app.domains.users.schemas import UserResponse

class PostCreate(BaseModel):
    image_url: str
    caption: str | None = None

class PostResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    image_url: str
    caption: str | None
    created_at: datetime
    author: UserResponse

    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False

    model_config = ConfigDict(from_attributes=True)


class Config:
        from_attributes = True

class PostAuthor(BaseModel):
    id: uuid.UUID
    username: str
    
    model_config = ConfigDict(from_attributes=True)

class PostFeedResponse(PostResponse):
    """Inherits everything from PostResponse, but adds the author"""
    author: PostAuthor