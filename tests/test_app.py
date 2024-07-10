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


def test_update_user(client, user):
    user_public_schema = UserPublic.model_validate(user).model_dump()
    # Input data
    data = user_public_schema.copy()
    data.update({"password": "new_password"})
    # Expected
    expected = user_public_schema

    response = client.put("/users/1", json=data)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected


def test_update_user_not_found_error(client):
    data = {
        "id": 10,
        "username": "test2",
        "email": "test2@mail.com",
        "password": "super_secret",
    }
    response = client.put(f"/users/{data.get('id')}", json=data)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user(client, user):
    response = client.delete("/users/1")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_delete_user_not_found_error(client, user):
    response = client.delete("/users/10")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {"detail": "User not found"}
