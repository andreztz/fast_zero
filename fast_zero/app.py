from http import HTTPStatus

from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema

app = FastAPI()


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Olá Mundo!"}


@app.post("/users/", response_model=UserPublic, status_code=HTTPStatus.CREATED)
def create_user(
    user_schema: UserSchema, session: Session = Depends(get_session)
):
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
        password=user_schema.password,
        email=user_schema.email,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get("/users/", response_model=UserList, status_code=HTTPStatus.OK)
def read_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {"users": users}


@app.get(
    "/users/{user_id}", response_model=UserPublic, status_code=HTTPStatus.OK
)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    return user


@app.put(
    "/users/{user_id}", response_model=UserPublic, status_code=HTTPStatus.OK
)
def update_user(
    user_id: int,
    user_schema: UserSchema,
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    user.username = user_schema.username
    user.password = user_schema.password
    user.email = user_schema.email
    session.commit()
    session.refresh(user)
    return user


@app.delete("/users/{user_id}", response_model=Message)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    session.delete(user)
    session.commit()
    return {"message": "User deleted"}
