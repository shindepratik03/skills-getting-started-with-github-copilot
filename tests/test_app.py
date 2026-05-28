import copy
from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import activities, app

original_activities = copy.deepcopy(activities)
client = TestClient(app)


def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(original_activities))


def setup_function(function):
    reset_activities()


def teardown_function(function):
    reset_activities()


def test_get_activities_returns_all_activities():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_participant_to_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity}/signup"
    params = {"email": email}

    # Act
    response = client.post(url, params=params)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400_and_does_not_duplicate_participant():
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = activities[activity_name]["participants"][0]
    encoded_activity = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity}/signup"
    params = {"email": duplicate_email}
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(url, params=params)
    payload = response.json()

    # Assert
    assert response.status_code == 400
    assert payload["detail"] == "Student is already signed up for this activity"
    assert len(activities[activity_name]["participants"]) == initial_count


def test_remove_participant_unregisters_student():
    # Arrange
    activity_name = "Programming Class"
    remove_email = activities[activity_name]["participants"][0]
    encoded_activity = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity}/participants"
    params = {"email": remove_email}

    # Act
    response = client.delete(url, params=params)
    payload = response.json()

    # Assert
    assert response.status_code == 200
    assert payload["message"] == f"Removed {remove_email} from {activity_name}"
    assert remove_email not in activities[activity_name]["participants"]


def test_remove_non_registered_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "notregistered@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    url = f"/activities/{encoded_activity}/participants"
    params = {"email": email}

    # Act
    response = client.delete(url, params=params)
    payload = response.json()

    # Assert
    assert response.status_code == 404
    assert payload["detail"] == "Participant not registered"
