from http import HTTPStatus


def test_get_token(client, user):
    data = {"username": user.email, "password": user.clean_password}
    response = client.post("/auth/token/", data=data)
    assert response.status_code == HTTPStatus.OK
    token = response.json()
    assert token["token_type"] == "Bearer"
    assert "access_token" in token


def test_get_token_with_invalid_user(client, user):
    data = {"username": "invalid_user", "password": user.clean_password}
    response = client.post("/auth/token/", data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == "Incorrect email or password"


def test_get_token_with_wrong_password(client, user):
    data = {"username": user.email, "password": "wrong_password"}
    response = client.post("/auth/token/", data=data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()['detail'] == "Incorrect email or password"
