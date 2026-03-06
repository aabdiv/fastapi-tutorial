import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base
from app.database import get_session

DATABASE_URL = f'postgresql://postgres:12347890@localhost:5432/fastapi_test'
engine = create_engine(DATABASE_URL, echo=False)

# override session dependency for path operations
# def get_session_test():
#     with Session(engine) as session:
#         Base.metadata.drop_all(engine)
#         Base.metadata.create_all(engine)
#         yield session

def get_session_test():
    with Session(engine) as session:
        yield session


# @pytest.fixture
# def session():
#     with Session(engine) as session:
#         Base.metadata.drop_all(engine)
#         Base.metadata.create_all(engine)
#         yield session


@pytest.fixture
def client():
    with Session(engine) as session:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    client = TestClient(app)
    app.dependency_overrides[get_session] = get_session_test
    return client


@pytest.fixture
def test_user(client):
    response = client.post("/users/", json={"email": "amogus@gmail.com", "password": "password123"})
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = "password123"
    return new_user