from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Olá Mundo!"}


def test_create_user(client):
    data = {
        "username": "test",
        "password": "super_secret",
        "email": "test@mail.com",
    }

    response = client.post("/users/", json=data)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": "test",
        "email": "test@mail.com",
    }


def test_read_users(client):
    expected = {
        "users": [{"id": 1, "username": "test", "email": "test@mail.com"}]
    }
    response = client.get("/users/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected


def test_read_user(client):
    expected = {"id": 1, "username": "test", "email": "test@mail.com"}
    response = client.get("/users/1")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected


def test_update_user(client):
    data = {
        "id": 1,
        "username": "test2",
        "email": "test2@mail.com",
        "password": "super_secret",
    }
    expected = {
        "id": 1,
        "username": "test2",
        "email": "test2@mail.com",
    }
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


def test_delete_user(client):
    response = client.delete("/users/1")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_delete_user_not_found_error(client):
    response = client.delete("/delete/10")
    assert response.status_code == HTTPStatus.NOT_FOUND
