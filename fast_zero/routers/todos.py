from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.database import get_session
from fast_zero.models import Todo, User
from fast_zero.schemas import (
    Message,
    TodoListSchema,
    TodoPublicSchema,
    TodoSchema,
    TodoUpdateSchema,
)
from fast_zero.security import get_current_user

T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("/", response_model=TodoListSchema)
def list_todos(  # noqa
    session: T_Session,
    user: T_CurrentUser,
    title: str = Query(None),
    description: str = Query(None),
    state: str = Query(None),
    offset: int = Query(None),
    limit: int = Query(None),
):
    query = select(Todo).where(Todo.user_id == user.id)
    if title:
        query = query.filter(Todo.title.contains(title))
    if description:
        query = query.filter(Todo.description.contains(description))
    if state:
        query = query.filter(Todo.state == state)
    todos = session.scalars(query.offset(offset).limit(limit)).all()
    return {"todos": todos}


@router.post("/", response_model=TodoPublicSchema)
def create_todo(
    todo_schema: TodoSchema, user: T_CurrentUser, session: T_Session
):
    todo = Todo(
        title=todo_schema.title,
        description=todo_schema.description,
        state=todo_schema.state,
        user_id=user.id,
    )

    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.patch("/{todo_id}", response_model=TodoPublicSchema)
def patch_todo(
    todo_id: int,
    session: T_Session,
    user: T_CurrentUser,
    todo_update_schema: TodoUpdateSchema,
):
    todo = session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )
    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Task not found."
        )
    values_to_update = todo_update_schema.model_dump(exclude_unset=True)
    for key, value in values_to_update.items():
        setattr(todo, key, value)
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@router.delete("/{todo_id}", response_model=Message)
def delete_todo(todo_id: int, session: T_Session, user: T_CurrentUser):
    todo = session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Task not found."
        )
    session.delete(todo)
    session.commit()
    return {"message": "Task has been deleted successfully."}
