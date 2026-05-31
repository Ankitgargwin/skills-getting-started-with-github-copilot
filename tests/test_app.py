from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/")

    assert response.status_code == 200
    assert str(response.url).endswith("/static/index.html")


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_existing_activity():
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    # cleanup: remove the test registration so other tests remain deterministic
    client.post(f"/activities/{activity_name}/unregister", params={"email": email})


def test_signup_duplicate_returns_400():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_unknown_activity_returns_404():
    response = client.post("/activities/Nonexistent/signup", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity():
    activity_name = "Chess Club"
    email = "testuser@mergington.edu"

    # ensure the student is registered first
    add_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert add_response.status_code == 200

    response = client.post(f"/activities/{activity_name}/unregister", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}


def test_unregister_not_registered_returns_400():
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_unregister_unknown_activity_returns_404():
    response = client.post("/activities/Nonexistent/unregister", params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
