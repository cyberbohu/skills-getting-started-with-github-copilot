"""
Tests for the FastAPI application
"""

import sys
from pathlib import Path

# Add the src directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app

# Create a test client
client = TestClient(app)


class TestGetActivities:
    """Test the /activities endpoint"""

    def test_get_activities_returns_list(self):
        """Test that /activities returns a list of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Basketball Team" in data
        assert "Soccer Club" in data

    def test_get_activities_contains_required_fields(self):
        """Test that each activity contains required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignup:
    """Test the signup endpoint"""

    def test_signup_new_participant(self):
        """Test signing up a new participant"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "test@mergington.edu" in data["message"]

    def test_signup_duplicate_participant(self):
        """Test that duplicate signups are rejected"""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Soccer%20Club/signup?email={email}"
        )
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Soccer%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_nonexistent_activity(self):
        """Test signing up for a non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestUnregister:
    """Test the unregister endpoint"""

    def test_unregister_existing_participant(self):
        """Test unregistering an existing participant"""
        email = "unregister_test@mergington.edu"
        activity = "Art%20Club"

        # First, sign up the participant
        client.post(f"/activities/{activity}/signup?email={email}")

        # Then unregister them
        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]

    def test_unregister_nonexistent_participant(self):
        """Test unregistering a participant who is not registered"""
        email = "notregistered@mergington.edu"
        activity = "Drama%20Club"

        response = client.delete(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]

    def test_unregister_nonexistent_activity(self):
        """Test unregistering from a non-existent activity"""
        response = client.delete(
            "/activities/NonExistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]


class TestRoot:
    """Test the root endpoint"""

    def test_root_redirect(self):
        """Test that root redirects to /static/index.html"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
