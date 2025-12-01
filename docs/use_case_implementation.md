# Assignment 3 - Part 4: Use Case Implementation (CQRS+EDA)
## Smart Study Resource Recommender - Team 24

**Team Members:** Tyler Sanford, Josh England, Kendric Jones  
**Date:** November 26, 2025

---

## Overview

This document describes the implementation of 5 key use cases using **CQRS (Command Query Responsibility Segregation)** and **EDA (Event-Driven Architecture)** patterns. The code has been implemented in the GitHub repository and demonstrates separation of read/write operations with event-driven communication.

---

## CQRS+EDA Architecture Overview

### CQRS Pattern:
- **Commands**: Operations that change state (write operations)
- **Queries**: Operations that read state (read operations)
- Separate models for reading and writing
- Commands trigger events that update read models

### EDA Pattern:
- **Events**: Notifications of state changes
- **Event Bus**: Central message broker
- **Event Handlers**: Subscribers that react to events
- Async processing of side effects

---

## Implemented Use Cases

### Use Case 1: User Registration with Event Notification
**Command**: `RegisterUserCommand`  
**Event**: `UserRegisteredEvent`  
**Query**: `GetUserProfileQuery`

### Use Case 2: Resource Upload with Auto-Tagging
**Command**: `UploadResourceCommand`  
**Event**: `ResourceUploadedEvent`  
**Query**: `GetResourceDetailsQuery`

### Use Case 3: View Resource with Activity Tracking
**Command**: `LogResourceViewCommand`  
**Event**: `ResourceViewedEvent`  
**Query**: `GetResourceStatsQuery`

### Use Case 4: Rate Resource with Stats Update
**Command**: `RateResourceCommand`  
**Event**: `ResourceRatedEvent`  
**Query**: `GetResourceRatingsQuery`

### Use Case 5: Generate Personalized Recommendations
**Command**: `GenerateRecommendationsCommand`  
**Event**: `RecommendationsGeneratedEvent`  
**Query**: `GetUserRecommendationsQuery`

---

## Implementation Details

### File Structure
```
backend/
â”œâ”€â”€ main.py                          # FastAPI application (existing)
â”œâ”€â”€ cqrs_eda_implementation.py       # NEW: CQRS+EDA implementation
â”œâ”€â”€ commands/                        # NEW: Command handlers
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ user_commands.py
â”‚   â”œâ”€â”€ resource_commands.py
â”‚   â””â”€â”€ recommendation_commands.py
â”œâ”€â”€ queries/                         # NEW: Query handlers
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ user_queries.py
â”‚   â”œâ”€â”€ resource_queries.py
â”‚   â””â”€â”€ recommendation_queries.py
â”œâ”€â”€ events/                          # NEW: Event definitions
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ event_bus.py
â”‚   â””â”€â”€ event_handlers.py
â”œâ”€â”€ models/                          # NEW: Data models
â”‚   â”œâ”€â”€ __init__.py
â”‚   â””â”€â”€ data_models.py
â””â”€â”€ repositories/                    # NEW: Data access layer
    â”œâ”€â”€ __init__.py
    â”œâ”€â”€ user_repository.py
    â”œâ”€â”€ resource_repository.py
    â””â”€â”€ activity_repository.py
```

---

## Use Case 1: User Registration with Event Notification

### API Endpoint
```
POST /api/cqrs/auth/register
```

### Request Body
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "role": "student",
  "full_name": "John Doe"
}
```

### Command Flow
```
1. RegisterUserCommand received
2. Validate user data
3. Create user in users_auth table
4. Create profile in users_profile table
5. Create preferences in users_preferences table
6. Publish UserRegisteredEvent
7. Return CommandResult
```

### Event Flow
```
UserRegisteredEvent published â†’
  â”œâ”€> SendWelcomeEmailHandler (sends email)
  â”œâ”€> CreateDefaultPreferencesHandler (initializes preferences)
  â””â”€> LogAnalyticsHandler (logs user signup metric)
```

### Database Queries
```sql
-- Command side (Write)
INSERT INTO users_auth (user_id, email, password_hash, role, created_at)
VALUES (?, ?, ?, ?, ?);

INSERT INTO users_profile (profile_id, user_id, username, full_name)
VALUES (?, ?, ?, ?);

INSERT INTO users_preferences (preference_id, user_id, learning_style, difficulty_level)
VALUES (?, ?, ?, ?);

-- Query side (Read)
SELECT u.user_id, u.email, u.role, p.username, p.full_name, pr.learning_style
FROM users_auth u
LEFT JOIN users_profile p ON u.user_id = p.user_id
LEFT JOIN users_preferences pr ON u.user_id = pr.user_id
WHERE u.user_id = ?;
```

### Response
```json
{
  "success": true,
  "user_id": "user-uuid-123",
  "message": "User registered successfully",
  "events_published": ["UserRegisteredEvent"]
}
```

---

## Use Case 2: Resource Upload with Auto-Tagging

### API Endpoint
```
POST /api/cqrs/resources/upload
```

### Request Body (multipart/form-data)
```
file: [PDF/video file]
title: "Calculus Study Guide"
description: "Comprehensive notes"
resource_type: "pdf"
difficulty_level: "intermediate"
```

### Command Flow
```
1. UploadResourceCommand received
2. Validate file (type, size, virus scan)
3. Upload to storage (S3/local)
4. Extract metadata (page count, duration)
5. Insert into resources_metadata table
6. Insert into resources_content table
7. Insert into resources_stats table
8. Auto-generate tags using NLP
9. Create tag mappings
10. Publish ResourceUploadedEvent
11. Return CommandResult
```

### Event Flow
```
ResourceUploadedEvent published â†’
  â”œâ”€> GenerateTagsHandler (auto-tag content using NLP)
  â”œâ”€> NotifyFollowersHandler (notify interested users)
  â”œâ”€> UpdateRecommendationsHandler (update recommendation pool)
  â””â”€> LogUploadMetricsHandler (analytics)
```

### Database Queries
```sql
-- Command side (Write)
INSERT INTO resources_metadata (resource_id, title, description, resource_type, 
                                difficulty_level, uploader_user_id, upload_timestamp)
VALUES (?, ?, ?, ?, ?, ?, ?);

INSERT INTO resources_content (content_id, resource_id, file_path, file_url, 
                                mime_type, page_count)
VALUES (?, ?, ?, ?, ?, ?);

INSERT INTO resources_stats (stat_id, resource_id, view_count, download_count, 
                              average_rating)
VALUES (?, ?, 0, 0, 0.0);

-- Auto-generate tags
INSERT INTO tags_master (tag_id, tag_name, category) VALUES (?, ?, ?)
ON DUPLICATE KEY UPDATE usage_count = usage_count + 1;

INSERT INTO mapping_resource_tags (mapping_id, resource_id, tag_id, confidence)
VALUES (?, ?, ?, ?);

-- Query side (Read)
SELECT r.resource_id, r.title, r.description, c.file_url, s.view_count
FROM resources_metadata r
LEFT JOIN resources_content c ON r.resource_id = c.resource_id
LEFT JOIN resources_stats s ON r.resource_id = s.resource_id
WHERE r.resource_id = ?;
```

### Response
```json
{
  "success": true,
  "resource_id": "resource-uuid-456",
  "file_url": "https://cdn.../calculus-guide.pdf",
  "auto_generated_tags": ["calculus", "mathematics", "derivatives"],
  "events_published": ["ResourceUploadedEvent"]
}
```

---

## Use Case 3: View Resource with Activity Tracking

### API Endpoint
```
POST /api/cqrs/resources/{resource_id}/view
```

### Request Body
```json
{
  "user_id": "user-uuid-123",
  "view_duration_seconds": 245,
  "device_type": "desktop",
  "session_id": "session-xyz"
}
```

### Command Flow
```
1. LogResourceViewCommand received
2. Verify user exists (users_auth)
3. Verify resource exists (resources_metadata)
4. Insert view record (activities_views)
5. Update view count (resources_stats)
6. Publish ResourceViewedEvent
7. Return CommandResult
```

### Event Flow
```
ResourceViewedEvent published â†’
  â”œâ”€> UpdateResourceStatsHandler (increment view count)
  â”œâ”€> UpdateUserPreferencesHandler (learn user interests)
  â”œâ”€> TriggerRecommendationRefreshHandler (update recommendations)
  â””â”€> LogViewAnalyticsHandler (track engagement metrics)
```

### Database Queries
```sql
-- Command side (Write)
-- Verify entities exist
SELECT user_id FROM users_auth WHERE user_id = ?;
SELECT resource_id FROM resources_metadata WHERE resource_id = ?;

-- Log view event
INSERT INTO activities_views (view_id, user_id, resource_id, view_timestamp, 
                               view_duration_seconds, device_type, session_id)
VALUES (?, ?, ?, ?, ?, ?, ?);

-- Update stats (separate transaction)
UPDATE resources_stats
SET view_count = view_count + 1,
    last_accessed = CURRENT_TIMESTAMP
WHERE resource_id = ?;

-- Query side (Read)
SELECT view_count, download_count, average_rating, last_accessed
FROM resources_stats
WHERE resource_id = ?;
```

### Response
```json
{
  "success": true,
  "view_id": "view-uuid-001",
  "resource_id": "resource-uuid-456",
  "new_view_count": 126,
  "events_published": ["ResourceViewedEvent"]
}
```

---

## Use Case 4: Rate Resource with Stats Update

### API Endpoint
```
POST /api/cqrs/resources/{resource_id}/rate
```

### Request Body
```json
{
  "user_id": "user-uuid-123",
  "rating_value": 5,
  "review_text": "Excellent study guide!"
}
```

### Command Flow
```
1. RateResourceCommand received
2. Verify user exists (users_auth)
3. Verify resource exists (resources_metadata)
4. Check for existing rating
5. Insert or update rating (activities_ratings)
6. Recalculate average rating
7. Update resource stats (resources_stats)
8. Publish ResourceRatedEvent
9. Return CommandResult
```

### Event Flow
```
ResourceRatedEvent published â†’
  â”œâ”€> UpdateResourceStatsHandler (recalculate avg rating)
  â”œâ”€> NotifyResourceOwnerHandler (notify uploader of new rating)
  â”œâ”€> UpdateRecommendationScoresHandler (adjust recommendation weights)
  â””â”€> LogRatingAnalyticsHandler (track rating patterns)
```

### Database Queries
```sql
-- Command side (Write)
-- Verify entities
SELECT user_id FROM users_auth WHERE user_id = ?;
SELECT resource_id FROM resources_metadata WHERE resource_id = ?;

-- Check existing rating
SELECT rating_id FROM activities_ratings 
WHERE user_id = ? AND resource_id = ?;

-- Insert or update rating
INSERT INTO activities_ratings (rating_id, user_id, resource_id, rating_value, 
                                review_text, rated_at)
VALUES (?, ?, ?, ?, ?, ?)
ON DUPLICATE KEY UPDATE 
    rating_value = VALUES(rating_value),
    review_text = VALUES(review_text),
    updated_at = CURRENT_TIMESTAMP;

-- Recalculate average
SELECT AVG(rating_value) as avg_rating, COUNT(*) as rating_count
FROM activities_ratings
WHERE resource_id = ?;

-- Update stats
UPDATE resources_stats
SET average_rating = ?,
    rating_count = ?
WHERE resource_id = ?;

-- Query side (Read)
SELECT r.rating_id, r.rating_value, r.review_text, r.rated_at,
       p.username
FROM activities_ratings r
LEFT JOIN users_profile p ON r.user_id = p.user_id
WHERE r.resource_id = ?
ORDER BY r.rated_at DESC;
```

### Response
```json
{
  "success": true,
  "rating_id": "rating-uuid-003",
  "resource_id": "resource-uuid-456",
  "updated_stats": {
    "average_rating": 4.6,
    "rating_count": 19
  },
  "events_published": ["ResourceRatedEvent"]
}
```

---

## Use Case 5: Generate Personalized Recommendations

### API Endpoint
```
POST /api/cqrs/recommendations/generate
```

### Request Body
```json
{
  "user_id": "user-uuid-123",
  "limit": 10,
  "algorithm": "hybrid"
}
```

### Command Flow
```
1. GenerateRecommendationsCommand received
2. Fetch user preferences (users_preferences)
3. Fetch user interests (mapping_user_interests)
4. Fetch user activity history (activities_views, activities_ratings)
5. Fetch candidate resources (resources_metadata)
6. Calculate recommendation scores (algorithm)
7. Rank and filter results
8. Insert recommendations (recommendations_generated)
9. Publish RecommendationsGeneratedEvent
10. Return CommandResult
```

### Event Flow
```
RecommendationsGeneratedEvent published â†’
  â”œâ”€> CacheRecommendationsHandler (cache for fast retrieval)
  â”œâ”€> NotifyUserHandler (send notification of new recommendations)
  â”œâ”€> LogRecommendationMetricsHandler (track algorithm performance)
  â””â”€> UpdateMLModelHandler (feedback to ML system)
```

### Database Queries
```sql
-- Command side (Write)
-- Fetch user data
SELECT learning_style, preferred_subjects, difficulty_level
FROM users_preferences
WHERE user_id = ?;

-- Fetch user interests
SELECT tag_id, interest_level
FROM mapping_user_interests
WHERE user_id = ?;

-- Fetch viewed resources (to exclude)
SELECT DISTINCT resource_id
FROM activities_views
WHERE user_id = ?
ORDER BY view_timestamp DESC
LIMIT 50;

-- Fetch highly rated resources (to find similar)
SELECT resource_id, rating_value
FROM activities_ratings
WHERE user_id = ? AND rating_value >= 4;

-- Find candidate resources
SELECT m.resource_id, m.title, m.difficulty_level, s.view_count, s.average_rating
FROM resources_metadata m
JOIN resources_stats s ON m.resource_id = s.resource_id
WHERE m.difficulty_level = ?
  AND m.resource_id NOT IN (?)
ORDER BY s.view_count DESC, s.average_rating DESC
LIMIT 50;

-- Get tags for each resource
SELECT resource_id, tag_id
FROM mapping_resource_tags
WHERE resource_id IN (?);

-- Insert recommendations
INSERT INTO recommendations_generated 
    (recommendation_id, user_id, resource_id, algorithm_used, 
     confidence_score, reason, generated_at, position)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);

-- Query side (Read)
SELECT r.recommendation_id, r.resource_id, r.confidence_score, r.reason,
       m.title, m.description, s.view_count, s.average_rating
FROM recommendations_generated r
JOIN resources_metadata m ON r.resource_id = m.resource_id
JOIN resources_stats s ON r.resource_id = s.resource_id
WHERE r.user_id = ?
ORDER BY r.position ASC;
```

### Response
```json
{
  "success": true,
  "user_id": "user-uuid-123",
  "recommendations_count": 10,
  "algorithm_used": "hybrid",
  "recommendations": [
    {
      "recommendation_id": "rec-uuid-001",
      "resource_id": "resource-uuid-500",
      "title": "Advanced Calculus Problems",
      "confidence_score": 0.87,
      "reason": "Based on your interest in calculus and high ratings on similar resources"
    }
  ],
  "events_published": ["RecommendationsGeneratedEvent"]
}
```

---

## CQRS+EDA Benefits Demonstrated

### 1. Separation of Concerns
- **Commands** handle writes with validation and business logic
- **Queries** handle reads optimized for specific views
- Clear boundaries between read and write models

### 2. Event-Driven Scalability
- **Events** enable async processing of side effects
- Stats updates don't block main operation
- Notifications sent asynchronously
- Analytics logged without impacting response time

### 3. Flexibility
- Can add new event handlers without modifying commands
- Easy to add features like email notifications, ML updates
- Different storage strategies for read/write models

### 4. Performance
- Read queries optimized separately from writes
- Can cache read models aggressively
- Event handlers process in background
- No transaction overhead for analytics

### 5. Audit Trail
- Every command generates events
- Complete history of state changes
- Can replay events to rebuild read models
- Useful for debugging and compliance

---

## CQRS+EDA Implementation Pattern

### Command Handler Pattern
```python
class CommandHandler:
    def __init__(self, repository, event_bus):
        self.repository = repository
        self.event_bus = event_bus
    
    async def handle(self, command):
        # 1. Validate command
        self.validate(command)
        
        # 2. Execute business logic
        result = await self.repository.execute(command)
        
        # 3. Publish event
        event = self.create_event(result)
        await self.event_bus.publish(event)
        
        # 4. Return result
        return CommandResult(success=True, data=result)
```

### Query Handler Pattern
```python
class QueryHandler:
    def __init__(self, read_repository):
        self.read_repository = read_repository
    
    async def handle(self, query):
        # 1. Fetch from read model
        data = await self.read_repository.get(query)
        
        # 2. Format response
        return QueryResult(success=True, data=data)
```

### Event Handler Pattern
```python
class EventHandler:
    def __init__(self, repository):
        self.repository = repository
    
    async def handle(self, event):
        # 1. Process event
        await self.process_event(event)
        
        # 2. Update read models
        await self.update_read_model(event)
        
        # 3. Trigger side effects
        await self.execute_side_effects(event)
```

---

## Reflection on CQRS+EDA Usage

### What Worked Well:

**Separation of Read/Write Models:**
The CQRS pattern helped us optimize queries for specific views without affecting write operations. For example, the recommendation query fetches from multiple tables but doesn't need to worry about transaction consistency.

**Event-Driven Side Effects:**
EDA pattern enabled us to process analytics, notifications, and stats updates asynchronously. When a user views a resource, the view is logged immediately, but stats are updated in the background without blocking the response.

**Scalability:**
By separating commands and queries, we can scale read replicas independently from write instances. High-traffic endpoints like "get recommendations" can be cached aggressively.

**Flexibility:**
Adding new features is easy - just add new event handlers. For example, adding email notifications required no changes to the upload command, just a new event handler.

### Challenges:

**Eventual Consistency:**
Read models may be slightly out of sync with write models. For example, after rating a resource, the updated average rating might not appear immediately. We handled this by returning the updated stats in the command response.

**Complexity:**
CQRS+EDA adds architectural complexity compared to simple CRUD. We need to manage event bus, multiple handlers, and ensure idempotency of event processing.

**Testing:**
Testing event-driven systems requires mocking the event bus and verifying event handlers are called correctly. Integration tests are more complex.

### When to Use CQRS+EDA:

**Good fit:**
- High read/write traffic imbalance (many reads, few writes)
- Complex business logic with multiple side effects
- Need for audit trails and event sourcing
- Microservices architecture

**Not a good fit:**
- Simple CRUD applications
- Tight consistency requirements
- Small applications with limited scalability needs
- Teams unfamiliar with event-driven patterns

---

## GitHub Repository

**Repository URL:** https://github.com/[your-username]/smart-study-recommender  
**Branch:** `assignment-3-cqrs-eda`

### Implemented Files:
- `backend/cqrs_eda_implementation.py` - Main CQRS+EDA implementation
- `backend/commands/*` - Command handlers for all 5 use cases
- `backend/queries/*` - Query handlers for read operations
- `backend/events/*` - Event bus and event handlers
- `backend/models/*` - Data models and DTOs
- `backend/repositories/*` - Data access layer (low-cohesion DB)

### Commit Messages:
1. `feat: Add CQRS+EDA architecture foundation`
2. `feat: Implement Use Case 1 - User Registration with events`
3. `feat: Implement Use Case 2 - Resource Upload with auto-tagging`
4. `feat: Implement Use Case 3 - View Resource with activity tracking`
5. `feat: Implement Use Case 4 - Rate Resource with stats update`
6. `feat: Implement Use Case 5 - Generate Personalized Recommendations`
7. `docs: Add CQRS+EDA implementation documentation`

---

## Testing the Implementation

### Run Backend Server:
```bash
cd backend
python cqrs_eda_implementation.py
```

### Test Endpoints:
```bash
# Use Case 1: Register User
curl -X POST http://localhost:8000/api/cqrs/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"pass123","role":"student"}'

# Use Case 2: Upload Resource
curl -X POST http://localhost:8000/api/cqrs/resources/upload \
  -F "file=@calculus-guide.pdf" \
  -F "title=Calculus Guide" \
  -F "resource_type=pdf"

# Use Case 3: View Resource
curl -X POST http://localhost:8000/api/cqrs/resources/{resource_id}/view \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user-123","view_duration_seconds":120}'

# Use Case 4: Rate Resource
curl -X POST http://localhost:8000/api/cqrs/resources/{resource_id}/rate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user-123","rating_value":5,"review_text":"Great!"}'

# Use Case 5: Generate Recommendations
curl -X POST http://localhost:8000/api/cqrs/recommendations/generate \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user-123","limit":10}'
```

---

## End of Part 4: Use Case Implementation