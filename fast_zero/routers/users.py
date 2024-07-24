from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema
from fast_zero.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=UserPublic, status_code=HTTPStatus.CREATED)
def create_user(user_schema: UserSchema, session: T_Session):
    """
    Create user if not exists in database.
    """
    user = session.scalar(
        select(User).where(
            (User.username == user_schema.username)
            | (User.email == user_schema.email)
        )
    )
    if user:
        detail = None
        if user.username == user_schema.username:
            detail = "Username already exists."
        elif user.email == user_schema.email:
            detail = "Email already exists."
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=detail)

    user = User(
        username=user_schema.username,
        password=get_password_hash(user_schema.password),
        email=user_schema.email,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("/", response_model=UserList, status_code=HTTPStatus.OK)
def read_users(
    session: T_Session,
    skip: int = 0,
    limit: int = 100,
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {"users": users}


@router.get("/{user_id}", response_model=UserPublic, status_code=HTTPStatus.OK)
def read_user(user_id: int, session: T_Session):
    user = session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user_schema: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    # O currente_user não pode alterar outro usuário
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )
    current_user.username = user_schema.username
    current_user.password = get_password_hash(user_schema.password)
    current_user.email = user_schema.email
    session.commit()
    session.refresh(current_user)
    return current_user


@router.delete("/{user_id}", response_model=Message)
def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    # O currente_user não pode alterar outro usuário
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )
    session.delete(current_user)
    session.commit()
    return {"message": "User deleted"}
