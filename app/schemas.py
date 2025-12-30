from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostPublic(PostBase):
    id: int
    created_at: datetime
    user_id: int
    user: UserPublic

class PostPublicWithVotes(BaseModel):
    Post: PostPublic
    votes: int
   

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str | None


class Vote(BaseModel):
    post_id: int
    dir: bool