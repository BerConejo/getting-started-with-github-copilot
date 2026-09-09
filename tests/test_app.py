from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def reset_activities():
    original = deepcopy(activities)
    activities.clear()
    activities.update(deepcopy(original))
    return original


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_seed_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()

    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert payload["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_new_participant():
    original = reset_activities()
    email = "student@mergington.edu"

    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]

    activities.clear()
    activities.update(deepcopy(original))


def test_signup_rejects_duplicate_participant():
    original = reset_activities()

    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }

    activities.clear()
    activities.update(deepcopy(original))


def test_signup_with_missing_activity_returns_404():
    response = client.post(
        "/activities/Unknown Activity/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_participant_removes_student_from_activity():
    original = reset_activities()
    email = "daniel@mergington.edu"

    response = client.delete(f"/activities/Chess Club/participants/{email}")

    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from Chess Club"
    }
    assert email not in activities["Chess Club"]["participants"]

    activities.clear()
    activities.update(deepcopy(original))


def test_unregister_missing_participant_returns_404():
    original = reset_activities()
    email = "not-registered@mergington.edu"

    response = client.delete(f"/activities/Chess Club/participants/{email}")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not registered for this activity"
    }

    activities.clear()
    activities.update(deepcopy(original))
