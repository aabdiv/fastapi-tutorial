

def test_vote_on_post(authorized_client, test_posts):
    response = authorized_client.post("/votes/", json={
        "post_id": test_posts[3].id,
        "dir": 1
    })
    assert response.status_code == 201
    assert response.json()["message"] == "successfully voted"


def test_vote_on_post_twice(authorized_client, test_posts_with_vote):
    response = authorized_client.post("/votes/", json={
        "post_id": test_posts_with_vote[0].post_id,
        "dir": True
    })
    assert response.status_code == 409


def test_delete_vote(authorized_client, test_posts_with_vote):
    response = authorized_client.post("/votes/", json={
        "post_id": test_posts_with_vote[0].post_id,
        "dir": False
    })
    assert response.status_code == 201
    assert response.json()["message"] == "vote retracted"


def test_delete_vote_non_exist(authorized_client, test_posts):
    response = authorized_client.post("/votes/", json={
        "post_id": test_posts[0].id,
        "dir": False
    })
    assert response.status_code == 409


def test_vote_post_non_exist(authorized_client, test_posts):
    response = authorized_client.post("/votes/", json={
        "post_id": 888,
        "dir": True
    })
    assert response.status_code == 404


def test_vote_unauthenticated_user(client, test_posts):
    response = client.post("/votes/", json={
        "post_id": test_posts[0].id,
        "dir": True
    })
    assert response.status_code == 401