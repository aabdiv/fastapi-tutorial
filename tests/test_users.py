import jwt

from app import schemas
from app.config import settings


def test_root(client):
    response = client.get("/")
    assert response.json().get('message') == 'Hello world fella'
    assert response.status_code == 200


def test_create_user(client):
    response = client.post("/users/", json={"email": "amogus@gmail.com", "password": "password123"})
    user = schemas.UserPublic(**response.json())
    assert response.status_code == 201
    assert user.email == "amogus@gmail.com"


def test_login_user(client, test_user):
    response = client.post("/login", data={"username": test_user["email"], "password": test_user["password"]})
    login_output = schemas.Token(**response.json())
    
    payload = jwt.decode(login_output.access_token, settings.secret_key, algorithms=[settings.algorithm])
    sub = int(payload.get("sub"))
    
    assert response.status_code == 200
    assert sub == test_user["id"]
    assert login_output.token_type == "bearer"