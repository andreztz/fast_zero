from http import HTTPStatus

from fastapi import FastAPI
from fastapi.exceptions import HTTPException

# from starlette.exceptions import HTTPException
from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()

database = []


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Olá Mundo!"}


@app.post("/users/", response_model=UserPublic, status_code=HTTPStatus.CREATED)
def create_user(user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(user_with_id)
    return user_with_id


@app.get("/users/", response_model=UserList, status_code=HTTPStatus.OK)
def read_users():
    return {"users": database}


@app.get(
    "/users/{user_id}", response_model=UserPublic, status_code=HTTPStatus.OK
)
def read_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    return database[user_id - 1]


@app.put(
    "/users/{user_id}", response_model=UserPublic, status_code=HTTPStatus.OK
)
def update_user(user_id: int, user: UserSchema):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    user_with_id = UserDB(id=user_id, **user.model_dump())
    database[user_id - 1] = user_with_id
    return user_with_id


@app.delete("/users/{user_id}", response_model=Message)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    del database[user_id - 1]
    return {"message": "User deleted"}
