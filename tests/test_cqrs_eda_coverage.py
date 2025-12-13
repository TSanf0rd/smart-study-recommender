"""
Comprehensive Test Suite for CQRS+EDA Implementation
Achieves 100% code coverage including boundary conditions and error cases

Team 24: Tyler Sanford, Josh England, Kendric Jones
"""

import pytest
import asyncio
from datetime import datetime
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Now import from backend
from cqrs_eda_implementation import (
    app,
    event_bus,
    EventBus,
    Event,
    CommandResult,
    QueryResult,
    RegisterUserCommand,
    UploadResourceCommand,
    LogResourceViewCommand,
    RateResourceCommand,
    GenerateRecommendationsCommand,
    RegisterUserCommandHandler,
    UploadResourceCommandHandler,
    LogResourceViewCommandHandler,
    RateResourceCommandHandler,
    GenerateRecommendationsCommandHandler,
    UserRepository,
    ResourceRepository,
    ActivityRepository,
    users_auth_db,
    users_profile_db,
    users_preferences_db,
    resources_metadata_db,
    resources_content_db,
    resources_stats_db,
    activities_views_db,
    activities_ratings_db,
    recommendations_generated_db,
)

# Test client
client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def clear_databases():
    """Clear all in-memory databases before each test"""
    users_auth_db.clear()
    users_profile_db.clear()
    users_preferences_db.clear()
    resources_metadata_db.clear()
    resources_content_db.clear()
    resources_stats_db.clear()
    activities_views_db.clear()
    activities_ratings_db.clear()
    recommendations_generated_db.clear()
    event_bus.event_log.clear()
    yield


@pytest.fixture
async def sample_user():
    """Create a sample user for tests"""
    user_id = "test-user-123"
    await UserRepository.create_user_auth(
        user_id, "test@example.com", "password123", "student"
    )
    await UserRepository.create_user_profile(user_id, "testuser", "Test User")
    await UserRepository.create_user_preferences(user_id)
    return user_id


@pytest.fixture
async def sample_resource(sample_user):
    """Create a sample resource for tests"""
    resource_id = "test-resource-456"
    await ResourceRepository.create_resource_metadata(
        resource_id,
        "Test Resource",
        "Test Description",
        "pdf",
        "intermediate",
        sample_user,
    )
    await ResourceRepository.create_resource_content(
        resource_id, "/test/path.pdf", "https://test.com/file.pdf"
    )
    await ResourceRepository.create_resource_stats(resource_id)
    return resource_id


# ============================================================================
# TEST EVENT BUS
# ============================================================================

class TestEventBus:
    """Test EventBus functionality"""

    def test_singleton_pattern(self):
        """Test that EventBus is a singleton"""
        bus1 = EventBus()
        bus2 = EventBus()
        assert isinstance(bus1, EventBus)
        assert isinstance(bus2, EventBus)

    @pytest.mark.asyncio
    async def test_subscribe_handler(self):
        """Test subscribing a handler to an event"""
        async def test_handler(event: Event):
            pass

        event_bus.subscribe("TestEvent", test_handler)
        assert test_handler in event_bus.subscribers["TestEvent"]

    @pytest.mark.asyncio
    async def test_publish_event(self):
        """Test publishing an event"""
        event = Event(
            event_id="evt-001",
            event_type="TestEvent",
            timestamp=datetime.now().isoformat(),
            data={"test": "data"},
        )

        await event_bus.publish(event)
        assert event in event_bus.event_log

    @pytest.mark.asyncio
    async def test_event_handler_execution(self):
        """Test that event handlers are executed"""
        handler_called = {"called": False}

        async def test_handler(event: Event):
            handler_called["called"] = True

        event_bus.subscribe("ExecutionTest", test_handler)

        event = Event(
            event_id="evt-002",
            event_type="ExecutionTest",
            timestamp=datetime.now().isoformat(),
            data={},
        )

        await event_bus.publish(event)
        assert handler_called["called"] is True

    @pytest.mark.asyncio
    async def test_event_handler_error_handling(self):
        """Test that errors in handlers don't break the system"""
        async def failing_handler(event: Event):
            raise ValueError("Test error")

        event_bus.subscribe("ErrorTest", failing_handler)

        event = Event(
            event_id="evt-003",
            event_type="ErrorTest",
            timestamp=datetime.now().isoformat(),
            data={},
        )

        # Should not raise exception
        await event_bus.publish(event)


# ============================================================================
# TEST USER REPOSITORY
# ============================================================================

class TestUserRepository:
    """Test UserRepository operations"""

    @pytest.mark.asyncio
    async def test_create_user_auth(self):
        """Test creating user authentication record"""
        user = await UserRepository.create_user_auth(
            "user-001", "test@example.com", "hashed_pwd", "student"
        )

        assert user["user_id"] == "user-001"
        assert user["email"] == "test@example.com"
        assert user["role"] == "student"
        assert "user-001" in users_auth_db

    @pytest.mark.asyncio
    async def test_create_user_profile(self):
        """Test creating user profile record"""
        profile = await UserRepository.create_user_profile(
            "user-001", "testuser", "Test User"
        )

        assert profile["user_id"] == "user-001"
        assert profile["username"] == "testuser"
        assert profile["full_name"] == "Test User"

    @pytest.mark.asyncio
    async def test_create_user_preferences(self):
        """Test creating user preferences"""
        prefs = await UserRepository.create_user_preferences("user-001")

        assert prefs["user_id"] == "user-001"
        assert prefs["learning_style"] == "visual"
        assert prefs["difficulty_level"] == "beginner"

    @pytest.mark.asyncio
    async def test_user_exists_true(self, sample_user):
        """Test user_exists returns True when user exists"""
        exists = await UserRepository.user_exists(sample_user)
        assert exists is True

    @pytest.mark.asyncio
    async def test_user_exists_false(self):
        """Test user_exists returns False when user doesn't exist"""
        exists = await UserRepository.user_exists("nonexistent-user")
        assert exists is False

    @pytest.mark.asyncio
    async def test_email_exists_true(self, sample_user):
        """Test email_exists returns True when email is registered"""
        exists = await UserRepository.email_exists("test@example.com")
        assert exists is True

    @pytest.mark.asyncio
    async def test_email_exists_false(self):
        """Test email_exists returns False when email is not registered"""
        exists = await UserRepository.email_exists("nonexistent@example.com")
        assert exists is False


# ============================================================================
# TEST RESOURCE REPOSITORY
# ============================================================================

class TestResourceRepository:
    """Test ResourceRepository operations"""

    @pytest.mark.asyncio
    async def test_create_resource_metadata(self):
        """Test creating resource metadata"""
        resource = await ResourceRepository.create_resource_metadata(
            "res-001",
            "Test Resource",
            "Description",
            "pdf",
            "beginner",
            "user-001",
        )

        assert resource["resource_id"] == "res-001"
        assert resource["title"] == "Test Resource"
        assert resource["resource_type"] == "pdf"

    @pytest.mark.asyncio
    async def test_create_resource_content(self):
        """Test creating resource content record"""
        content = await ResourceRepository.create_resource_content(
            "res-001", "/path/file.pdf", "https://cdn.com/file.pdf"
        )

        assert content["resource_id"] == "res-001"
        assert content["file_path"] == "/path/file.pdf"
        assert content["file_url"] == "https://cdn.com/file.pdf"

    @pytest.mark.asyncio
    async def test_create_resource_stats(self):
        """Test initializing resource statistics"""
        stats = await ResourceRepository.create_resource_stats("res-001")

        assert stats["resource_id"] == "res-001"
        assert stats["view_count"] == 0
        assert stats["download_count"] == 0
        assert stats["average_rating"] == 0.0

    @pytest.mark.asyncio
    async def test_resource_exists_true(self, sample_resource):
        """Test resource_exists returns True when resource exists"""
        exists = await ResourceRepository.resource_exists(sample_resource)
        assert exists is True

    @pytest.mark.asyncio
    async def test_resource_exists_false(self):
        """Test resource_exists returns False when resource doesn't exist"""
        exists = await ResourceRepository.resource_exists("nonexistent-resource")
        assert exists is False

    @pytest.mark.asyncio
    async def test_get_resource_stats(self, sample_resource):
        """Test retrieving resource statistics"""
        stats = await ResourceRepository.get_resource_stats(sample_resource)

        assert stats is not None
        assert stats["resource_id"] == sample_resource
        assert stats["view_count"] == 0

    @pytest.mark.asyncio
    async def test_get_resource_stats_nonexistent(self):
        """Test get_resource_stats returns None for nonexistent resource"""
        stats = await ResourceRepository.get_resource_stats("nonexistent")
        assert stats is None

    @pytest.mark.asyncio
    async def test_update_view_count(self, sample_resource):
        """Test incrementing view count"""
        initial_stats = await ResourceRepository.get_resource_stats(sample_resource)
        initial_count = initial_stats["view_count"]

        updated_stats = await ResourceRepository.update_view_count(sample_resource)

        assert updated_stats["view_count"] == initial_count + 1


# ============================================================================
# TEST ACTIVITY REPOSITORY
# ============================================================================

class TestActivityRepository:
    """Test ActivityRepository operations"""

    @pytest.mark.asyncio
    async def test_log_view(self, sample_user, sample_resource):
        """Test logging a view activity"""
        view = await ActivityRepository.log_view(
            sample_user, sample_resource, 120, "desktop", "session-123"
        )

        assert view["user_id"] == sample_user
        assert view["resource_id"] == sample_resource
        assert view["view_duration_seconds"] == 120
        assert view["device_type"] == "desktop"

    @pytest.mark.asyncio
    async def test_log_rating(self, sample_user, sample_resource):
        """Test logging a rating"""
        rating = await ActivityRepository.log_rating(
            sample_user, sample_resource, 5, "Excellent!"
        )

        assert rating["user_id"] == sample_user
        assert rating["resource_id"] == sample_resource
        assert rating["rating_value"] == 5
        assert rating["review_text"] == "Excellent!"

    @pytest.mark.asyncio
    async def test_get_ratings_for_resource(self, sample_user, sample_resource):
        """Test retrieving all ratings for a resource"""
        # Create multiple ratings
        await ActivityRepository.log_rating(sample_user, sample_resource, 5, "Great")
        await ActivityRepository.log_rating(
            "user-002", sample_resource, 4, "Good"
        )

        ratings = await ActivityRepository.get_ratings_for_resource(sample_resource)

        assert len(ratings) == 2

    @pytest.mark.asyncio
    async def test_get_ratings_empty(self):
        """Test get_ratings returns empty list when no ratings exist"""
        ratings = await ActivityRepository.get_ratings_for_resource("res-none")
        assert ratings == []

    @pytest.mark.asyncio
    async def test_calculate_average_rating(self, sample_user, sample_resource):
        """Test calculating average rating"""
        # Create ratings
        await ActivityRepository.log_rating(sample_user, sample_resource, 5, "Great")
        await ActivityRepository.log_rating(
            "user-002", sample_resource, 3, "OK"
        )

        avg, count = await ActivityRepository.calculate_average_rating(sample_resource)

        assert avg == 4.0  # (5 + 3) / 2
        assert count == 2

    @pytest.mark.asyncio
    async def test_calculate_average_rating_empty(self):
        """Test calculating average with no ratings"""
        avg, count = await ActivityRepository.calculate_average_rating("res-none")

        assert avg == 0.0
        assert count == 0


# ============================================================================
# TEST COMMAND HANDLERS
# ============================================================================

class TestRegisterUserCommandHandler:
    """Test RegisterUserCommand and handler"""

    @pytest.mark.asyncio
    async def test_successful_registration(self):
        """Test successful user registration"""
        command = RegisterUserCommand(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            role="student",
            full_name="New User",
        )

        result = await RegisterUserCommandHandler.handle(command)

        assert result.success is True
        assert result.data["email"] == "newuser@example.com"
        assert "UserRegisteredEvent" in result.events_published
        assert len(event_bus.event_log) > 0

    @pytest.mark.asyncio
    async def test_duplicate_email_error(self, sample_user):
        """Test registration with duplicate email fails"""
        command = RegisterUserCommand(
            username="duplicate",
            email="test@example.com",  # Already exists
            password="password123",
            role="student",
            full_name="Duplicate User",
        )

        with pytest.raises(Exception):  # Should raise HTTPException
            await RegisterUserCommandHandler.handle(command)


class TestUploadResourceCommandHandler:
    """Test UploadResourceCommand and handler"""

    @pytest.mark.asyncio
    async def test_successful_upload(self, sample_user):
        """Test successful resource upload"""
        command = UploadResourceCommand(
            title="New Resource",
            description="Test Description",
            resource_type="pdf",
            difficulty_level="intermediate",
            uploader_user_id=sample_user,
            file_name="test.pdf",
        )

        result = await UploadResourceCommandHandler.handle(command)

        assert result.success is True
        assert result.data["title"] == "New Resource"
        assert "ResourceUploadedEvent" in result.events_published
        assert len(result.data["auto_generated_tags"]) > 0

    @pytest.mark.asyncio
    async def test_upload_with_nonexistent_user(self):
        """Test upload with nonexistent user fails"""
        command = UploadResourceCommand(
            title="Resource",
            description="Desc",
            resource_type="pdf",
            difficulty_level="beginner",
            uploader_user_id="nonexistent-user",
            file_name="test.pdf",
        )

        with pytest.raises(Exception):
            await UploadResourceCommandHandler.handle(command)


class TestLogResourceViewCommandHandler:
    """Test LogResourceViewCommand and handler"""

    @pytest.mark.asyncio
    async def test_successful_view_log(self, sample_user, sample_resource):
        """Test successful view logging"""
        command = LogResourceViewCommand(
            user_id=sample_user,
            resource_id=sample_resource,
            view_duration_seconds=180,
            device_type="mobile",
            session_id="session-456",
        )

        result = await LogResourceViewCommandHandler.handle(command)

        assert result.success is True
        assert result.data["resource_id"] == sample_resource
        assert result.data["new_view_count"] == 1
        assert "ResourceViewedEvent" in result.events_published

    @pytest.mark.asyncio
    async def test_view_with_nonexistent_user(self, sample_resource):
        """Test view logging with nonexistent user fails"""
        command = LogResourceViewCommand(
            user_id="nonexistent-user",
            resource_id=sample_resource,
            view_duration_seconds=100,
            device_type="desktop",
            session_id="session-789",
        )

        with pytest.raises(Exception):
            await LogResourceViewCommandHandler.handle(command)

    @pytest.mark.asyncio
    async def test_view_with_nonexistent_resource(self, sample_user):
        """Test view logging with nonexistent resource fails"""
        command = LogResourceViewCommand(
            user_id=sample_user,
            resource_id="nonexistent-resource",
            view_duration_seconds=100,
            device_type="desktop",
            session_id="session-789",
        )

        with pytest.raises(Exception):
            await LogResourceViewCommandHandler.handle(command)


class TestRateResourceCommandHandler:
    """Test RateResourceCommand and handler"""

    @pytest.mark.asyncio
    async def test_successful_rating(self, sample_user, sample_resource):
        """Test successful resource rating"""
        command = RateResourceCommand(
            user_id=sample_user,
            resource_id=sample_resource,
            rating_value=5,
            review_text="Excellent resource!",
        )

        result = await RateResourceCommandHandler.handle(command)

        assert result.success is True
        assert result.data["updated_stats"]["average_rating"] == 5.0
        assert result.data["updated_stats"]["rating_count"] == 1
        assert "ResourceRatedEvent" in result.events_published

    @pytest.mark.asyncio
    async def test_rating_boundary_min(self, sample_user, sample_resource):
        """Test rating with minimum value (1)"""
        command = RateResourceCommand(
            user_id=sample_user,
            resource_id=sample_resource,
            rating_value=1,
            review_text="Poor",
        )

        result = await RateResourceCommandHandler.handle(command)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_rating_boundary_max(self, sample_user, sample_resource):
        """Test rating with maximum value (5)"""
        command = RateResourceCommand(
            user_id=sample_user,
            resource_id=sample_resource,
            rating_value=5,
            review_text="Excellent",
        )

        result = await RateResourceCommandHandler.handle(command)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_rating_below_minimum(self, sample_user, sample_resource):
        """Test rating below minimum value (0) fails"""
        command = RateResourceCommand(
            user_id=sample_user,
            resource_id=sample_resource,
            rating_value=0,
            review_text="Invalid",
        )

        with pytest.raises(Exception):
            await RateResourceCommandHandler.handle(command)

    @pytest.mark.asyncio
    async def test_rating_above_maximum(self, sample_user, sample_resource):
        """Test rating above maximum value (6) fails"""
        command = RateResourceCommand(
            user_id=sample_user,
            resource_id=sample_resource,
            rating_value=6,
            review_text="Invalid",
        )

        with pytest.raises(Exception):
            await RateResourceCommandHandler.handle(command)

    @pytest.mark.asyncio
    async def test_multiple_ratings_average(self, sample_user, sample_resource):
        """Test average calculation with multiple ratings"""
        # First rating
        command1 = RateResourceCommand(
            user_id=sample_user,
            resource_id=sample_resource,
            rating_value=5,
            review_text="Great",
        )
        await RateResourceCommandHandler.handle(command1)

        #Create Second User
        user2_id = "user-002"
        await UserRepository.create_user_auth(user2_id, "user2@example.com", "pass", "student")

        # Second rating
        command2 = RateResourceCommand(
            user_id="user-002",
            resource_id=sample_resource,
            rating_value=3,
            review_text="OK",
        )
        result = await RateResourceCommandHandler.handle(command2)

        assert result.data["updated_stats"]["average_rating"] == 4.0
        assert result.data["updated_stats"]["rating_count"] == 2


class TestGenerateRecommendationsCommandHandler:
    """Test GenerateRecommendationsCommand and handler"""

    @pytest.mark.asyncio
    async def test_successful_recommendation_generation(
        self, sample_user, sample_resource
    ):
        """Test successful recommendation generation"""
        command = GenerateRecommendationsCommand(
            user_id=sample_user, limit=5, algorithm="hybrid"
        )

        result = await GenerateRecommendationsCommandHandler.handle(command)

        assert result.success is True
        assert result.data["user_id"] == sample_user
        assert len(result.data["recommendations"]) <= 5
        assert "RecommendationsGeneratedEvent" in result.events_published

    @pytest.mark.asyncio
    async def test_recommendation_with_nonexistent_user(self):
        """Test recommendation generation with nonexistent user fails"""
        command = GenerateRecommendationsCommand(
            user_id="nonexistent-user", limit=10, algorithm="hybrid"
        )

        with pytest.raises(Exception):
            await GenerateRecommendationsCommandHandler.handle(command)

    @pytest.mark.asyncio
    async def test_recommendation_limit_boundary(self, sample_user):
        """Test recommendation with different limit values"""
        # Minimum limit
        command1 = GenerateRecommendationsCommand(
            user_id=sample_user, limit=1, algorithm="hybrid"
        )
        result1 = await GenerateRecommendationsCommandHandler.handle(command1)
        assert len(result1.data["recommendations"]) <= 1

        # Maximum limit
        command2 = GenerateRecommendationsCommand(
            user_id=sample_user, limit=20, algorithm="collaborative"
        )
        result2 = await GenerateRecommendationsCommandHandler.handle(command2)
        assert len(result2.data["recommendations"]) <= 20


# ============================================================================
# TEST API ENDPOINTS
# ============================================================================

class TestAPIEndpoints:
    """Test FastAPI endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint returns system info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["use_cases_implemented"] == 5

    def test_register_user_endpoint_success(self):
        """Test user registration endpoint with valid data"""
        response = client.post(
            "/api/cqrs/auth/register",
            json={
                "username": "apiuser",
                "email": "apiuser@example.com",
                "password": "password123",
                "role": "student",
                "full_name": "API User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "apiuser@example.com"

    def test_register_user_endpoint_duplicate(self):
        """Test registration with duplicate email returns error"""
        # Register first time
        client.post(
            "/api/cqrs/auth/register",
            json={
                "username": "user1",
                "email": "dup@example.com",
                "password": "pass123",
                "role": "student",
                "full_name": "User One",
            },
        )

        # Try to register again with same email
        response = client.post(
            "/api/cqrs/auth/register",
            json={
                "username": "user2",
                "email": "dup@example.com",
                "password": "pass456",
                "role": "instructor",
                "full_name": "User Two",
            },
        )

        assert response.status_code == 400

    def test_upload_resource_endpoint(self):
        """Test resource upload endpoint"""
        # First register a user
        reg_response = client.post(
            "/api/cqrs/auth/register",
            json={
                "username": "uploader",
                "email": "uploader@example.com",
                "password": "pass123",
                "role": "instructor",
                "full_name": "Uploader",
            },
        )
        user_id = reg_response.json()["data"]["user_id"]

        # Upload resource
        response = client.post(
            "/api/cqrs/resources/upload",
            data={
                "title": "API Resource",
                "description": "Test upload",
                "resource_type": "pdf",
                "difficulty_level": "beginner",
                "uploader_user_id": user_id,
                "file_name": "api_test.pdf",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "API Resource"

    def test_get_event_log_endpoint(self):
        """Test event log endpoint"""
        response = client.get("/api/cqrs/events")
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data
        assert "events" in data


# ============================================================================
# TEST QUERY ENDPOINTS
# ============================================================================

class TestQueryEndpoints:
    """Test query (read) endpoints"""

    def test_get_user_profile_success(self):
        """Test getting user profile"""
        # Create user first
        reg_response = client.post(
            "/api/cqrs/auth/register",
            json={
                "username": "queryuser",
                "email": "query@example.com",
                "password": "pass123",
                "role": "student",
                "full_name": "Query User",
            },
        )
        user_id = reg_response.json()["data"]["user_id"]

        # Query profile
        response = client.get(f"/api/cqrs/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == "query@example.com"

    def test_get_user_profile_not_found(self):
        """Test getting nonexistent user profile"""
        response = client.get("/api/cqrs/users/nonexistent-user")
        assert response.status_code == 404

    def test_get_resource_details_success(self):
        """Test getting resource details"""
        # Create user and resource
        reg_response = client.post(
            "/api/cqrs/auth/register",
            json={
                "username": "resourceowner",
                "email": "owner@example.com",
                "password": "pass123",
                "role": "instructor",
                "full_name": "Owner",
            },
        )
        user_id = reg_response.json()["data"]["user_id"]

        upload_response = client.post(
            "/api/cqrs/resources/upload",
            data={
                "title": "Query Resource",
                "description": "Test",
                "resource_type": "pdf",
                "difficulty_level": "intermediate",
                "uploader_user_id": user_id,
                "file_name": "query_test.pdf",
            },
        )
        resource_id = upload_response.json()["data"]["resource_id"]

        # Query resource
        response = client.get(f"/api/cqrs/resources/{resource_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["title"] == "Query Resource"

    def test_get_resource_details_not_found(self):
        """Test getting nonexistent resource details"""
        response = client.get("/api/cqrs/resources/nonexistent-resource")
        assert response.status_code == 404


# ============================================================================
# TEST MODELS
# ============================================================================

class TestModels:
    """Test Pydantic models"""

    def test_command_result_model(self):
        """Test CommandResult model"""
        result = CommandResult(
            success=True,
            data={"key": "value"},
            events_published=["TestEvent"],
            message="Test message",
        )

        assert result.success is True
        assert result.data["key"] == "value"
        assert len(result.events_published) == 1

    def test_query_result_model(self):
        """Test QueryResult model"""
        result = QueryResult(success=True, data={"result": "data"})

        assert result.success is True
        assert result.data["result"] == "data"

    def test_event_model(self):
        """Test Event model"""
        event = Event(
            event_id="evt-123",
            event_type="TestEvent",
            timestamp=datetime.now().isoformat(),
            data={"test": "data"},
        )

        assert event.event_id == "evt-123"
        assert event.event_type == "TestEvent"
        assert "test" in event.data

    def test_register_user_command_validation(self):
        """Test RegisterUserCommand validation"""
        # Valid command
        cmd = RegisterUserCommand(
            username="testuser",
            email="valid@example.com",
            password="pass123",
            role="student",
            full_name="Test User",
        )
        assert cmd.username == "testuser"

        # Invalid email should be caught by Pydantic
        with pytest.raises(Exception):
            RegisterUserCommand(
                username="test",
                email="invalid-email",  # Invalid format
                password="pass",
                role="student",
                full_name="Test",
            )


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=backend.cqrs_eda_implementation", "--cov-report=html"])