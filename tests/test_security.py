from http import HTTPStatus

import pytest
from fastapi import HTTPException
from jwt import decode

from fast_zero.security import (
    create_access_token,
    get_current_user,
)
from fast_zero.settings import Settings

settings = Settings()


def test_jwt():
    data = {"sub": "test@mail.com"}
    token = create_access_token(data)
    result = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )
    assert result["sub"] == data["sub"]
    assert result["exp"]


def test_jwt_invalid_token(client):
    headers = {"Authorization": "Bearer token-invalido"}
    response = client.delete("/users/1", headers=headers)
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validate credentials"}


def test_get_current_user_not_found_exception(session):
    invalid_token = create_access_token(data={"sub": ""})

    with pytest.raises(HTTPException) as exc:
        get_current_user(session, invalid_token)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == "Could not validate credentials"
    assert exc.value.headers == {"WWW-Authenticate": "Bearer"}


def test_get_current_user_not_found_exception_with_invalid_user(session):
    invalid_token = create_access_token(data={"sub": "invalid_user"})

    with pytest.raises(HTTPException) as exc:
        get_current_user(session, invalid_token)

    assert exc.value.status_code == HTTPStatus.UNAUTHORIZED
    assert exc.value.detail == "Could not validate credentials"
    assert exc.value.headers == {"WWW-Authenticate": "Bearer"}


def test_get_current_user_with_valid_user(session, user, token):
    token = create_access_token(data={"sub": user.email})
    user = get_current_user(session, token)
    assert user.username == user.username
