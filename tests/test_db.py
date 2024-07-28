from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.models import Todo, User


def test_create_user(session: Session):
    user = User(username="test", email="test@test.com", password="secret")
    session.add(user)
    session.commit()
    session.refresh(
        user
    )  # inicializa/atualiza dados para id, create_at... direto no DB.
    result = session.scalar(select(User).where(User.email == "test@test.com"))
    assert result.id == 1
    assert result.username == "test"
    assert result.password == "secret"


def test_create_todo(session, user: User):
    todo = Todo(
        title="Test todo",
        description="Test Desc",
        state="draft",
        user_id=user.id,
    )
    session.add(todo)
    session.commit()
    session.refresh(todo)
    user = session.scalar(select(User).where(User.id == user.id))
    assert todo in user.todos
