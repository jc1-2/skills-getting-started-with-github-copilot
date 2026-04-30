import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)
INITIAL_ACTIVITIES = copy.deepcopy(app_module.activities)


def setup_function(function):
    app_module.activities.clear()
    app_module.activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_activities():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_for_activity_adds_participant():
    activity_name = "Chess Club"
    email = "alex@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    response = client.get("/activities")
    assert email in response.json()[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_remove_participant_success():
    activity_name = "Chess Club"
    email = "daniel@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    response = client.get("/activities")
    assert email not in response.json()[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404():
    activity_name = "Chess Club"
    email = "unknown@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
