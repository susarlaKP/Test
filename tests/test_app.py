"""
Tests for the Mergington High School Activities API
Uses the AAA (Arrange-Act-Assert) pattern
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to a known state before each test"""
    # Arrange: save original state
    original_participants = {name: list(details["participants"]) for name, details in activities.items()}
    yield
    # Restore original participants after each test
    for name, details in activities.items():
        details["participants"] = original_participants[name]


class TestGetActivities:
    def test_get_activities_returns_200(self):
        # Act
        response = client.get("/activities")
        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        # Act
        response = client.get("/activities")
        # Assert
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self):
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        # Act
        response = client.get("/activities")
        # Assert
        data = response.json()
        for activity in expected_activities:
            assert activity in data

    def test_get_activities_has_at_least_four(self):
        # Act
        response = client.get("/activities")
        # Assert
        assert len(response.json()) >= 4


class TestSignupForActivity:
    def test_signup_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_signup_returns_message(self):
        # Arrange
        activity_name = "Basketball Team"
        email = "test@mergington.edu"
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_signup_nonexistent_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_returns_400(self):
        # Arrange
        activity_name = "Chess Club"
        email = "duplicate@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")
        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()


class TestUnregisterFromActivity:
    def test_unregister_success(self):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_unregister_returns_message(self):
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        # Assert
        assert response.status_code == 200
        assert "message" in response.json()

    def test_unregister_nonexistent_activity_returns_404(self):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        # Assert
        assert response.status_code == 404

    def test_unregister_not_signed_up_returns_404(self):
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")
        # Assert
        assert response.status_code == 404
