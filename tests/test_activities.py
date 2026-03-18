"""Tests for the Mergington High School API."""

import pytest


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint."""

    def test_get_activities_returns_list(self, client):
        """Test that the /activities endpoint returns a list of activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, list)
        assert len(activities) > 0

    def test_get_activities_returns_correct_structure(self, client):
        """Test that activities have the expected structure."""
        response = client.get("/activities")
        activities = response.json()
        
        # Check first activity has required fields
        activity = activities[0]
        assert "id" in activity
        assert "name" in activity
        assert "description" in activity
        assert "schedule" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_includes_all_activities(self, client):
        """Test that all activities are returned."""
        response = client.get("/activities")
        activities = response.json()
        activity_names = [a["name"] for a in activities]
        
        assert "Soccer Team" in activity_names
        assert "Basketball Club" in activity_names
        assert "Art Studio" in activity_names
        assert "Theater Drama" in activity_names
        assert "Robotics Club" in activity_names
        assert "Debate Team" in activity_names
        assert "Chess Club" in activity_names
        assert "Programming Class" in activity_names
        assert "Gym Class" in activity_names

    def test_get_activities_includes_participants(self, client):
        """Test that activities include their participants."""
        response = client.get("/activities")
        activities = response.json()
        
        # Find Soccer Team
        soccer = next(a for a in activities if a["name"] == "Soccer Team")
        assert "alex@mergington.edu" in soccer["participants"]
        assert "ryan@mergington.edu" in soccer["participants"]


class TestSignupEndpoint:
    """Tests for the signup endpoint."""

    def test_signup_valid_activity_and_email(self, client):
        """Test successful signup for an activity."""
        response = client.post(
            "/activities/Soccer Team/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Soccer Team" in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity."""
        email = "newstudent@mergington.edu"
        
        # Signup
        response = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response.status_code == 200
        
        # Verify in activities list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        soccer = next(a for a in activities if a["name"] == "Soccer Team")
        assert email in soccer["participants"]

    def test_signup_duplicate_participant(self, client):
        """Test that signing up twice returns an error."""
        email = "alex@mergington.edu"  # Already signed up
        response = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]

    def test_signup_invalid_activity(self, client):
        """Test that signing up for non-existent activity returns 404."""
        response = client.post(
            "/activities/NonExistentActivity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with special characters in email."""
        email = "student+tag@mergington.edu"
        # Properly URL encode the email
        response = client.post(f"/activities/Chess Club/signup?email={email.replace('+', '%2B')}")
        assert response.status_code == 200
        
        # Verify in activities list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        chess = next(a for a in activities if a["name"] == "Chess Club")
        assert email in chess["participants"]

    def test_signup_multiple_different_activities(self, client):
        """Test that a student can sign up for multiple activities."""
        email = "student@mergington.edu"
        
        # Sign up for two activities
        response1 = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response2.status_code == 200
        
        # Verify in activities list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        soccer = next(a for a in activities if a["name"] == "Soccer Team")
        chess = next(a for a in activities if a["name"] == "Chess Club")
        assert email in soccer["participants"]
        assert email in chess["participants"]


class TestUnregisterEndpoint:
    """Tests for the unregister endpoint."""

    def test_unregister_existing_participant(self, client):
        """Test unregistering an existing participant from an activity."""
        email = "alex@mergington.edu"  # Already signed up for Soccer Team
        response = client.delete(
            f"/activities/Soccer Team/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant."""
        email = "alex@mergington.edu"
        
        # Unregister
        response = client.delete(f"/activities/Soccer Team/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify removed from activities list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        soccer = next(a for a in activities if a["name"] == "Soccer Team")
        assert email not in soccer["participants"]

    def test_unregister_non_existent_participant(self, client):
        """Test unregistering a participant not signed up for the activity."""
        email = "notstudent@mergington.edu"
        response = client.delete(
            f"/activities/Soccer Team/unregister?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"] or "not found" in data["detail"]

    def test_unregister_invalid_activity(self, client):
        """Test unregistering from non-existent activity returns 404."""
        response = client.delete(
            "/activities/NonExistentActivity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_after_unregister(self, client):
        """Test that a participant can sign up again after unregistering."""
        email = "alex@mergington.edu"
        
        # Unregister
        client.delete(f"/activities/Soccer Team/unregister?email={email}")
        
        # Sign up again
        response = client.post(f"/activities/Soccer Team/signup?email={email}")
        assert response.status_code == 200
        
        # Verify in activities list
        activities_response = client.get("/activities")
        activities = activities_response.json()
        soccer = next(a for a in activities if a["name"] == "Soccer Team")
        assert email in soccer["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_redirects_to_index(self, client):
        """Test that the root endpoint redirects to index.html."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
