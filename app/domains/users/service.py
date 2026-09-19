import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.users.schemas import UserCreate
from app.domains.users.repository import UserRepository
from app.core.security import get_password_hash, verify_password, create_access_token


class UserService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)

    async def register_user(self, user_data: UserCreate):
        # 1. Check if email or username is taken
        if await self.repo.get_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if await self.repo.get_by_username(user_data.username):
            raise HTTPException(status_code=400, detail="Username already taken")

        # 2. Hash the password
        hashed_password = get_password_hash(user_data.password)

        # 3. Save the user
        new_user = await self.repo.create(user_data, hashed_password)
        return new_user



    async def authenticate_user(self, email: str, password: str):
        # 1. Fetch the user by email
        user = await self.repo.get_by_email(email)
        
        # 2. Check if user exists AND password matches
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 3. Generate the JWT token containing the user's ID
        access_token = create_access_token(data={"sub": str(user.id)})
        
        return {"access_token": access_token, "token_type": "bearer"}



    async def follow_user(self, current_user_id: uuid.UUID, target_user_id: uuid.UUID):
        if current_user_id == target_user_id:
            raise HTTPException(status_code=400, detail="You cannot follow yourself")
            
        target_user = await self.repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if await self.repo.is_following(current_user_id, target_user_id):
            raise HTTPException(status_code=400, detail="You are already following this user")
            
        await self.repo.follow(current_user_id, target_user_id)
        return {"message": f"Successfully followed {target_user.username}"}

    async def unfollow_user(self, current_user_id: uuid.UUID, target_user_id: uuid.UUID):
        target_user = await self.repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        if not await self.repo.is_following(current_user_id, target_user_id):
            raise HTTPException(status_code=400, detail="You are not following this user")
            
        await self.repo.unfollow(current_user_id, target_user_id)
        return {"message": f"Successfully unfollowed {target_user.username}"}