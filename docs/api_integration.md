# Assignment 3 - Part 3: API Integration
## Smart Study Resource Recommender - Team 24

**Team Members:** Tyler Sanford, Josh England, Kendric Jones  
**Date:** November 26, 2025

---

## 1. API Integration Overview

This section designs RESTful APIs that interact with the low-cohesion database (from Part 2) while performing necessary validations and cross-table checks at the **Application Layer**. Since our database lacks foreign key constraints, the API layer is responsible for:

1. **Verifying entity existence** in base tables
2. **Validating ownership and relationships** through mapping tables
3. **Retrieving dependent information** from related tables
4. **Assembling the final output** in the API layer

---

## 2. Core API Endpoints for MVP

### 2.1 Authentication Endpoints

#### **POST /api/auth/register**
**Purpose:** Register a new user account  
**REST Method:** POST  
**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "securepass123",
  "username": "johndoe",
  "role": "student",
  "full_name": "John Doe"
}
```

**Relevant DB Tables:** `users_auth`, `users_profile`, `users_preferences`

**Database Query Steps:**
```sql
-- Step 1: Check if email already exists (validate uniqueness)
SELECT user_id FROM users_auth WHERE email = 'student@example.com';
-- If exists â†’ Return 400 Bad Request: "Email already registered"

-- Step 2: Hash password (application layer using bcrypt)
-- hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

-- Step 3: Generate unique user_id (UUID)
-- user_id = uuid.uuid4()

-- Step 4: Insert into users_auth table
INSERT INTO users_auth (user_id, email, password_hash, role, created_at, last_login)
VALUES ('user-uuid-123', 'student@example.com', '$2b$12$...', 'student', 
        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- Step 5: Insert into users_profile table (separate table, NO FK constraint)
INSERT INTO users_profile (profile_id, user_id, username, full_name, updated_at)
VALUES ('profile-uuid-456', 'user-uuid-123', 'johndoe', 'John Doe', CURRENT_TIMESTAMP);

-- Step 6: Insert default preferences (separate table, NO FK constraint)
INSERT INTO users_preferences (preference_id, user_id, learning_style, 
                                preferred_subjects, difficulty_level, created_at)
VALUES ('pref-uuid-789', 'user-uuid-123', 'visual', '[]', 'beginner', CURRENT_TIMESTAMP);
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user_id": "user-uuid-123",
  "email": "student@example.com",
  "username": "johndoe",
  "role": "student"
}
```

**Application Layer Responsibilities:**
- Password hashing (bcrypt)
- UUID generation for all three tables
- Ensuring all three tables are updated atomically (transaction-like behavior)
- Email format validation
- Password strength validation

---

#### **POST /api/auth/login**
**Purpose:** Authenticate user and issue JWT token  
**REST Method:** POST  
**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "securepass123"
}
```

**Relevant DB Tables:** `users_auth`, `users_profile`

**Database Query Steps:**
```sql
-- Step 1: Retrieve user authentication data
SELECT user_id, email, password_hash, role, created_at
FROM users_auth
WHERE email = 'student@example.com';
-- If not found â†’ Return 401 Unauthorized: "Invalid credentials"

-- Step 2: Verify password (application layer)
-- bcrypt.checkpw(provided_password, stored_password_hash)
-- If mismatch â†’ Return 401 Unauthorized: "Invalid credentials"

-- Step 3: Update last_login timestamp
UPDATE users_auth
SET last_login = CURRENT_TIMESTAMP
WHERE user_id = 'user-uuid-123';

-- Step 4: Fetch user profile data (separate query, NO JOIN)
SELECT username, full_name, avatar_url
FROM users_profile
WHERE user_id = 'user-uuid-123';
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": "user-uuid-123",
    "email": "student@example.com",
    "username": "johndoe",
    "role": "student"
  }
}
```

**Application Layer Responsibilities:**
- Password verification (bcrypt)
- JWT token generation with user_id, email, role
- Token expiration handling (e.g., 24 hours)
- Rate limiting on failed login attempts

---

### 2.2 Resource Management Endpoints

#### **POST /api/resources/upload**
**Purpose:** Upload a new study resource  
**REST Method:** POST  
**Request Body (multipart/form-data):**
```
file: [PDF/Video file]
title: "Calculus Study Guide"
description: "Comprehensive calculus notes"
resource_type: "pdf"
difficulty_level: "intermediate"
tags: ["calculus", "mathematics", "derivatives"]
```

**Relevant DB Tables:** `resources_metadata`, `resources_content`, `resources_stats`, `tags_master`, `mapping_resource_tags`

**Database Query Steps:**
```sql
-- Step 1: Verify user exists and is authenticated
-- (JWT token validation in middleware extracts user_id)
SELECT user_id FROM users_auth WHERE user_id = 'user-uuid-123';
-- If not found â†’ Return 401 Unauthorized

-- Step 2: Generate resource_id (UUID)
-- resource_id = uuid.uuid4()

-- Step 3: Upload file to storage (S3/local) and get file_path
-- file_path = storage_service.upload(file)
-- file_size = get_file_size(file)

-- Step 4: Insert into resources_metadata
INSERT INTO resources_metadata (
    resource_id, title, description, resource_type,
    difficulty_level, file_size_mb, upload_timestamp, uploader_user_id
) VALUES (
    'resource-uuid-456', 'Calculus Study Guide',
    'Comprehensive calculus notes', 'pdf', 'intermediate',
    2.45, CURRENT_TIMESTAMP, 'user-uuid-123'
);

-- Step 5: Insert into resources_content (separate table, NO FK)
INSERT INTO resources_content (
    content_id, resource_id, file_path, file_url,
    mime_type, page_count, storage_location, checksum
) VALUES (
    'content-uuid-789', 'resource-uuid-456',
    '/uploads/calculus-guide.pdf', 'https://cdn.../calculus-guide.pdf',
    'application/pdf', 45, 's3', 'sha256hash...'
);

-- Step 6: Initialize resource stats (separate table, NO FK)
INSERT INTO resources_stats (
    stat_id, resource_id, view_count, download_count,
    favorite_count, average_rating, rating_count, updated_at
) VALUES (
    'stat-uuid-012', 'resource-uuid-456', 0, 0, 0, 0.00, 0, CURRENT_TIMESTAMP
);

-- Step 7: Process tags (for each tag in ["calculus", "mathematics", "derivatives"])
-- For tag "calculus":
SELECT tag_id FROM tags_master WHERE tag_name = 'calculus';
-- If not found â†’ Create new tag
INSERT INTO tags_master (tag_id, tag_name, category, usage_count, created_at)
VALUES ('tag-uuid-101', 'calculus', 'subject', 1, CURRENT_TIMESTAMP);

-- Step 8: Create mapping entries (NO FK constraints)
INSERT INTO mapping_resource_tags (
    mapping_id, resource_id, tag_id, assigned_at, assigned_by_user_id, confidence
) VALUES (
    'map-uuid-201', 'resource-uuid-456', 'tag-uuid-101',
    CURRENT_TIMESTAMP, 'user-uuid-123', 1.0
);
-- Repeat for "mathematics" and "derivatives" tags
```

**Response (201 Created):**
```json
{
  "message": "Resource uploaded successfully",
  "resource_id": "resource-uuid-456",
  "title": "Calculus Study Guide",
  "file_url": "https://cdn.../calculus-guide.pdf",
  "tags": ["calculus", "mathematics", "derivatives"],
  "upload_timestamp": "2025-11-26T10:30:00Z"
}
```

**Application Layer Responsibilities:**
- File upload validation (type, size, virus scan)
- UUID generation for resource, content, stats
- File storage management (S3/local)
- Tag creation and mapping logic
- Checksum calculation for file integrity
- Metadata extraction (PDF page count, video duration)

---

#### **GET /api/resources/{resource_id}**
**Purpose:** Retrieve detailed information about a specific resource  
**REST Method:** GET  
**URL Parameters:** `resource_id` (e.g., "resource-uuid-456")

**Relevant DB Tables:** `resources_metadata`, `resources_content`, `resources_stats`, `mapping_resource_tags`, `tags_master`, `users_profile`

**Database Query Steps:**
```sql
-- Step 1: Verify resource exists
SELECT resource_id, title, description, resource_type, difficulty_level,
       file_size_mb, upload_timestamp, uploader_user_id
FROM resources_metadata
WHERE resource_id = 'resource-uuid-456';
-- If not found â†’ Return 404 Not Found: "Resource not found"

-- Step 2: Fetch resource content details (separate query, NO JOIN)
SELECT file_url, mime_type, page_count, duration_seconds
FROM resources_content
WHERE resource_id = 'resource-uuid-456';

-- Step 3: Fetch resource statistics (separate query, NO JOIN)
SELECT view_count, download_count, favorite_count,
       average_rating, rating_count, last_accessed
FROM resources_stats
WHERE resource_id = 'resource-uuid-456';

-- Step 4: Fetch uploader profile (separate query, NO JOIN)
SELECT username, avatar_url
FROM users_profile
WHERE user_id = 'user-uuid-123';

-- Step 5: Fetch tags via mapping table (NO JOIN)
SELECT tag_id FROM mapping_resource_tags
WHERE resource_id = 'resource-uuid-456';
-- Returns: ['tag-uuid-101', 'tag-uuid-102', 'tag-uuid-103']

-- Step 6: Fetch tag names (application layer loops through tag_ids)
SELECT tag_name, category
FROM tags_master
WHERE tag_id = 'tag-uuid-101';
-- Repeat for each tag_id
```

**Response (200 OK):**
```json
{
  "resource_id": "resource-uuid-456",
  "title": "Calculus Study Guide",
  "description": "Comprehensive calculus notes",
  "resource_type": "pdf",
  "difficulty_level": "intermediate",
  "file_size_mb": 2.45,
  "file_url": "https://cdn.../calculus-guide.pdf",
  "page_count": 45,
  "upload_timestamp": "2025-11-26T10:30:00Z",
  "uploader": {
    "username": "johndoe",
    "avatar_url": "https://cdn.../johndoe.jpg"
  },
  "stats": {
    "views": 125,
    "downloads": 34,
    "favorites": 12,
    "average_rating": 4.5,
    "rating_count": 18
  },
  "tags": [
    {"name": "calculus", "category": "subject"},
    {"name": "mathematics", "category": "subject"},
    {"name": "derivatives", "category": "topic"}
  ]
}
```

**Application Layer Responsibilities:**
- Verify resource existence before querying related tables
- Assemble data from 6 different tables (NO JOINs)
- Handle missing data gracefully (e.g., no uploader profile)
- Cache frequently accessed resources

---

#### **DELETE /api/resources/{resource_id}**
**Purpose:** Delete a resource (only by owner or admin)  
**REST Method:** DELETE  
**URL Parameters:** `resource_id`  
**Headers:** `Authorization: Bearer {jwt_token}`

**Relevant DB Tables:** `resources_metadata`, `resources_content`, `resources_stats`, `mapping_resource_tags`, `activities_views`, `activities_downloads`, `activities_ratings`, `recommendations_generated`

**Database Query Steps:**
```sql
-- Step 1: Verify resource exists
SELECT resource_id, uploader_user_id
FROM resources_metadata
WHERE resource_id = 'resource-uuid-456';
-- If not found â†’ Return 404 Not Found

-- Step 2: Verify ownership (application layer)
-- Extract user_id from JWT token
-- If user_id != uploader_user_id AND role != 'admin'
--     â†’ Return 403 Forbidden: "Not authorized to delete this resource"

-- Step 3: Get file path for deletion
SELECT file_path, storage_location
FROM resources_content
WHERE resource_id = 'resource-uuid-456';
-- Delete file from storage (S3/local) - application layer

-- Step 4: Delete from resources_metadata
DELETE FROM resources_metadata WHERE resource_id = 'resource-uuid-456';

-- Step 5: Delete from resources_content (NO CASCADE, manual deletion)
DELETE FROM resources_content WHERE resource_id = 'resource-uuid-456';

-- Step 6: Delete from resources_stats (NO CASCADE, manual deletion)
DELETE FROM resources_stats WHERE resource_id = 'resource-uuid-456';

-- Step 7: Delete tag mappings (NO CASCADE, manual deletion)
DELETE FROM mapping_resource_tags WHERE resource_id = 'resource-uuid-456';

-- Step 8: Delete activity logs (optional - keep for analytics)
-- DELETE FROM activities_views WHERE resource_id = 'resource-uuid-456';
-- DELETE FROM activities_downloads WHERE resource_id = 'resource-uuid-456';
-- DELETE FROM activities_ratings WHERE resource_id = 'resource-uuid-456';

-- Step 9: Delete recommendations (optional - keep for history)
-- DELETE FROM recommendations_generated WHERE resource_id = 'resource-uuid-456';
```

**Response (200 OK):**
```json
{
  "message": "Resource deleted successfully",
  "resource_id": "resource-uuid-456",
  "deleted_at": "2025-11-26T12:45:00Z"
}
```

**Application Layer Responsibilities:**
- Authorization check (ownership or admin role)
- Manual deletion from multiple tables (no cascade)
- File deletion from storage system
- Decision on whether to keep activity logs for analytics
- Handle partial deletion failures (implement transaction-like behavior)

---

### 2.3 Recommendation Endpoints

#### **GET /api/recommendations/personalized**
**Purpose:** Get personalized resource recommendations for authenticated user  
**REST Method:** GET  
**Headers:** `Authorization: Bearer {jwt_token}`  
**Query Parameters:** `limit=10`, `subject=mathematics` (optional filter)

**Relevant DB Tables:** `users_auth`, `users_preferences`, `activities_views`, `activities_ratings`, `mapping_user_interests`, `resources_metadata`, `resources_stats`, `mapping_resource_tags`, `recommendations_generated`

**Database Query Steps:**
```sql
-- Step 1: Extract user_id from JWT token and verify user exists
SELECT user_id, role FROM users_auth WHERE user_id = 'user-uuid-123';
-- If not found â†’ Return 401 Unauthorized

-- Step 2: Fetch user preferences (separate query, NO JOIN)
SELECT learning_style, preferred_subjects, difficulty_level
FROM users_preferences
WHERE user_id = 'user-uuid-123';
-- Returns: {'learning_style': 'visual', 'preferred_subjects': ['mathematics', 'physics'], 
--            'difficulty_level': 'intermediate'}

-- Step 3: Fetch user interests via mapping table (NO JOIN)
SELECT tag_id, interest_level
FROM mapping_user_interests
WHERE user_id = 'user-uuid-123';
-- Returns: [('tag-uuid-101', 'high'), ('tag-uuid-102', 'medium')]

-- Step 4: Fetch user's past viewed resources (to exclude from recommendations)
SELECT DISTINCT resource_id
FROM activities_views
WHERE user_id = 'user-uuid-123'
ORDER BY view_timestamp DESC
LIMIT 50;
-- Returns: ['resource-uuid-100', 'resource-uuid-200', ...]

-- Step 5: Fetch user's highly rated resources (to find similar ones)
SELECT resource_id, rating_value
FROM activities_ratings
WHERE user_id = 'user-uuid-123' AND rating_value >= 4;
-- Returns: [('resource-uuid-300', 5), ('resource-uuid-400', 4)]

-- Step 6: Find resources with user's interested tags (via mapping table, NO JOIN)
SELECT resource_id, tag_id, confidence
FROM mapping_resource_tags
WHERE tag_id IN ('tag-uuid-101', 'tag-uuid-102')
ORDER BY confidence DESC;
-- Returns: list of resource_ids with matching tags

-- Step 7: Fetch metadata for candidate resources (application layer loops)
SELECT resource_id, title, description, resource_type, difficulty_level, upload_timestamp
FROM resources_metadata
WHERE resource_id IN ('resource-uuid-500', 'resource-uuid-600', 'resource-uuid-700')
  AND resource_id NOT IN ('resource-uuid-100', 'resource-uuid-200')  -- Exclude viewed
  AND difficulty_level = 'intermediate';  -- Match user's difficulty level

-- Step 8: Fetch stats for ranking (separate query per resource)
SELECT view_count, download_count, average_rating, rating_count
FROM resources_stats
WHERE resource_id = 'resource-uuid-500';
-- Repeat for each candidate resource

-- Step 9: Application layer calculates recommendation scores
-- score = (tag_match * 0.4) + (difficulty_match * 0.2) + 
--         (popularity * 0.2) + (rating * 0.2)
-- Sort by score and select top N

-- Step 10: Log recommendations (for feedback tracking)
INSERT INTO recommendations_generated (
    recommendation_id, user_id, resource_id, algorithm_used,
    confidence_score, reason, generated_at, position
) VALUES (
    'rec-uuid-001', 'user-uuid-123', 'resource-uuid-500',
    'content-based', 0.87, 'Based on your interest in calculus',
    CURRENT_TIMESTAMP, 1
);
-- Repeat for each recommended resource
```

**Response (200 OK):**
```json
{
  "user_id": "user-uuid-123",
  "recommendations": [
    {
      "resource_id": "resource-uuid-500",
      "title": "Advanced Calculus Problems",
      "description": "Practice problems with solutions",
      "resource_type": "pdf",
      "difficulty_level": "intermediate",
      "confidence_score": 0.87,
      "reason": "Based on your interest in calculus and high ratings on similar resources",
      "stats": {
        "views": 450,
        "average_rating": 4.6,
        "downloads": 120
      },
      "tags": ["calculus", "mathematics", "problem-solving"]
    },
    {
      "resource_id": "resource-uuid-600",
      "title": "Calculus Video Lectures",
      "resource_type": "video",
      "confidence_score": 0.82,
      "reason": "Matches your visual learning style preference"
    }
    // ... up to 10 recommendations
  ],
  "total": 10,
  "generated_at": "2025-11-26T13:00:00Z"
}
```

**Application Layer Responsibilities:**
- Complex recommendation algorithm implementation
- Score calculation based on multiple factors
- Data assembly from 8+ tables without JOINs
- Filtering already-viewed resources
- Matching user preferences (learning style, difficulty level)
- Logging recommendations for feedback analysis
- Caching recommendation results

---

### 2.4 Search Endpoints

#### **GET /api/search/resources**
**Purpose:** Search for resources by keywords, tags, and filters  
**REST Method:** GET  
**Query Parameters:**
- `q=calculus` (search query)
- `tags=mathematics,derivatives` (tag filters)
- `difficulty=intermediate` (difficulty filter)
- `type=pdf` (resource type filter)
- `limit=20`, `offset=0` (pagination)

**Relevant DB Tables:** `resources_metadata`, `resources_stats`, `tags_master`, `mapping_resource_tags`

**Database Query Steps:**
```sql
-- Step 1: If tags provided, find tag_ids (separate queries)
SELECT tag_id FROM tags_master WHERE tag_name = 'mathematics';
SELECT tag_id FROM tags_master WHERE tag_name = 'derivatives';
-- Returns: ['tag-uuid-101', 'tag-uuid-103']

-- Step 2: Find resources with matching tags (via mapping table, NO JOIN)
SELECT resource_id, COUNT(*) as tag_match_count
FROM mapping_resource_tags
WHERE tag_id IN ('tag-uuid-101', 'tag-uuid-103')
GROUP BY resource_id
HAVING COUNT(*) >= 1  -- At least one tag matches
ORDER BY tag_match_count DESC;
-- Returns: resource_ids ranked by tag relevance

-- Step 3: Search in resources_metadata by keyword (separate query)
SELECT resource_id, title, description, resource_type, difficulty_level
FROM resources_metadata
WHERE (title LIKE '%calculus%' OR description LIKE '%calculus%')
  AND difficulty_level = 'intermediate'
  AND resource_type = 'pdf'
ORDER BY upload_timestamp DESC
LIMIT 20 OFFSET 0;
-- Returns: resources matching keyword and filters

-- Step 4: Intersect tag results and keyword results (application layer)
-- Find resource_ids present in both lists

-- Step 5: Fetch stats for each result (separate query per resource)
SELECT view_count, download_count, average_rating
FROM resources_stats
WHERE resource_id = 'resource-uuid-500';
-- Repeat for each resource in results

-- Step 6: Fetch tags for each resource (via mapping table)
SELECT tag_id FROM mapping_resource_tags WHERE resource_id = 'resource-uuid-500';
-- Then fetch tag names: SELECT tag_name FROM tags_master WHERE tag_id = ?
```

**Response (200 OK):**
```json
{
  "query": "calculus",
  "filters": {
    "tags": ["mathematics", "derivatives"],
    "difficulty": "intermediate",
    "type": "pdf"
  },
  "results": [
    {
      "resource_id": "resource-uuid-500",
      "title": "Advanced Calculus Problems",
      "description": "Comprehensive problem set for intermediate students",
      "resource_type": "pdf",
      "difficulty_level": "intermediate",
      "relevance_score": 0.92,
      "stats": {
        "views": 450,
        "average_rating": 4.6,
        "downloads": 120
      },
      "tags": ["calculus", "mathematics", "derivatives", "problem-solving"]
    }
    // ... up to 20 results
  ],
  "total_results": 156,
  "limit": 20,
  "offset": 0,
  "page": 1,
  "total_pages": 8
}
```

**Application Layer Responsibilities:**
- Keyword search implementation (consider full-text search later)
- Combining tag-based and keyword-based search results
- Relevance scoring algorithm
- Pagination logic
- Assembling data from 4 tables without JOINs
- Caching popular search queries

---

### 2.5 Activity Tracking Endpoints

#### **POST /api/activities/view**
**Purpose:** Log when a user views a resource  
**REST Method:** POST  
**Headers:** `Authorization: Bearer {jwt_token}`  
**Request Body:**
```json
{
  "resource_id": "resource-uuid-456",
  "view_duration_seconds": 245,
  "device_type": "desktop",
  "session_id": "session-xyz-789"
}
```

**Relevant DB Tables:** `activities_views`, `resources_stats`, `users_auth`, `resources_metadata`

**Database Query Steps:**
```sql
-- Step 1: Verify user exists (extract from JWT)
SELECT user_id FROM users_auth WHERE user_id = 'user-uuid-123';
-- If not found â†’ Return 401 Unauthorized

-- Step 2: Verify resource exists
SELECT resource_id FROM resources_metadata WHERE resource_id = 'resource-uuid-456';
-- If not found â†’ Return 404 Not Found: "Resource not found"

-- Step 3: Log view event (independent table, NO FK constraints)
INSERT INTO activities_views (
    view_id, user_id, resource_id, view_timestamp,
    view_duration_seconds, device_type, session_id
) VALUES (
    'view-uuid-001', 'user-uuid-123', 'resource-uuid-456',
    CURRENT_TIMESTAMP, 245, 'desktop', 'session-xyz-789'
);

-- Step 4: Update resource stats (separate table, NO JOIN)
UPDATE resources_stats
SET view_count = view_count + 1,
    last_accessed = CURRENT_TIMESTAMP,
    updated_at = CURRENT_TIMESTAMP
WHERE resource_id = 'resource-uuid-456';
```

**Response (201 Created):**
```json
{
  "message": "View logged successfully",
  "view_id": "view-uuid-001",
  "resource_id": "resource-uuid-456",
  "timestamp": "2025-11-26T14:30:00Z"
}
```

**Application Layer Responsibilities:**
- User authentication verification
- Resource existence validation
- Atomic updates (view log + stats increment)
- Preventing duplicate view logging (same user, same resource, within 5 minutes)
- Session tracking

---

#### **POST /api/activities/download**
**Purpose:** Log resource download and provide download URL  
**REST Method:** POST  
**Headers:** `Authorization: Bearer {jwt_token}`  
**Request Body:**
```json
{
  "resource_id": "resource-uuid-456"
}
```

**Relevant DB Tables:** `activities_downloads`, `resources_metadata`, `resources_content`, `resources_stats`

**Database Query Steps:**
```sql
-- Step 1: Verify user exists
SELECT user_id FROM users_auth WHERE user_id = 'user-uuid-123';

-- Step 2: Verify resource exists
SELECT resource_id FROM resources_metadata WHERE resource_id = 'resource-uuid-456';

-- Step 3: Get download URL and file size
SELECT file_url, file_path, mime_type
FROM resources_content
WHERE resource_id = 'resource-uuid-456';

-- Step 4: Check file size for bandwidth tracking
SELECT file_size_mb FROM resources_metadata WHERE resource_id = 'resource-uuid-456';

-- Step 5: Log download event (independent table, NO FK)
INSERT INTO activities_downloads (
    download_id, user_id, resource_id, download_timestamp,
    file_size_downloaded, download_success, ip_address
) VALUES (
    'download-uuid-002', 'user-uuid-123', 'resource-uuid-456',
    CURRENT_TIMESTAMP, 2567890, TRUE, '192.168.1.100'
);

-- Step 6: Increment download count (separate table)
UPDATE resources_stats
SET download_count = download_count + 1,
    updated_at = CURRENT_TIMESTAMP
WHERE resource_id = 'resource-uuid-456';
```

**Response (200 OK):**
```json
{
  "message": "Download logged successfully",
  "download_id": "download-uuid-002",
  "download_url": "https://cdn.example.com/calculus-guide.pdf?token=xyz",
  "file_name": "calculus-guide.pdf",
  "file_size_mb": 2.45,
  "expires_at": "2025-11-26T15:00:00Z"
}
```

**Application Layer Responsibilities:**
- Generate signed/temporary download URLs (security)
- Track download success/failure
- Bandwidth monitoring
- IP address logging for analytics
- Rate limiting downloads per user

---

#### **POST /api/activities/rate**
**Purpose:** Submit a rating/review for a resource  
**REST Method:** POST  
**Headers:** `Authorization: Bearer {jwt_token}`  
**Request Body:**
```json
{
  "resource_id": "resource-uuid-456",
  "rating_value": 5,
  "review_text": "Excellent study guide! Very helpful for my exam prep."
}
```

**Relevant DB Tables:** `activities_ratings`, `resources_stats`, `users_auth`, `resources_metadata`

**Database Query Steps:**
```sql
-- Step 1: Verify user exists
SELECT user_id FROM users_auth WHERE user_id = 'user-uuid-123';

-- Step 2: Verify resource exists
SELECT resource_id FROM resources_metadata WHERE resource_id = 'resource-uuid-456';

-- Step 3: Check if user already rated this resource
SELECT rating_id, rating_value
FROM activities_ratings
WHERE user_id = 'user-uuid-123' AND resource_id = 'resource-uuid-456';
-- If exists â†’ UPDATE instead of INSERT

-- Step 4a: If new rating, INSERT
INSERT INTO activities_ratings (
    rating_id, user_id, resource_id, rating_value,
    review_text, rated_at, updated_at
) VALUES (
    'rating-uuid-003', 'user-uuid-123', 'resource-uuid-456', 5,
    'Excellent study guide! Very helpful for my exam prep.',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

-- Step 4b: If updating existing rating, UPDATE
UPDATE activities_ratings
SET rating_value = 5,
    review_text = 'Excellent study guide! Very helpful for my exam prep.',
    updated_at = CURRENT_TIMESTAMP
WHERE rating_id = 'rating-uuid-003';

-- Step 5: Recalculate average rating (get all ratings for this resource)
SELECT AVG(rating_value) as new_avg, COUNT(*) as new_count
FROM activities_ratings
WHERE resource_id = 'resource-uuid-456';
-- Returns: {new_avg: 4.6, new_count: 19}

-- Step 6: Update resource stats (separate table)
UPDATE resources_stats
SET average_rating = 4.6,
    rating_count = 19,
    updated_at = CURRENT_TIMESTAMP
WHERE resource_id = 'resource-uuid-456';
```

**Response (201 Created or 200 OK if updating):**
```json
{
  "message": "Rating submitted successfully",
  "rating_id": "rating-uuid-003",
  "resource_id": "resource-uuid-456",
  "rating_value": 5,
  "updated_stats": {
    "average_rating": 4.6,
    "rating_count": 19
  },
  "timestamp": "2025-11-26T15:15:00Z"
}
```

**Application Layer Responsibilities:**
- Validate rating value (1-5 range)
- Check for existing ratings (update vs. insert)
- Recalculate aggregate statistics
- Sanitize review text (prevent XSS)
- Rate limiting (one rating per resource per user per day)

---

### 2.6 User Profile Endpoints

#### **GET /api/users/profile**
**Purpose:** Get authenticated user's profile with activity summary  
**REST Method:** GET  
**Headers:** `Authorization: Bearer {jwt_token}`

**Relevant DB Tables:** `users_auth`, `users_profile`, `users_preferences`, `activities_views`, `activities_downloads`, `activities_ratings`, `resources_metadata`, `mapping_user_interests`

**Database Query Steps:**
```sql
-- Step 1: Extract user_id from JWT and verify
SELECT user_id, email, role, created_at
FROM users_auth
WHERE user_id = 'user-uuid-123';

-- Step 2: Fetch profile data (separate query, NO JOIN)
SELECT username, full_name, bio, avatar_url
FROM users_profile
WHERE user_id = 'user-uuid-123';

-- Step 3: Fetch preferences (separate query, NO JOIN)
SELECT learning_style, preferred_subjects, difficulty_level, study_time_preference
FROM users_preferences
WHERE user_id = 'user-uuid-123';

-- Step 4: Count user's uploaded resources
SELECT COUNT(*) as resources_uploaded
FROM resources_metadata
WHERE uploader_user_id = 'user-uuid-123';

-- Step 5: Count user's activities (separate queries)
SELECT COUNT(*) as total_views FROM activities_views WHERE user_id = 'user-uuid-123';
SELECT COUNT(*) as total_downloads FROM activities_downloads WHERE user_id = 'user-uuid-123';
SELECT COUNT(*) as total_ratings FROM activities_ratings WHERE user_id = 'user-uuid-123';

-- Step 6: Get user's recent activity (last 5 viewed resources)
SELECT resource_id, view_timestamp
FROM activities_views
WHERE user_id = 'user-uuid-123'
ORDER BY view_timestamp DESC
LIMIT 5;

-- Step 7: Fetch metadata for recent resources (application loops)
SELECT resource_id, title, resource_type
FROM resources_metadata
WHERE resource_id IN (list from step 6);

-- Step 8: Get user interests via mapping table
SELECT tag_id, interest_level
FROM mapping_user_interests
WHERE user_id = 'user-uuid-123';

-- Step 9: Fetch tag names (application loops)
SELECT tag_name, category FROM tags_master WHERE tag_id = 'tag-uuid-101';
```

**Response (200 OK):**
```json
{
  "user_id": "user-uuid-123",
  "email": "student@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "student",
  "bio": "Computer Science student passionate about mathematics",
  "avatar_url": "https://cdn.../johndoe.jpg",
  "preferences": {
    "learning_style": "visual",
    "preferred_subjects": ["mathematics", "physics", "computer-science"],
    "difficulty_level": "intermediate",
    "study_time_preference": "evening"
  },
  "interests": [
    {"tag": "calculus", "level": "high"},
    {"tag": "algorithms", "level": "medium"},
    {"tag": "quantum-mechanics", "level": "low"}
  ],
  "activity_summary": {
    "resources_uploaded": 3,
    "resources_viewed": 47,
    "resources_downloaded": 12,
    "ratings_given": 8,
    "member_since": "2025-09-15T10:00:00Z"
  },
  "recent_activity": [
    {
      "resource_id": "resource-uuid-500",
      "title": "Advanced Calculus Problems",
      "type": "pdf",
      "viewed_at": "2025-11-26T14:30:00Z"
    }
    // ... up to 5 recent views
  ]
}
```

**Application Layer Responsibilities:**
- Assemble data from 9 different tables (NO JOINs)
- Calculate activity summaries
- Format dates and timestamps
- Cache profile data for performance
- Handle missing data gracefully

---

## 3. API Design Patterns Summary

### Cross-Table Validation Pattern
```
1. Extract entity ID from request (user_id, resource_id, etc.)
2. Query base table to verify entity exists
3. If not found â†’ Return 404 Not Found
4. Proceed with business logic
```

### Ownership Validation Pattern
```
1. Extract user_id from JWT token
2. Query metadata table to get owner_user_id
3. Compare user_id === owner_user_id OR role === 'admin'
4. If unauthorized â†’ Return 403 Forbidden
5. Proceed with action
```

### Mapping Table Relationship Pattern
```
1. Query mapping table (e.g., mapping_resource_tags)
2. Get list of related IDs
3. Loop through IDs and query respective tables
4. Assemble results in application layer
5. Return aggregated response
```

### Multi-Table Assembly Pattern
```
1. Query table A for primary data
2. Extract foreign reference (e.g., user_id)
3. Query table B using reference (separate query, NO JOIN)
4. Query table C for additional data
5. Combine all data in application layer
6. Return unified response
```

### Stats Update Pattern
```
1. Perform main action (view, download, rate)
2. Log event in activity table
3. Separately update stats table (increment counters)
4. Handle failures gracefully (retry logic)
```

---

## 4. Application Layer Responsibilities Summary

For all endpoints, the application layer must handle:

1. **Authentication & Authorization:**
   - JWT token validation
   - User existence verification
   - Role-based access control
   - Ownership checks

2. **Entity Existence Validation:**
   - Verify user_id exists in users_auth before operations
   - Verify resource_id exists in resources_metadata
   - Check tag_id exists before creating mappings

3. **Cross-Table Consistency:**
   - Manual cascade deletes (no foreign key cascade)
   - Transaction-like behavior across multiple tables
   - Rollback handling on partial failures

4. **Data Assembly:**
   - Fetch data from multiple tables (NO JOINs)
   - Combine results in memory
   - Format unified response

5. **Business Logic:**
   - Recommendation algorithms
   - Search relevance scoring
   - Statistics calculations
   - Validation rules

6. **Performance Optimization:**
   - Caching frequently accessed data
   - Pagination implementation
   - Query result limiting
   - Connection pooling

---

## End of Part 3: API Integration