
from pydantic import BaseModel, EmailStr
import uuid
from fastapi_users import schemas as fastapi_users_schemas

class NalezInfo(BaseModel):
    id: int
    nazev: str
    datum: str | None
    lokace: str | None
    popis: str | None
    obrazek: str | None
    author_name: str | None = None

class NalezyListResponse(BaseModel):
    nalezy: list[NalezInfo]

class FriendRequest(BaseModel):
    sender_id: int
    receiver_id: int

class FriendAccept(BaseModel):
    request_id: int

class FriendInfo(BaseModel):
    id: int
    username: str
    email: str

class FriendListResponse(BaseModel):
    friends: list[FriendInfo]


class UserCreate(fastapi_users_schemas.BaseUserCreate):
    username: str
    email: EmailStr
    password: str



class UserRead(fastapi_users_schemas.BaseUser[uuid.UUID]):
    username: str
    email: EmailStr
    id: uuid.UUID


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
