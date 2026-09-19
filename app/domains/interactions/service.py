import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.interactions.repository import InteractionRepository

class InteractionService:
    def __init__(self, session: AsyncSession):
        self.repo = InteractionRepository(session)

    async def toggle_like(self, user_id: uuid.UUID, post_id: uuid.UUID):
        # Check if the user already liked this post
        if await self.repo.is_liked(user_id, post_id):
            await self.repo.unlike_post(user_id, post_id)
            return {"message": "Post unliked", "liked": False}
        else:
            await self.repo.like_post(user_id, post_id)
            return {"message": "Post liked", "liked": True}

    async def create_comment(self, user_id: uuid.UUID, post_id: uuid.UUID, text: str):
        # We assume the post_id exists here, but in production, you might verify it first!
        return await self.repo.add_comment(user_id, post_id, text)


    async def get_post_comments(self, post_id: uuid.UUID, limit: int = 50):
        return await self.repo.get_comments_for_post(post_id, limit)