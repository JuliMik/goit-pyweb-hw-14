from unittest.mock import Mock
import pytest

import app.services.auth

user = {
    "email": "john.doe@example.com",
    "password": "Secret_password",
    "username": "John",
}


def test_signup_success(client, monkeypatch):
    mock_create_user = Mock()
    mock_create_user.return_value = {
        "id": 1,
        "email": user["email"],
        "username": user["username"],
    }
    monkeypatch.setattr('app.repository.users.create_user', mock_create_user)

    response = client.post("/auth/signup", json=user)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == user["email"]
    assert data["username"] == user["username"]


def test_signup_duplicate(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("app.services.mail.send_confirmation_email", mock_send_email)

    response = client.post("/auth/signup", json=user)
    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Email already exists"


def test_login_success(client):
    client.post("/auth/signup", json=user)

    response = client.post("/auth/login", json={
        "email": user["email"],
        "password": user["password"],
        "username": user["username"]
    })

    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    client.post("/auth/signup", json=user)

    response = client.post("/auth/login", json={
        "email": user["email"],
        "password": "wrong_password",
        "username": user["username"]
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"


def test_login_not_existent_user(client):
    response = client.post("/auth/login", json={
        "email": "fail@example.com",
        "password": "pass",
        "username": "fail_username"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid credentials"


def test_get_me(client):
    client.post("/auth/signup", json=user)

    response = client.post("/auth/login", json={
        "email": user["email"],
        "password": user["password"],
        "username": user["username"]
    })
    assert response.status_code == 200
    token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user["email"]
    assert "id" in data
    assert "username" in data


def test_confirm_email(client):
    client.post("/auth/signup", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword"
    })
    token = app.services.auth.create_email_token({"sub": "newuser@example.com"})
    response = client.get(f"/auth/confirm-email/{token}")
    assert response.status_code == 200
    assert response.json() == {"message": "Email successfully confirmed"}
