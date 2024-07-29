from tests.conftest import client, test_db
from app.models import User

REGISTER_DATA = {
    "email": "test@gmail.com",
    "password": "@Test6627",
    "first_name": "omar",
    "last_name": "al-desi"
}


def test_register(client, test_db):
    response = client.post("/api/v1/auth/register", json=REGISTER_DATA)
    assert response.status_code == 201
    assert 'access_token' in response.json()
    assert 'refresh_token' in response.json()


def test_login(client, test_db):
    client.post("/api/v1/auth/register", json=REGISTER_DATA)
    response = client.post("/api/v1/auth/login", json={
        "email": REGISTER_DATA.get("email"),
        "password": REGISTER_DATA.get("password")
    })

    assert response.status_code == 200
    assert 'access_token' in response.json()
    assert 'refresh_token' in response.json()


def test_refresh(client, test_db):
    response = client.post("/api/v1/auth/register", json=REGISTER_DATA)
    assert response.status_code == 201

    refresh_token = response.json()['refresh_token']

    response_2 = client.post("/api/v1/auth/token/refresh", json={
        "refresh_token": refresh_token
    })

    assert response_2.status_code == 201
    assert 'access_token' in response_2.json()
    assert 'refresh_token' in response_2.json()

    # test invalid refresh token
    invalid_refresh_token = refresh_token + "1234312"
    response_3 = client.post("/api/v1/auth/token/refresh", json={
        "refresh_token": invalid_refresh_token
    })
    assert response_3.status_code == 401


if __name__ == "__main__":
    test_register(client, test_db)
    test_login(client, test_db)
    test_refresh(client, test_db)
