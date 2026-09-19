import uuid
from sqlalchemy import select, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.interactions.models import Like, Comment
from sqlalchemy.orm import selectinload
from typing import Sequence

class InteractionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_liked(self, user_id: uuid.UUID, post_id: uuid.UUID) -> bool:
        query = select(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        result = await self.session.execute(query)
        return result.first() is not None

    async def like_post(self, user_id: uuid.UUID, post_id: uuid.UUID):
        stmt = insert(Like).values(user_id=user_id, post_id=post_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def unlike_post(self, user_id: uuid.UUID, post_id: uuid.UUID):
        stmt = delete(Like).where(Like.user_id == user_id, Like.post_id == post_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def add_comment(self, user_id: uuid.UUID, post_id: uuid.UUID, text: str) -> Comment:
        new_comment = Comment(user_id=user_id, post_id=post_id, text=text)
        self.session.add(new_comment)
        await self.session.commit()
        await self.session.refresh(new_comment)
        return new_comment

    async def get_comments_for_post(self, post_id: uuid.UUID, limit: int = 50) -> Sequence[Comment]:
        query = (
            select(Comment)
            .where(Comment.post_id == post_id)
            .options(selectinload(Comment.author)) # Eagerly load the user who wrote it
            .order_by(Comment.created_at.asc())    # Oldest comments first, like standard Instagram
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()