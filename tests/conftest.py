import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base
from app.database import get_session
from app.oauth2 import create_access_token
from app import models

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
def session():
    with Session(engine) as session:
        yield session


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


@pytest.fixture
def test_user2(client):
    response = client.post("/users/", json={"email": "bebris@gmail.com", "password": "password123"})
    assert response.status_code == 201
    new_user = response.json()
    new_user["password"] = "password123"
    return new_user


@pytest.fixture
def token(test_user):
    token = create_access_token({"sub": str(test_user['id'])})
    return token


@pytest.fixture
def authorized_client(token, client):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}" 
    }
    return client


@pytest.fixture
def test_posts(session, test_user, test_user2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "user_id": test_user['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "user_id": test_user['id']
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "user_id": test_user['id']
    }, {
        "title": "4th title",
        "content": "4th content",
        "user_id": test_user2['id']
    }]
    posts = map(lambda x: models.Post(**x), posts_data)
    session.add_all(posts)
    session.commit()

    posts = session.execute(select(models.Post)).scalars().all()
    return posts

@pytest.fixture
def test_posts_with_vote(session, test_user, test_user2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "user_id": test_user['id']
    }, {
        "title": "2nd title",
        "content": "2nd content",
        "user_id": test_user['id']
    },
        {
        "title": "3rd title",
        "content": "3rd content",
        "user_id": test_user['id']
    }, {
        "title": "4th title",
        "content": "4th content",
        "user_id": test_user2['id']
    }]

    posts = map(lambda x: models.Post(**x), posts_data)
    session.add_all(posts)
    session.commit()
    posts = session.execute(select(models.Post)).scalars().all()

    votes_data = [
        {"user_id": test_user['id'], "post_id": posts[0].id}
    ]
    votes = map(lambda x: models.Vote(**x), votes_data)
    session.add_all(votes)
    session.commit()
    votes = session.execute(select(models.Vote)).scalars().all()
    return votes