from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from fast_zero.models import TodoState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    """User input data model"""

    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """Public user response data model"""

    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class TodoUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    state: str | None = None


class TodoSchema(BaseModel):
    """Todo input data model"""
    title: str
    description: str
    state: TodoState


class TodoPublicSchema(TodoSchema):
    """Public todo response data model"""
    id: int
    created_at: datetime
    updated_at: datetime


class TodoListSchema(BaseModel):
    todos: list[TodoPublicSchema]


class TokenData(BaseModel):
    username: str | None = None
