from http import HTTPStatus

from fast_zero.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Olá Mundo!"}


def test_create_user(client):
    data = {
        "username": "Test",
        "email": "test@mail.com",
        "password": "super_secret",
    }

    response = client.post("/users/", json=data)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": "Test",
        "email": "test@mail.com",
    }


def test_create_user_already_exists(client, user):
    data = {
        "username": user.username,
        "password": "123456",
        "email": "bob@mail.com",
    }

    response = client.post("/users/", json=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Username already exists."}

    data = {
        "username": "bob",
        "password": "123456",
        "email": user.email,
    }

    response = client.post("/users/", json=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {"detail": "Email already exists."}


def test_read_user(client, user):
    user_public_schema = UserPublic.model_validate(user).model_dump()
    expected = user_public_schema
    response = client.get(f"/users/{user_public_schema.get('id')}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected


def test_read_users(client):
    expected = {"users": []}
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected


def test_read_user_with_users(client, user):
    user_public_schema = UserPublic.model_validate(user).model_dump()
    expected = {"users": [user_public_schema]}
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected


def test_read_user_not_found(client, user):
    response = client.get("/users/10")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}


def test_update_user(client, user, token):
    headers = {
        "Authorization": f"Bearer {token}",
    }
    data = {
        "username": "test",
        "email": "test@mail.com",
        "password": "new_super_secret_password",
    }
    expected = {"username": "test", "email": "test@mail.com", "id": user.id}

    response = client.put(f"/users/{user.id}", json=data, headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected


def test_update_user_not_found_error(client, token):
    headers = {
        "Authorization": f"Bearer {token}",
    }

    data = {
        "id": 10,
        "username": "test2",
        "email": "test2@mail.com",
        "password": "super_secret",
    }
    response = client.put(
        f"/users/{data.get('id')}", json=data, headers=headers
    )
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_delete_user(client, user, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/users/{user.id}", headers=headers)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_delete_user_not_found_error(client, user, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/users/10", headers=headers)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {"detail": "Not enough permissions"}


def test_get_token(client, user):
    data = {"username": user.email, "password": user.clean_password}
    response = client.post("/token/", data=data)
    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert token["token_type"] == "Bearer"
    assert "access_token" in token


def test_get_token_with_invalid_user(client, user):
    data = {"username": "invalid_user", "password": user.clean_password}
    response = client.post("/token/", data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == "Incorrect email or password"


def test_get_token_with_wrong_password(client, user):
    data = {"username": user.email, "password": "wrong_password"}
    response = client.post("/token/", data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == "Incorrect email or password"
