from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

class PostCreate(BaseModel):
    image_url: str
    caption: str | None = None

class PostResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    image_url: str
    caption: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



# Add this to the bottom of app/domains/posts/schemas.py

class PostAuthor(BaseModel):
    id: uuid.UUID
    username: str
    
    model_config = ConfigDict(from_attributes=True)

class PostFeedResponse(PostResponse):
    """Inherits everything from PostResponse, but adds the author"""
    author: PostAuthor