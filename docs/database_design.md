# Assignment 3 - Part 2: Database Design (Low-Cohesion)
## Smart Study Resource Recommender - Team 24

**Team Members:** Tyler Sanford, Josh England, Kendric Jones  
**Date:** November 26, 2025

---

## 1. Database Design Overview

This database design follows **Low-Cohesion principles** to minimize cross-table dependencies and reduce JOIN operations. Each logical entity is intentionally split across multiple independent tables, with relationships managed through mapping tables rather than foreign keys.

**Design Philosophy:** Prioritize query performance and scalability by denormalizing data and avoiding foreign key constraints where possible.

---

## 2. Core Entities Identification

Based on the Smart Study Resource Recommender requirements, we identified these core entities:

1. **User** - Students, instructors, and tutors using the system
2. **Resource** - Study materials (PDFs, videos, notes, documents)
3. **Recommendation** - Personalized resource suggestions for users
4. **Activity** - User interactions with resources (views, downloads, ratings)
5. **Tag** - Categorization labels for resources
6. **Preference** - User learning preferences and interests

---

## 3. Low-Cohesion Schema Design

### 3.1 User Domain Tables

#### Table: `users_auth`
**Purpose:** Store authentication-related user data only  
**Independent Responsibility:** Handle login credentials and security

| Column | Type | Description |
|--------|------|-------------|
| user_id | VARCHAR(36) | Primary identifier (UUID) |
| email | VARCHAR(255) | User email (unique) |
| password_hash | VARCHAR(255) | Bcrypt hashed password |
| role | VARCHAR(20) | User role (student/instructor/tutor) |
| created_at | TIMESTAMP | Account creation timestamp |
| last_login | TIMESTAMP | Last successful login |

**No Foreign Keys** - This table is completely independent

---

#### Table: `users_profile`
**Purpose:** Store user profile and personal information  
**Independent Responsibility:** Manage user identity and metadata

| Column | Type | Description |
|--------|------|-------------|
| profile_id | VARCHAR(36) | Primary identifier (UUID) |
| user_id | VARCHAR(36) | Links to users_auth (NO FK constraint) |
| username | VARCHAR(100) | Display name |
| full_name | VARCHAR(255) | Complete name |
| bio | TEXT | User biography |
| avatar_url | VARCHAR(500) | Profile picture URL |
| updated_at | TIMESTAMP | Last profile update |

**No Foreign Keys** - Linked via user_id value only, no constraint enforced

---

#### Table: `users_preferences`
**Purpose:** Store user learning preferences and interests  
**Independent Responsibility:** Track user study habits and preferences

| Column | Type | Description |
|--------|------|-------------|
| preference_id | VARCHAR(36) | Primary identifier (UUID) |
| user_id | VARCHAR(36) | Links to users_auth (NO FK constraint) |
| learning_style | VARCHAR(50) | visual/auditory/kinesthetic |
| preferred_subjects | TEXT | JSON array of subjects |
| difficulty_level | VARCHAR(20) | beginner/intermediate/advanced |
| study_time_preference | VARCHAR(20) | morning/afternoon/evening/night |
| created_at | TIMESTAMP | Preference record creation |
| updated_at | TIMESTAMP | Last preference update |

**No Foreign Keys** - Completely independent table

---

### 3.2 Resource Domain Tables

#### Table: `resources_metadata`
**Purpose:** Store core resource information and metadata  
**Independent Responsibility:** Manage resource identity and basic info

| Column | Type | Description |
|--------|------|-------------|
| resource_id | VARCHAR(36) | Primary identifier (UUID) |
| title | VARCHAR(500) | Resource title |
| description | TEXT | Resource description |
| resource_type | VARCHAR(50) | pdf/video/document/notes/slides |
| difficulty_level | VARCHAR(20) | beginner/intermediate/advanced |
| file_size_mb | DECIMAL(10,2) | File size in megabytes |
| upload_timestamp | TIMESTAMP | When resource was uploaded |
| uploader_user_id | VARCHAR(36) | Who uploaded (NO FK constraint) |

**No Foreign Keys** - uploader_user_id is informational only

---

#### Table: `resources_content`
**Purpose:** Store actual resource content and file information  
**Independent Responsibility:** Manage file storage and access

| Column | Type | Description |
|--------|------|-------------|
| content_id | VARCHAR(36) | Primary identifier (UUID) |
| resource_id | VARCHAR(36) | Links to resources_metadata (NO FK) |
| file_path | VARCHAR(1000) | Storage location path |
| file_url | VARCHAR(1000) | Direct access URL |
| mime_type | VARCHAR(100) | File MIME type |
| page_count | INTEGER | Number of pages (for PDFs) |
| duration_seconds | INTEGER | Video/audio length |
| storage_location | VARCHAR(100) | S3/local/cloud identifier |
| checksum | VARCHAR(64) | File integrity hash |

**No Foreign Keys** - Independent storage management

---

#### Table: `resources_stats`
**Purpose:** Store resource usage statistics  
**Independent Responsibility:** Track resource popularity and engagement

| Column | Type | Description |
|--------|------|-------------|
| stat_id | VARCHAR(36) | Primary identifier (UUID) |
| resource_id | VARCHAR(36) | Links to resources_metadata (NO FK) |
| view_count | INTEGER | Total views |
| download_count | INTEGER | Total downloads |
| favorite_count | INTEGER | Times favorited |
| average_rating | DECIMAL(3,2) | Average user rating (0-5) |
| rating_count | INTEGER | Number of ratings |
| last_accessed | TIMESTAMP | Most recent access |
| updated_at | TIMESTAMP | Stats last updated |

**No Foreign Keys** - Aggregated data stored independently

---

### 3.3 Recommendation Domain Tables

#### Table: `recommendations_generated`
**Purpose:** Store generated recommendation records  
**Independent Responsibility:** Track recommendations shown to users

| Column | Type | Description |
|--------|------|-------------|
| recommendation_id | VARCHAR(36) | Primary identifier (UUID) |
| user_id | VARCHAR(36) | Target user (NO FK constraint) |
| resource_id | VARCHAR(36) | Recommended resource (NO FK) |
| algorithm_used | VARCHAR(50) | collaborative/content-based/hybrid |
| confidence_score | DECIMAL(5,4) | Recommendation strength (0-1) |
| reason | TEXT | Why this was recommended |
| generated_at | TIMESTAMP | When recommendation was created |
| position | INTEGER | Display position in list |

**No Foreign Keys** - All relationships via IDs only

---

#### Table: `recommendations_feedback`
**Purpose:** Store user feedback on recommendations  
**Independent Responsibility:** Collect recommendation quality data

| Column | Type | Description |
|--------|------|-------------|
| feedback_id | VARCHAR(36) | Primary identifier (UUID) |
| recommendation_id | VARCHAR(36) | Links to recommendations_generated (NO FK) |
| user_id | VARCHAR(36) | User providing feedback (NO FK) |
| was_clicked | BOOLEAN | Did user click recommendation |
| was_helpful | BOOLEAN | User-reported helpfulness |
| feedback_type | VARCHAR(50) | positive/negative/neutral/irrelevant |
| feedback_text | TEXT | Optional user comment |
| submitted_at | TIMESTAMP | Feedback submission time |

**No Foreign Keys** - Independent feedback collection

---

### 3.4 Activity Domain Tables

#### Table: `activities_views`
**Purpose:** Track when users view resources  
**Independent Responsibility:** Record view events only

| Column | Type | Description |
|--------|------|-------------|
| view_id | VARCHAR(36) | Primary identifier (UUID) |
| user_id | VARCHAR(36) | Viewing user (NO FK constraint) |
| resource_id | VARCHAR(36) | Viewed resource (NO FK) |
| view_timestamp | TIMESTAMP | When view occurred |
| view_duration_seconds | INTEGER | How long viewed |
| device_type | VARCHAR(50) | desktop/mobile/tablet |
| session_id | VARCHAR(100) | User session identifier |

**No Foreign Keys** - Pure event log

---

#### Table: `activities_downloads`
**Purpose:** Track resource download events  
**Independent Responsibility:** Record download actions

| Column | Type | Description |
|--------|------|-------------|
| download_id | VARCHAR(36) | Primary identifier (UUID) |
| user_id | VARCHAR(36) | Downloading user (NO FK) |
| resource_id | VARCHAR(36) | Downloaded resource (NO FK) |
| download_timestamp | TIMESTAMP | When download occurred |
| file_size_downloaded | BIGINT | Bytes transferred |
| download_success | BOOLEAN | Completed successfully |
| ip_address | VARCHAR(45) | User IP (for analytics) |

**No Foreign Keys** - Independent download tracking

---

#### Table: `activities_ratings`
**Purpose:** Store user ratings for resources  
**Independent Responsibility:** Manage rating data

| Column | Type | Description |
|--------|------|-------------|
| rating_id | VARCHAR(36) | Primary identifier (UUID) |
| user_id | VARCHAR(36) | Rating user (NO FK) |
| resource_id | VARCHAR(36) | Rated resource (NO FK) |
| rating_value | INTEGER | 1-5 star rating |
| review_text | TEXT | Optional review comment |
| rated_at | TIMESTAMP | When rating was given |
| updated_at | TIMESTAMP | Last rating update |

**No Foreign Keys** - Standalone rating records

---

### 3.5 Tag Domain Tables (Mapping Tables)

#### Table: `tags_master`
**Purpose:** Store all available tags in the system  
**Independent Responsibility:** Manage tag definitions

| Column | Type | Description |
|--------|------|-------------|
| tag_id | VARCHAR(36) | Primary identifier (UUID) |
| tag_name | VARCHAR(100) | Tag label (unique) |
| category | VARCHAR(50) | subject/topic/difficulty/format |
| usage_count | INTEGER | Times this tag is used |
| created_at | TIMESTAMP | Tag creation time |

**No Foreign Keys** - Completely independent tag registry

---

#### Table: `mapping_resource_tags`
**Purpose:** Link resources to tags without foreign keys  
**Independent Responsibility:** Manage resource-tag relationships

| Column | Type | Description |
|--------|------|-------------|
| mapping_id | VARCHAR(36) | Primary identifier (UUID) |
| resource_id | VARCHAR(36) | Resource identifier (NO FK) |
| tag_id | VARCHAR(36) | Tag identifier (NO FK) |
| assigned_at | TIMESTAMP | When tag was assigned |
| assigned_by_user_id | VARCHAR(36) | Who assigned tag (NO FK) |
| confidence | DECIMAL(3,2) | Tag relevance (auto-tags) |

**No Foreign Keys** - Pure mapping table, no constraints

**Key Feature:** This is a bridge table that manages relationships WITHOUT using JOIN operations or foreign keys

---

#### Table: `mapping_user_interests`
**Purpose:** Link users to subject tags they're interested in  
**Independent Responsibility:** Track user subject interests

| Column | Type | Description |
|--------|------|-------------|
| mapping_id | VARCHAR(36) | Primary identifier (UUID) |
| user_id | VARCHAR(36) | User identifier (NO FK) |
| tag_id | VARCHAR(36) | Interest tag (NO FK) |
| interest_level | VARCHAR(20) | high/medium/low |
| added_at | TIMESTAMP | When interest was recorded |
| last_interaction | TIMESTAMP | Most recent related activity |

**No Foreign Keys** - Manages user interests independently

---

## 4. Schema Diagram (Textual Representation)

```
LOW-COHESION DATABASE SCHEMA
(No foreign key constraints - relationships via mapping tables)

USER DOMAIN (Split into 3 independent tables):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  users_auth     â”‚     â”‚  users_profile   â”‚     â”‚ users_preferences   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤     â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ user_id (PK)    â”‚     â”‚ profile_id (PK)  â”‚     â”‚ preference_id (PK)  â”‚
â”‚ email           â”‚     â”‚ user_id          â”‚     â”‚ user_id             â”‚
â”‚ password_hash   â”‚     â”‚ username         â”‚     â”‚ learning_style      â”‚
â”‚ role            â”‚     â”‚ full_name        â”‚     â”‚ preferred_subjects  â”‚
â”‚ created_at      â”‚     â”‚ bio              â”‚     â”‚ difficulty_level    â”‚
â”‚ last_login      â”‚     â”‚ avatar_url       â”‚     â”‚ study_time_pref     â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â†“ user_id              â†“ user_id                 â†“ user_id
       (NO FK)                (NO FK)                    (NO FK)


RESOURCE DOMAIN (Split into 3 independent tables):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ resources_metadata   â”‚   â”‚ resources_content    â”‚   â”‚ resources_stats â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ resource_id (PK)     â”‚   â”‚ content_id (PK)      â”‚   â”‚ stat_id (PK)    â”‚
â”‚ title                â”‚   â”‚ resource_id          â”‚   â”‚ resource_id     â”‚
â”‚ description          â”‚   â”‚ file_path            â”‚   â”‚ view_count      â”‚
â”‚ resource_type        â”‚   â”‚ file_url             â”‚   â”‚ download_count  â”‚
â”‚ difficulty_level     â”‚   â”‚ mime_type            â”‚   â”‚ favorite_count  â”‚
â”‚ uploader_user_id     â”‚   â”‚ storage_location     â”‚   â”‚ average_rating  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â†“ resource_id            â†“ resource_id              â†“ resource_id
       (NO FK)                  (NO FK)                     (NO FK)


RECOMMENDATION DOMAIN (Split into 2 independent tables):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ recommendations_generatedâ”‚        â”‚ recommendations_feedback â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤        â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ recommendation_id (PK)  â”‚        â”‚ feedback_id (PK)         â”‚
â”‚ user_id                 â”‚        â”‚ recommendation_id        â”‚
â”‚ resource_id             â”‚        â”‚ user_id                  â”‚
â”‚ algorithm_used          â”‚        â”‚ was_clicked              â”‚
â”‚ confidence_score        â”‚        â”‚ was_helpful              â”‚
â”‚ generated_at            â”‚        â”‚ feedback_type            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       â†“ rec_id                           â†“ rec_id
       (NO FK)                            (NO FK)


ACTIVITY DOMAIN (Split into 3 independent event logs):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”   â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ activities_views â”‚   â”‚ activities_downloads  â”‚   â”‚ activities_ratingsâ”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤   â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ view_id (PK)     â”‚   â”‚ download_id (PK)      â”‚   â”‚ rating_id (PK)   â”‚
â”‚ user_id          â”‚   â”‚ user_id               â”‚   â”‚ user_id          â”‚
â”‚ resource_id      â”‚   â”‚ resource_id           â”‚   â”‚ resource_id      â”‚
â”‚ view_timestamp   â”‚   â”‚ download_timestamp    â”‚   â”‚ rating_value     â”‚
â”‚ view_duration    â”‚   â”‚ download_success      â”‚   â”‚ review_text      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜   â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜


MAPPING TABLES (Manage relationships WITHOUT foreign keys):
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚ tags_master          â”‚        â”‚ mapping_resource_tags  â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤        â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ tag_id (PK)          â”‚        â”‚ mapping_id (PK)        â”‚
â”‚ tag_name             â”‚        â”‚ resource_id            â”‚
â”‚ category             â”‚        â”‚ tag_id                 â”‚
â”‚ usage_count          â”‚        â”‚ assigned_at            â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
           â†“ tag_id                      â†“ tag_id
           (NO FK)                       (NO FK)

                       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                       â”‚ mapping_user_interests â”‚
                       â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
                       â”‚ mapping_id (PK)        â”‚
                       â”‚ user_id                â”‚
                       â”‚ tag_id                 â”‚
                       â”‚ interest_level         â”‚
                       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

---

## 5. Query Examples (No JOINs)

### Example 1: Get User's Recommended Resources

**Traditional High-Cohesion Approach (with JOINs):**
```sql
-- NOT USED - This requires multiple JOINs
SELECT r.title, r.description, rec.confidence_score
FROM recommendations_generated rec
JOIN resources_metadata r ON rec.resource_id = r.resource_id
JOIN users_auth u ON rec.user_id = u.user_id
WHERE u.email = 'student@example.com';
```

**Low-Cohesion Approach (NO JOINs):**
```sql
-- Step 1: Get user_id from email (separate query)
SELECT user_id FROM users_auth WHERE email = 'student@example.com';
-- Returns: 'user-123'

-- Step 2: Get recommendations (separate query)
SELECT resource_id, confidence_score, reason
FROM recommendations_generated
WHERE user_id = 'user-123'
ORDER BY confidence_score DESC
LIMIT 10;
-- Returns: list of resource_ids

-- Step 3: Get resource details (application layer loops through each)
SELECT title, description, resource_type
FROM resources_metadata
WHERE resource_id = 'resource-456';

-- Step 4: Get resource stats (separate query per resource)
SELECT view_count, average_rating, download_count
FROM resources_stats
WHERE resource_id = 'resource-456';
```

**Benefit:** Each query is simple, fast, and independently cacheable. Application layer handles data assembly.

---

### Example 2: Search Resources by Tag

**Low-Cohesion Approach:**
```sql
-- Step 1: Find tag_id for "Machine Learning"
SELECT tag_id FROM tags_master WHERE tag_name = 'Machine Learning';
-- Returns: 'tag-789'

-- Step 2: Get all resources with this tag (mapping table)
SELECT resource_id, assigned_at
FROM mapping_resource_tags
WHERE tag_id = 'tag-789'
ORDER BY assigned_at DESC;
-- Returns: list of resource_ids

-- Step 3: Fetch resource metadata (application loops)
SELECT title, description, difficulty_level, upload_timestamp
FROM resources_metadata
WHERE resource_id IN ('res-1', 'res-2', 'res-3');

-- Step 4: Get stats for each resource
SELECT view_count, average_rating
FROM resources_stats
WHERE resource_id IN ('res-1', 'res-2', 'res-3');
```

**Benefit:** Mapping table acts as bridge without foreign key constraints. Each query targets one table only.

---

### Example 3: Track User Activity

**Low-Cohesion Approach:**
```sql
-- Insert view event (completely independent)
INSERT INTO activities_views (
    view_id, user_id, resource_id, view_timestamp,
    view_duration_seconds, device_type, session_id
) VALUES (
    'view-001', 'user-123', 'resource-456',
    CURRENT_TIMESTAMP, 245, 'desktop', 'session-xyz'
);

-- Insert download event (separate table, no relation to view)
INSERT INTO activities_downloads (
    download_id, user_id, resource_id,
    download_timestamp, download_success
) VALUES (
    'download-002', 'user-123', 'resource-456',
    CURRENT_TIMESTAMP, TRUE
);

-- Insert rating (yet another independent table)
INSERT INTO activities_ratings (
    rating_id, user_id, resource_id,
    rating_value, review_text, rated_at
) VALUES (
    'rating-003', 'user-123', 'resource-456',
    5, 'Excellent study guide!', CURRENT_TIMESTAMP
);
```

**Benefit:** Each activity type stored separately. No foreign key validation overhead. Faster inserts.

---

## 6. Justification for Low-Cohesion Design Choices

### Where We Applied Low-Cohesion (and Why):

#### âœ… User Domain Split (3 tables)
**Why:** User authentication, profile, and preferences change at different rates and are queried separately. Login operations only need `users_auth`, profile displays only need `users_profile`, and recommendation engine only needs `users_preferences`.

**Performance Benefit:** Smaller table sizes, better index performance, independent caching strategies.

---

#### âœ… Resource Domain Split (3 tables)
**Why:** Resource metadata is frequently queried for searches, content storage details are only needed on download, and statistics are constantly updated but rarely joined with metadata.

**Performance Benefit:** Stats updates don't lock metadata queries. Content storage can scale independently (different storage backend).

---

#### âœ… Activity Domain Split (3 tables)
**Why:** View events, downloads, and ratings have different schemas, are written at different frequencies, and are analyzed separately. No need to JOIN them for typical queries.

**Performance Benefit:** High-volume event logging without foreign key validation overhead. Each table can be partitioned differently.

---

#### âœ… Mapping Tables Without Foreign Keys
**Why:** Resource-tag and user-interest relationships don't require referential integrity for this application. Tags can be created dynamically, and resources can be deleted without cascading.

**Performance Benefit:** No foreign key index maintenance, faster bulk inserts, easier data migration and archival.

---

### Where We DID NOT Use Low-Cohesion (and Why):

#### âŒ Authentication Credentials (users_auth)
**Why:** Login operations require ACID guarantees. Email uniqueness, password validation, and session management must be transactional. This is a critical security feature.

**Justification:** Authentication is high-transactional and requires data integrity. Password resets, account lockouts, and security auditing demand foreign key relationships to be maintained in a single authoritative table.

---

#### âŒ Payment/Billing System (if added)
**Why:** Financial transactions require strong consistency, foreign key constraints, and ACID compliance. Payment records must be linked to users with referential integrity.

**Justification:** Regulatory compliance (PCI-DSS) and financial accuracy require high-cohesion design. Cannot risk orphaned payment records or inconsistent billing data.

---

#### âŒ Real-Time Notification Queue (if added)
**Why:** Notification delivery requires immediate consistency and guaranteed delivery. Message queues need strong transactional boundaries.

**Justification:** Notifications for critical events (exam reminders, deadline alerts) must be delivered exactly once. This requires high-cohesion with proper foreign key relationships to ensure notification-user integrity.

---

## 7. Low-Cohesion Benefits for This Application

### Scalability:
Each table can be scaled independently. `activities_views` can be sharded by timestamp, `resources_metadata` by subject category, and `users_auth` by region.

### Performance:
- No JOIN operations means faster queries (O(1) lookups instead of O(n*m))
- Smaller indexes per table (only primary keys)
- Better cache hit rates (each table cached separately)
- Parallel query execution (multiple tables queried simultaneously)

### Maintainability:
- Schema changes to one table don't cascade to others
- Easier to add new activity types (just create new table)
- Simpler database migrations (no foreign key dependency chains)

### Flexibility:
- Can use different databases for different tables (e.g., MongoDB for resources_content, PostgreSQL for users_auth)
- Easier to archive old data (just move old activities_* tables)
- Can denormalize further if needed without breaking existing queries

---

## 8. Implementation Notes

### Application Layer Responsibility:
Since we avoid foreign keys, the application layer must:
1. Validate that user_id exists before creating recommendations
2. Check resource_id exists before logging activities
3. Handle orphaned records in mapping tables (cleanup jobs)
4. Maintain data consistency through application logic

### Database Configuration:
```sql
-- Example: Disable foreign key checks globally
-- (Not recommended for all tables, but acceptable for low-cohesion design)
SET FOREIGN_KEY_CHECKS = 0;

-- Create tables without FOREIGN KEY constraints
CREATE TABLE recommendations_generated (
    recommendation_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,  -- NO FOREIGN KEY
    resource_id VARCHAR(36) NOT NULL,  -- NO FOREIGN KEY
    confidence_score DECIMAL(5,4),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),  -- Index for fast lookups
    INDEX idx_resource_id (resource_id)
) ENGINE=InnoDB;
```

### Indexing Strategy:
Even without foreign keys, we create indexes on columns used for lookups:
- `users_auth.email` (UNIQUE INDEX)
- `users_auth.user_id` (PRIMARY KEY)
- `recommendations_generated.user_id` (INDEX)
- `mapping_resource_tags.resource_id` (INDEX)
- `mapping_resource_tags.tag_id` (INDEX)

---

## End of Part 2: Database Design (Low-Cohesion)