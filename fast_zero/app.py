from http import HTTPStatus

from fastapi import Depends, FastAPI
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.schemas import Message, UserList, UserPublic, UserSchema
from fast_zero.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

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
        password=get_password_hash(user_schema.password),
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


@app.put("/users/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user_schema: UserSchema,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # O currente_user não pode alterar outro usuário
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permissions"
        )
    current_user.username = user_schema.username
    current_user.password = get_password_hash(user_schema.password)
    current_user.email = user_schema.email
    session.commit()
    session.refresh(current_user)
    return current_user


@app.delete("/users/{user_id}", response_model=Message)
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # O currente_user não pode alterar outro usuário
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Not enough permissions"
        )
    session.delete(current_user)
    session.commit()
    return {"message": "User deleted"}


@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Incorrect email or password",
        )

    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "Bearer"}
