import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # The ForeignKey links this post to a specific user. 
    # ondelete="CASCADE" means if the user is deleted, their posts are deleted too.
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # We will store the URL of the image (e.g., an Amazon S3 link)
    image_url: Mapped[str] = mapped_column(String(500)) 
    
    # Instagram captions max out around 2200 characters
    caption: Mapped[str | None] = mapped_column(String(2200), nullable=True) 
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # This creates a "virtual" relationship so SQLAlchemy can easily fetch the user who made the post
    author = relationship("User", back_populates="posts")

    # A post has many comments
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    
    # A post has many likes
    likes = relationship("Like", cascade="all, delete-orphan")