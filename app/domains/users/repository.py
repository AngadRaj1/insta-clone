import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from app.domains.users.models import User, follows
from app.domains.users.schemas import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()


    async def create(self, user_data: UserCreate, hashed_password: str) -> User:
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user


    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def is_following(self, follower_id: uuid.UUID, followee_id: uuid.UUID) -> bool:
        query = select(follows).where(
            follows.c.follower_id == follower_id,
            follows.c.followee_id == followee_id
        )
        result = await self.session.execute(query)
        return result.first() is not None

    async def follow(self, follower_id: uuid.UUID, followee_id: uuid.UUID):
        stmt = insert(follows).values(follower_id=follower_id, followee_id=followee_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def unfollow(self, follower_id: uuid.UUID, followee_id: uuid.UUID):
        stmt = delete(follows).where(
            follows.c.follower_id == follower_id,
            follows.c.followee_id == followee_id
        )
        await self.session.execute(stmt)
        await self.session.commit()