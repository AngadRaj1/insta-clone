import uuid
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.posts.models import Post
from app.domains.posts.schemas import PostCreate
from app.domains.users.models import follows

class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, post_data: PostCreate, user_id: uuid.UUID) -> Post:
        new_post = Post(
            user_id=user_id,
            image_url=post_data.image_url,
            caption=post_data.caption
        )
        self.session.add(new_post)
        await self.session.commit()
        await self.session.refresh(new_post)
        return new_post


    async def get_latest(self, limit: int = 20) -> Sequence[Post]:
        query = (
            select(Post)
            .options(selectinload(Post.author)) # Eagerly load the user data
            .order_by(Post.created_at.desc())   # Newest posts first
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()


    async def get_personalized_feed(self, user_id: uuid.UUID, limit: int = 20) -> Sequence[Post]:
        # Step 1: Create a subquery to find all the IDs of users the current user follows
        followed_users_subquery = select(follows.c.followee_id).where(
            follows.c.follower_id == user_id
        )

        # Step 2: Fetch posts where the author is in that subquery OR the author is the user themselves
        query = (
            select(Post)
            .options(selectinload(Post.author)) # Eagerly load the author data
            .where(
                or_(
                    Post.user_id.in_(followed_users_subquery),
                    Post.user_id == user_id
                )
            )
            .order_by(Post.created_at.desc())
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return result.scalars().all()