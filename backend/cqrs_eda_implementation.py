"""
CQRS+EDA Implementation for Smart Study Resource Recommender
Assignment 3 - Part 4
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel, EmailStr
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import uuid
import asyncio
from collections import defaultdict

# ============================================================================
# MODELS AND DATA STRUCTURES
# ============================================================================

class CommandResult(BaseModel):
    """Result of executing a command"""
    success: bool
    data: Dict[str, Any]
    events_published: List[str] = []
    message: str = ""

class QueryResult(BaseModel):
    """Result of executing a query"""
    success: bool
    data: Dict[str, Any]

class Event(BaseModel):
    """Base event class"""
    event_id: str
    event_type: str
    timestamp: str
    data: Dict[str, Any]

# ============================================================================
# EVENT BUS (Simple in-memory implementation)
# ============================================================================

class EventBus:
    """Simple event bus for pub/sub pattern"""
    
    def __init__(self):
        self.subscribers: Dict[str, List] = defaultdict(list)
        self.event_log: List[Event] = []
    
    def subscribe(self, event_type: str, handler):
        """Subscribe a handler to an event type"""
        self.subscribers[event_type].append(handler)
        print(f"✓ Subscribed {handler.__name__} to {event_type}")
    
    async def publish(self, event: Event):
        """Publish an event to all subscribers"""
        self.event_log.append(event)
        print(f" Published event: {event.event_type}")
        
        # Call all handlers for this event type
        handlers = self.subscribers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                print(f" Error in handler {handler.__name__}: {str(e)}")

# Global event bus instance
event_bus = EventBus()

# ============================================================================
# IN-MEMORY DATABASES (Low-Cohesion Design)
# ============================================================================

# User domain tables
users_auth_db: Dict[str, dict] = {}
users_profile_db: Dict[str, dict] = {}
users_preferences_db: Dict[str, dict] = {}

# Resource domain tables
resources_metadata_db: Dict[str, dict] = {}
resources_content_db: Dict[str, dict] = {}
resources_stats_db: Dict[str, dict] = {}

# Activity domain tables
activities_views_db: Dict[str, dict] = {}
activities_downloads_db: Dict[str, dict] = {}
activities_ratings_db: Dict[str, dict] = {}

# Recommendation domain tables
recommendations_generated_db: Dict[str, dict] = {}

# Tag domain tables
tags_master_db: Dict[str, dict] = {}
mapping_resource_tags_db: Dict[str, dict] = {}
mapping_user_interests_db: Dict[str, dict] = {}

# ============================================================================
# REPOSITORIES (Data Access Layer)
# ============================================================================

class UserRepository:
    """Repository for user data operations"""
    
    @staticmethod
    async def create_user_auth(user_id: str, email: str, password: str, role: str):
        """Create user authentication record"""
        users_auth_db[user_id] = {
            "user_id": user_id,
            "email": email,
            "password_hash": password,  # In production: bcrypt hash
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat()
        }
        return users_auth_db[user_id]
    
    @staticmethod
    async def create_user_profile(user_id: str, username: str, full_name: str):
        """Create user profile record"""
        profile_id = str(uuid.uuid4())
        users_profile_db[profile_id] = {
            "profile_id": profile_id,
            "user_id": user_id,
            "username": username,
            "full_name": full_name,
            "bio": "",
            "avatar_url": "",
            "updated_at": datetime.now().isoformat()
        }
        return users_profile_db[profile_id]
    
    @staticmethod
    async def create_user_preferences(user_id: str):
        """Create default user preferences"""
        pref_id = str(uuid.uuid4())
        users_preferences_db[pref_id] = {
            "preference_id": pref_id,
            "user_id": user_id,
            "learning_style": "visual",
            "preferred_subjects": [],
            "difficulty_level": "beginner",
            "study_time_preference": "evening",
            "created_at": datetime.now().isoformat()
        }
        return users_preferences_db[pref_id]
    
    @staticmethod
    async def user_exists(user_id: str) -> bool:
        """Check if user exists"""
        return user_id in users_auth_db
    
    @staticmethod
    async def email_exists(email: str) -> bool:
        """Check if email already registered"""
        return any(u["email"] == email for u in users_auth_db.values())

class ResourceRepository:
    """Repository for resource data operations"""
    
    @staticmethod
    async def create_resource_metadata(resource_id: str, title: str, description: str,
                                      resource_type: str, difficulty: str, uploader_id: str):
        """Create resource metadata record"""
        resources_metadata_db[resource_id] = {
            "resource_id": resource_id,
            "title": title,
            "description": description,
            "resource_type": resource_type,
            "difficulty_level": difficulty,
            "file_size_mb": 2.5,  # Mock value
            "upload_timestamp": datetime.now().isoformat(),
            "uploader_user_id": uploader_id
        }
        return resources_metadata_db[resource_id]
    
    @staticmethod
    async def create_resource_content(resource_id: str, file_path: str, file_url: str):
        """Create resource content record"""
        content_id = str(uuid.uuid4())
        resources_content_db[content_id] = {
            "content_id": content_id,
            "resource_id": resource_id,
            "file_path": file_path,
            "file_url": file_url,
            "mime_type": "application/pdf",
            "page_count": 45,  # Mock value
            "storage_location": "local"
        }
        return resources_content_db[content_id]
    
    @staticmethod
    async def create_resource_stats(resource_id: str):
        """Initialize resource statistics"""
        stat_id = str(uuid.uuid4())
        resources_stats_db[stat_id] = {
            "stat_id": stat_id,
            "resource_id": resource_id,
            "view_count": 0,
            "download_count": 0,
            "favorite_count": 0,
            "average_rating": 0.0,
            "rating_count": 0,
            "last_accessed": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return resources_stats_db[stat_id]
    
    @staticmethod
    async def resource_exists(resource_id: str) -> bool:
        """Check if resource exists"""
        return resource_id in resources_metadata_db
    
    @staticmethod
    async def get_resource_stats(resource_id: str) -> Optional[dict]:
        """Get resource statistics"""
        for stats in resources_stats_db.values():
            if stats["resource_id"] == resource_id:
                return stats
        return None
    
    @staticmethod
    async def update_view_count(resource_id: str):
        """Increment view count"""
        for stats in resources_stats_db.values():
            if stats["resource_id"] == resource_id:
                stats["view_count"] += 1
                stats["last_accessed"] = datetime.now().isoformat()
                stats["updated_at"] = datetime.now().isoformat()
                return stats

class ActivityRepository:
    """Repository for activity tracking"""
    
    @staticmethod
    async def log_view(user_id: str, resource_id: str, duration: int, device: str, session: str):
        """Log a view event"""
        view_id = str(uuid.uuid4())
        activities_views_db[view_id] = {
            "view_id": view_id,
            "user_id": user_id,
            "resource_id": resource_id,
            "view_timestamp": datetime.now().isoformat(),
            "view_duration_seconds": duration,
            "device_type": device,
            "session_id": session
        }
        return activities_views_db[view_id]
    
    @staticmethod
    async def log_rating(user_id: str, resource_id: str, rating: int, review: str):
        """Log a rating"""
        rating_id = str(uuid.uuid4())
        activities_ratings_db[rating_id] = {
            "rating_id": rating_id,
            "user_id": user_id,
            "resource_id": resource_id,
            "rating_value": rating,
            "review_text": review,
            "rated_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return activities_ratings_db[rating_id]
    
    @staticmethod
    async def get_ratings_for_resource(resource_id: str) -> List[dict]:
        """Get all ratings for a resource"""
        return [r for r in activities_ratings_db.values() if r["resource_id"] == resource_id]
    
    @staticmethod
    async def calculate_average_rating(resource_id: str) -> tuple:
        """Calculate average rating and count"""
        ratings = await ActivityRepository.get_ratings_for_resource(resource_id)
        if not ratings:
            return 0.0, 0
        
        total = sum(r["rating_value"] for r in ratings)
        count = len(ratings)
        average = round(total / count, 2)
        return average, count

# ============================================================================
# EVENT HANDLERS
# ============================================================================

async def handle_user_registered(event: Event):
    """Handle UserRegisteredEvent"""
    print(f"  → Sending welcome email to {event.data['email']}")
    print(f"  → Creating default preferences for user {event.data['user_id']}")
    print(f"  → Logging user registration analytics")

async def handle_resource_uploaded(event: Event):
    """Handle ResourceUploadedEvent"""
    print(f"  → Auto-generating tags for resource {event.data['resource_id']}")
    print(f"  → Notifying followers about new resource")
    print(f"  → Updating recommendation pool")

async def handle_resource_viewed(event: Event):
    """Handle ResourceViewedEvent"""
    print(f"  → Updating user preferences based on view")
    print(f"  → Triggering recommendation refresh")
    print(f"  → Logging engagement metrics")

async def handle_resource_rated(event: Event):
    """Handle ResourceRatedEvent"""
    print(f"  → Notifying resource owner of new rating")
    print(f"  → Updating recommendation scores")
    print(f"  → Logging rating analytics")

async def handle_recommendations_generated(event: Event):
    """Handle RecommendationsGeneratedEvent"""
    print(f"  → Caching recommendations for user {event.data['user_id']}")
    print(f"  → Sending notification to user")
    print(f"  → Logging recommendation metrics")

# Subscribe event handlers
event_bus.subscribe("UserRegisteredEvent", handle_user_registered)
event_bus.subscribe("ResourceUploadedEvent", handle_resource_uploaded)
event_bus.subscribe("ResourceViewedEvent", handle_resource_viewed)
event_bus.subscribe("ResourceRatedEvent", handle_resource_rated)
event_bus.subscribe("RecommendationsGeneratedEvent", handle_recommendations_generated)

# ============================================================================
# COMMAND HANDLERS
# ============================================================================

class RegisterUserCommand(BaseModel):
    """Command to register a new user"""
    username: str
    email: EmailStr
    password: str
    role: str = "student"
    full_name: str

class RegisterUserCommandHandler:
    """Handler for user registration command"""
    
    @staticmethod
    async def handle(command: RegisterUserCommand) -> CommandResult:
        print(f"\n Executing RegisterUserCommand for {command.email}")
        
        # 1. Validate
        if await UserRepository.email_exists(command.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # 2. Generate user_id
        user_id = str(uuid.uuid4())
        
        # 3. Create user records (low-cohesion: 3 separate tables)
        await UserRepository.create_user_auth(user_id, command.email, command.password, command.role)
        await UserRepository.create_user_profile(user_id, command.username, command.full_name)
        await UserRepository.create_user_preferences(user_id)
        
        # 4. Publish event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="UserRegisteredEvent",
            timestamp=datetime.now().isoformat(),
            data={
                "user_id": user_id,
                "email": command.email,
                "username": command.username,
                "role": command.role
            }
        )
        await event_bus.publish(event)
        
        # 5. Return result
        return CommandResult(
            success=True,
            data={"user_id": user_id, "email": command.email, "username": command.username},
            events_published=["UserRegisteredEvent"],
            message="User registered successfully"
        )

class UploadResourceCommand(BaseModel):
    """Command to upload a resource"""
    title: str
    description: str
    resource_type: str
    difficulty_level: str
    uploader_user_id: str
    file_name: str

class UploadResourceCommandHandler:
    """Handler for resource upload command"""
    
    @staticmethod
    async def handle(command: UploadResourceCommand) -> CommandResult:
        print(f"\n📝 Executing UploadResourceCommand: {command.title}")
        
        # 1. Validate user exists
        if not await UserRepository.user_exists(command.uploader_user_id):
            raise HTTPException(status_code=404, detail="User not found")
        
        # 2. Generate resource_id
        resource_id = str(uuid.uuid4())
        
        # 3. Create resource records (low-cohesion: 3 separate tables)
        await ResourceRepository.create_resource_metadata(
            resource_id, command.title, command.description,
            command.resource_type, command.difficulty_level, command.uploader_user_id
        )
        
        file_url = f"https://cdn.example.com/{command.file_name}"
        await ResourceRepository.create_resource_content(resource_id, f"/uploads/{command.file_name}", file_url)
        await ResourceRepository.create_resource_stats(resource_id)
        
        # 4. Auto-generate tags (simplified)
        auto_tags = ["mathematics", "study-guide", "beginner"]
        print(f"  → Auto-generated tags: {auto_tags}")
        
        # 5. Publish event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="ResourceUploadedEvent",
            timestamp=datetime.now().isoformat(),
            data={
                "resource_id": resource_id,
                "title": command.title,
                "uploader_user_id": command.uploader_user_id,
                "auto_tags": auto_tags
            }
        )
        await event_bus.publish(event)
        
        # 6. Return result
        return CommandResult(
            success=True,
            data={
                "resource_id": resource_id,
                "title": command.title,
                "file_url": file_url,
                "auto_generated_tags": auto_tags
            },
            events_published=["ResourceUploadedEvent"],
            message="Resource uploaded successfully"
        )

class LogResourceViewCommand(BaseModel):
    """Command to log a resource view"""
    user_id: str
    resource_id: str
    view_duration_seconds: int
    device_type: str = "desktop"
    session_id: str

class LogResourceViewCommandHandler:
    """Handler for logging resource views"""
    
    @staticmethod
    async def handle(command: LogResourceViewCommand) -> CommandResult:
        print(f"\n📝 Executing LogResourceViewCommand for resource {command.resource_id}")
        
        # 1. Validate entities exist
        if not await UserRepository.user_exists(command.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        
        if not await ResourceRepository.resource_exists(command.resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # 2. Log view event
        view_record = await ActivityRepository.log_view(
            command.user_id, command.resource_id,
            command.view_duration_seconds, command.device_type, command.session_id
        )
        
        # 3. Update stats (separate table, NO JOIN)
        updated_stats = await ResourceRepository.update_view_count(command.resource_id)
        
        # 4. Publish event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="ResourceViewedEvent",
            timestamp=datetime.now().isoformat(),
            data={
                "view_id": view_record["view_id"],
                "user_id": command.user_id,
                "resource_id": command.resource_id,
                "new_view_count": updated_stats["view_count"] if updated_stats else 1
            }
        )
        await event_bus.publish(event)
        
        # 5. Return result
        return CommandResult(
            success=True,
            data={
                "view_id": view_record["view_id"],
                "resource_id": command.resource_id,
                "new_view_count": updated_stats["view_count"] if updated_stats else 1
            },
            events_published=["ResourceViewedEvent"],
            message="View logged successfully"
        )

class RateResourceCommand(BaseModel):
    """Command to rate a resource"""
    user_id: str
    resource_id: str
    rating_value: int
    review_text: str = ""

class RateResourceCommandHandler:
    """Handler for rating resources"""
    
    @staticmethod
    async def handle(command: RateResourceCommand) -> CommandResult:
        print(f"\n Executing RateResourceCommand: {command.rating_value} stars")
        
        # 1. Validate
        if not 1 <= command.rating_value <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        if not await UserRepository.user_exists(command.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        
        if not await ResourceRepository.resource_exists(command.resource_id):
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # 2. Log rating
        rating_record = await ActivityRepository.log_rating(
            command.user_id, command.resource_id, command.rating_value, command.review_text
        )
        
        # 3. Recalculate average rating
        avg_rating, rating_count = await ActivityRepository.calculate_average_rating(command.resource_id)
        
        # 4. Update resource stats (separate table)
        stats = await ResourceRepository.get_resource_stats(command.resource_id)
        if stats:
            stats["average_rating"] = avg_rating
            stats["rating_count"] = rating_count
            stats["updated_at"] = datetime.now().isoformat()
        
        # 5. Publish event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="ResourceRatedEvent",
            timestamp=datetime.now().isoformat(),
            data={
                "rating_id": rating_record["rating_id"],
                "user_id": command.user_id,
                "resource_id": command.resource_id,
                "rating_value": command.rating_value,
                "new_average": avg_rating,
                "rating_count": rating_count
            }
        )
        await event_bus.publish(event)
        
        # 6. Return result
        return CommandResult(
            success=True,
            data={
                "rating_id": rating_record["rating_id"],
                "resource_id": command.resource_id,
                "updated_stats": {
                    "average_rating": avg_rating,
                    "rating_count": rating_count
                }
            },
            events_published=["ResourceRatedEvent"],
            message="Rating submitted successfully"
        )

class GenerateRecommendationsCommand(BaseModel):
    """Command to generate recommendations"""
    user_id: str
    limit: int = 10
    algorithm: str = "hybrid"

class GenerateRecommendationsCommandHandler:
    """Handler for generating recommendations"""
    
    @staticmethod
    async def handle(command: GenerateRecommendationsCommand) -> CommandResult:
        print(f"\n Executing GenerateRecommendationsCommand for user {command.user_id}")
        
        # 1. Validate user exists
        if not await UserRepository.user_exists(command.user_id):
            raise HTTPException(status_code=404, detail="User not found")
        
        # 2. Fetch user preferences (simplified)
        print(f"  → Fetching user preferences...")
        print(f"  → Fetching user activity history...")
        
        # 3. Generate recommendations (simplified algorithm)
        recommendations = []
        for resource_id, resource in list(resources_metadata_db.items())[:command.limit]:
            rec_id = str(uuid.uuid4())
            confidence_score = 0.85  # Mock score
            
            recommendations.append({
                "recommendation_id": rec_id,
                "resource_id": resource_id,
                "title": resource["title"],
                "confidence_score": confidence_score,
                "reason": f"Based on your interest in {resource['resource_type']}"
            })
            
            # Store recommendation
            recommendations_generated_db[rec_id] = {
                "recommendation_id": rec_id,
                "user_id": command.user_id,
                "resource_id": resource_id,
                "algorithm_used": command.algorithm,
                "confidence_score": confidence_score,
                "reason": f"Based on your interest in {resource['resource_type']}",
                "generated_at": datetime.now().isoformat(),
                "position": len(recommendations)
            }
        
        # 4. Publish event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="RecommendationsGeneratedEvent",
            timestamp=datetime.now().isoformat(),
            data={
                "user_id": command.user_id,
                "recommendations_count": len(recommendations),
                "algorithm_used": command.algorithm
            }
        )
        await event_bus.publish(event)
        
        # 5. Return result
        return CommandResult(
            success=True,
            data={
                "user_id": command.user_id,
                "recommendations_count": len(recommendations),
                "algorithm_used": command.algorithm,
                "recommendations": recommendations
            },
            events_published=["RecommendationsGeneratedEvent"],
            message="Recommendations generated successfully"
        )

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Smart Study Recommender - CQRS+EDA",
    description="Assignment 3 Part 4 - Use Case Implementation",
    version="1.0.0"
)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    return {
        "message": "CQRS+EDA Implementation - Assignment 3 Part 4",
        "team": "Team 24",
        "use_cases_implemented": 5,
        "endpoints": [
            "POST /api/cqrs/auth/register",
            "POST /api/cqrs/resources/upload",
            "POST /api/cqrs/resources/{resource_id}/view",
            "POST /api/cqrs/resources/{resource_id}/rate",
            "POST /api/cqrs/recommendations/generate"
        ]
    }

# Use Case 1: User Registration
@app.post("/api/cqrs/auth/register", response_model=CommandResult, status_code=status.HTTP_201_CREATED)
async def register_user(command: RegisterUserCommand):
    """
    Use Case 1: Register a new user with event-driven notifications
    
    CQRS: Command creates user records across 3 tables
    EDA: Publishes UserRegisteredEvent for async processing
    """
    return await RegisterUserCommandHandler.handle(command)

# Use Case 2: Resource Upload
@app.post("/api/cqrs/resources/upload", response_model=CommandResult, status_code=status.HTTP_201_CREATED)
async def upload_resource(
    title: str = Form(...),
    description: str = Form(...),
    resource_type: str = Form(...),
    difficulty_level: str = Form(...),
    uploader_user_id: str = Form(...),
    file_name: str = Form(...)
):
    """
    Use Case 2: Upload resource with auto-tagging
    
    CQRS: Command creates resource records across 3 tables
    EDA: Publishes ResourceUploadedEvent for tag generation and notifications
    """
    command = UploadResourceCommand(
        title=title,
        description=description,
        resource_type=resource_type,
        difficulty_level=difficulty_level,
        uploader_user_id=uploader_user_id,
        file_name=file_name
    )
    return await UploadResourceCommandHandler.handle(command)

# Use Case 3: View Resource
@app.post("/api/cqrs/resources/{resource_id}/view", response_model=CommandResult)
async def view_resource(resource_id: str, command: LogResourceViewCommand):
    """
    Use Case 3: Log resource view with activity tracking
    
    CQRS: Command logs view and updates stats separately
    EDA: Publishes ResourceViewedEvent for analytics and preference updates
    """
    command.resource_id = resource_id
    return await LogResourceViewCommandHandler.handle(command)

# Use Case 4: Rate Resource
@app.post("/api/cqrs/resources/{resource_id}/rate", response_model=CommandResult)
async def rate_resource(resource_id: str, command: RateResourceCommand):
    """
    Use Case 4: Rate a resource and update statistics
    
    CQRS: Command logs rating and recalculates stats
    EDA: Publishes ResourceRatedEvent for owner notifications and recommendation updates
    """
    command.resource_id = resource_id
    return await RateResourceCommandHandler.handle(command)

# Use Case 5: Generate Recommendations
@app.post("/api/cqrs/recommendations/generate", response_model=CommandResult)
async def generate_recommendations(command: GenerateRecommendationsCommand):
    """
    Use Case 5: Generate personalized recommendations
    
    CQRS: Command executes recommendation algorithm and stores results
    EDA: Publishes RecommendationsGeneratedEvent for caching and notifications
    """
    return await GenerateRecommendationsCommandHandler.handle(command)

# ============================================================================
# QUERY ENDPOINTS (Read side)
# ============================================================================

@app.get("/api/cqrs/users/{user_id}")
async def get_user_profile(user_id: str):
    """Query: Get user profile (read model)"""
    if not await UserRepository.user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    
    # Assemble from multiple tables (NO JOIN)
    auth = users_auth_db.get(user_id)
    profile = next((p for p in users_profile_db.values() if p["user_id"] == user_id), None)
    prefs = next((p for p in users_preferences_db.values() if p["user_id"] == user_id), None)
    
    return QueryResult(
        success=True,
        data={
            "user_id": user_id,
            "email": auth["email"] if auth else None,
            "username": profile["username"] if profile else None,
            "learning_style": prefs["learning_style"] if prefs else None
        }
    )

@app.get("/api/cqrs/resources/{resource_id}")
async def get_resource_details(resource_id: str):
    """Query: Get resource details (read model)"""
    if not await ResourceRepository.resource_exists(resource_id):
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Assemble from multiple tables (NO JOIN)
    metadata = resources_metadata_db.get(resource_id)
    content = next((c for c in resources_content_db.values() if c["resource_id"] == resource_id), None)
    stats = await ResourceRepository.get_resource_stats(resource_id)
    
    return QueryResult(
        success=True,
        data={
            "resource_id": resource_id,
            "title": metadata["title"] if metadata else None,
            "file_url": content["file_url"] if content else None,
            "view_count": stats["view_count"] if stats else 0,
            "average_rating": stats["average_rating"] if stats else 0.0
        }
    )

@app.get("/api/cqrs/events")
async def get_event_log():
    """Query: Get all published events (for debugging)"""
    return {
        "total_events": len(event_bus.event_log),
        "events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "timestamp": e.timestamp,
                "data": e.data
            }
            for e in event_bus.event_log[-20:]  # Last 20 events
        ]
    }

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print(" Starting CQRS+EDA Implementation - Assignment 3 Part 4")
    print("="*70)
    print("\n📋 Implemented Use Cases:")
    print("  1. User Registration with Event Notification")
    print("  2. Resource Upload with Auto-Tagging")
    print("  3. View Resource with Activity Tracking")
    print("  4. Rate Resource with Stats Update")
    print("  5. Generate Personalized Recommendations")
    print("\n Event Handlers Subscribed:")
    print("  - UserRegisteredEvent")
    print("  - ResourceUploadedEvent")
    print("  - ResourceViewedEvent")
    print("  - ResourceRatedEvent")
    print("  - RecommendationsGeneratedEvent")
    print("\n" + "="*70)
    print(" Server starting on http://localhost:8000")
    print(" API Docs: http://localhost:8000/docs")
    print("="*70 + "\n")
    
    uvicorn.run(
        "cqrs_eda_implementation:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )