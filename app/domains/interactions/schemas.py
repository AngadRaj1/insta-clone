from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime


class CommentCreate(BaseModel):
    text: str

class CommentResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    post_id: uuid.UUID
    text: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CommentAuthor(BaseModel):
    id: uuid.UUID
    username: str
    
    model_config = ConfigDict(from_attributes=True)

class CommentWithAuthorResponse(CommentResponse):
    """Inherits the base comment fields and adds the author data"""
    author: CommentAuthor