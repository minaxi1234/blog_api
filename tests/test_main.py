import pytest
import sys
import os

# 👇 Add the project root to Python's path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.core.dependencies import get_current_user

client = TestClient(app)




def override_get_current_user():
    return User(id=1, username="testuser", email="test@example.com", role="user")

app.dependency_overrides[get_current_user] = override_get_current_user



def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}

def test_create_post():
    post_data = {
        "title": "Test Post",
        "content": "This is a test post."
    }

    # 2️⃣ Send a POST request to /posts/
    response = client.post("/posts/", json=post_data)

    # 3️⃣ Check the status code
    assert response.status_code == 200

    # 4️⃣ Check the response content
    data = response.json()
    assert data["title"] == post_data["title"]
    assert data["content"] == post_data["content"]
    assert "id" in data
    assert "author_id" in data

def test_read_posts():
    # 1️⃣ Send a GET request to /posts/
    response = client.get("/posts/")

    # 2️⃣ Check if the request succeeded
    assert response.status_code == 200

    # 3️⃣ The response should be a list (array in JSON)
    data = response.json()
    assert isinstance(data, list)

    # 4️⃣ At least one post should exist (the one we created before)
    assert len(data) > 0

    # 5️⃣ The first post should have the keys "title" and "content"
    first_post = data[0]
    assert "title" in first_post
    assert "content" in first_post

def test_read_post_by_id():
    # 1️⃣ First create a post
    post_data = {"title": "Read Test", "content": "This is a read test post."}
    create_response = client.post("/posts/", json=post_data)
    assert create_response.status_code == 200
    created_post = create_response.json()

    # 2️⃣ Get the post by its id
    post_id = created_post["id"]
    response = client.get(f"/posts/{post_id}")

    # 3️⃣ Check the status code
    assert response.status_code == 200

    # 4️⃣ Verify the content
    post = response.json()
    assert post["title"] == post_data["title"]
    assert post["content"] == post_data["content"]




