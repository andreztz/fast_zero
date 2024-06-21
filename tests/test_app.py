from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_zero.app import app

client = TestClient(app)


def test_root_deve_retornar_ok_e_ola_mundo():
    response = client.get("/")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Olá Mundo!"}


def test_html_deve_retornar_paggina_html_contendo_ola_mundo():
    response = client.get("/html")
    assert response.status_code == HTTPStatus.OK
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert (
        response.text
        == """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Olá Mundo!</title>
            </head>
            <body>
                <h1>Olá Mundo!</h1>
            </body>
        </html>
    """
    )
    assert "Olá Mundo!" in response.text
