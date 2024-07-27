from http import HTTPStatus

from freezegun import freeze_time


def test_get_token(client, user):
    data = {"username": user.email, "password": user.clean_password}
    response = client.post("/auth/token/", data=data)
    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert token["token_type"] == "Bearer"
    assert "access_token" in token


def test_get_token_with_invalid_user(client, user):
    data = {"username": "invalid_user", "password": "password"}
    response = client.post("/auth/token/", data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Incorrect email or password"


def test_get_token_with_wrong_password(client, user):
    data = {"username": user.email, "password": "wrong_password"}
    response = client.post("/auth/token/", data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Incorrect email or password"


def test_token_expired_after_time(client, user):
    with freeze_time("2024-07-14 12:00:00"):
        response = client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2024-07-14 12:31:00"):
        response = client.put(
            f"/users/{user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "wrong_username",
                "email": "wrong_username@mail.com",
                "password": "wrong_password",
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}


def test_refresh_token(client, user, token):
    response = client.post(
        "/auth/refresh_token", headers={"Authorization": f"Bearer {token}"}
    )
    data = response.json()
    assert response.status_code == HTTPStatus.OK
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "Bearer"


def test_token_expired_dont_refresh(client, user):
    with freeze_time("2024-07-14 12:00:00"):
        response = client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time("2024-07-14 12:31:00"):
        response = client.post(
            "/auth/refresh_token", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validate credentials"}
