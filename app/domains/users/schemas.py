from pydantic import BaseModel, EmailStr, ConfigDict
import uuid
from datetime import datetime

# What we expect from the user when they register
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# What we send back to the user (notice we DO NOT include the password!)
class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    bio: str | None
    created_at: datetime

    # This tells Pydantic to read data from a SQLAlchemy model
    model_config = ConfigDict(from_attributes=True)


# Add this to the bottom of app/domains/users/schemas.py
class Token(BaseModel):
    access_token: str
    token_type: str