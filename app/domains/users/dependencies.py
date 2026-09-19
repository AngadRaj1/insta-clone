import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.domains.users.models import User
from app.domains.users.repository import UserRepository

# This tells FastAPI where the client should go to get a token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        # Convert string back to UUID
        user_id = uuid.UUID(user_id_str)
        
    except (JWTError, ValueError):
        raise credentials_exception
        
    # 2. Fetch the user from the database
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    
    if user is None:
        raise credentials_exception
        
    # 3. Return the authenticated user object
    return user