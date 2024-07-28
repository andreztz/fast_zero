from pydantic import BaseModel, ConfigDict, EmailStr

from fast_zero.models import TodoState


class Message(BaseModel):
    message: str


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserDB(UserSchema):
    id: int


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class UserList(BaseModel):
    users: list[UserPublic]


class Token(BaseModel):
    access_token: str
    token_type: str


class TodoSchema(BaseModel):
    title: str
    description: str
    state: TodoState


class TodoPublicSchema(TodoSchema):
    id: int


class TodoListSchema(BaseModel):
    todos: list[TodoPublicSchema]


class TodoUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    state: str | None = None


class TokenData(BaseModel):
    username: str | None = None
