import pytest
from app import schemas

def test_get_all_posts(test_posts, authorized_client):
    response = authorized_client.get("/posts/")
    posts = list(map(lambda x: schemas.PostPublicWithVotes(**x), response.json()))
    # print(test_posts)
    assert len(response.json()) == len(test_posts)
    assert response.status_code == 200


def test_get_post(test_posts, authorized_client):
    response = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostPublicWithVotes(**response.json())
    assert post.Post.title == test_posts[0].title
    assert response.status_code == 200


def test_unauthenticated_get_all_posts(test_posts, client):
    response = client.get("/posts/")
    assert response.status_code == 401


def test_unauthenticated_get_post(test_posts, client):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401


def test_get_post_not_exist(test_posts, authorized_client):
    response = authorized_client.get("/posts/888")
    assert response.status_code == 404

@pytest.mark.parametrize("title, content, published", [
    ("some title 1", "some content 1", True),
    ("some title 2", "some content 2", False),
])
def test_create_post(authorized_client, test_user, title, content, published):
    response = authorized_client.post("/posts/", json={
        "title": title,
        "content": content,
        "published": published})
    new_post = schemas.PostPublic(**response.json())
    assert response.status_code == 201
    assert new_post.user_id == test_user["id"]
    assert new_post.title == title
    assert new_post.content == content
    assert new_post.published == published


def test_create_post_default_published_true(authorized_client):
    response = authorized_client.post("/posts/", json={
        "title": "some title",
        "content": "some content"})
    new_post = schemas.PostPublic(**response.json())
    assert response.status_code == 201
    assert new_post.published == True


def test_unauthenticated_create_post(client):
    response = client.post("/posts/", json={
        "title": "some title",
        "content": "some content"})
    assert response.status_code == 401


def test_unauthenticated_delete_post(test_posts, client):
    response = client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401


def test_delete_post_success(test_posts, authorized_client):
    response = authorized_client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 204


def test_delete_post_non_exist(test_posts, authorized_client):
    response = authorized_client.delete(f"/posts/{888}")
    assert response.status_code == 404


def test_delete_other_user_post(test_posts, test_user, test_user2, authorized_client):
    response = authorized_client.delete(f"/posts/{test_posts[3].id}")
    assert response.status_code == 403


def test_update_post(test_posts, test_user, authorized_client):
    response = authorized_client.put(f"/posts/{test_posts[0].id}", json={
        "title": "NEW TITLE",
        "content": "NEW CONTENT"})
    assert response.status_code == 200
    updated_post = schemas.PostPublic(**response.json())
    assert updated_post.title == "NEW TITLE"
    assert updated_post.content == "NEW CONTENT"
    assert updated_post.id == test_posts[0].id


def test_update_other_user_post(test_posts, test_user, test_user2, authorized_client):
    response = authorized_client.put(f"/posts/{test_posts[3].id}", json={
        "title": "NEW TITLE",
        "content": "NEW CONTENT"})
    assert response.status_code == 403


def test_unauthenticated_update_post(test_posts, test_user, test_user2, client):
    response = client.put(f"/posts/{test_posts[3].id}", json={
        "title": "NEW TITLE",
        "content": "NEW CONTENT"})
    assert response.status_code == 401


def test_update_post_non_exist(test_posts, authorized_client):
    response = authorized_client.put(f"/posts/{888}",  json={
        "title": "NEW TITLE",
        "content": "NEW CONTENT"})
    assert response.status_code == 404


