import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from sqlalchemy import String, DateTime, func, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship


follows = Table(
    "follows",
    Base.metadata,
    
    Column("id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column("follower_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("followee_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now())
)

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    bio: Mapped[str | None] = mapped_column(String(150), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")

    # Add these two new relationships at the bottom of the User class
    
    # People this user is following
    following = relationship(
        "User",
        secondary=follows,
        primaryjoin="User.id == follows.c.follower_id",
        secondaryjoin="User.id == follows.c.followee_id",
        back_populates="followers"
    )

    # People following this user
    followers = relationship(
        "User",
        secondary=follows,
        primaryjoin="User.id == follows.c.followee_id",
        secondaryjoin="User.id == follows.c.follower_id",
        back_populates="following"
    )
    
    # A user can leave many comments
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    
    # A user can like many posts (we don't strictly need a back_populates here, just a simple list is fine)
    likes = relationship("Like", cascade="all, delete-orphan")


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    token = Column(String, unique=True, index=True, nullable=False)
    revoked_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
    expires_at = Column(DateTime, nullable=False)