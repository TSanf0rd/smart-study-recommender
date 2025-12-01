# Assignment 3 - Part 1: Software Architecture Design
## Smart Study Resource Recommender - Team 24

**Team Members:** Tyler Sanford, Josh England, Kendric Jones  
**Date:** November 26, 2025

---

## 1. System Architecture Overview

The Smart Study Resource Recommender follows a **Layered (N-Tier) Architecture** with four distinct layers, each with specific responsibilities for handling study resource management, user authentication, personalized recommendations, and resource discovery.

---

## 2. Layered Architecture Table

| Layer | Components | Description | Responsibility |
|-------|-----------|-------------|----------------|
| **Presentation Layer** | - React Frontend<br>- Authentication UI (Login/Register)<br>- Resource Dashboard<br>- Upload Interface<br>- Search & Filter Components<br>- Recommendation Display<br>- User Profile Management | Provides web-based user interface for students, instructors, and tutors to interact with the study resource recommendation system | - Display study resources and recommendations<br>- Capture user inputs (credentials, resource uploads, search queries)<br>- Render personalized resource suggestions<br>- Handle client-side validation<br>- Manage UI state and navigation |
| **Application Layer** | - FastAPI Routes/Controllers<br>- Authentication Endpoints (`/api/auth/*`)<br>- Resource Management Endpoints (`/api/resources/*`)<br>- Recommendation Endpoints (`/api/recommendations/*`)<br>- User Profile Endpoints (`/api/users/*`)<br>- Search Endpoints (`/api/search/*`)<br>- Request Validators<br>- Response Formatters | Contains REST API controllers that handle HTTP requests for authentication, resource management, and recommendation generation | - Route incoming HTTP requests to appropriate services<br>- Validate user input (emails, passwords, file uploads)<br>- Handle request/response formatting (JSON)<br>- Manage CORS and middleware<br>- Coordinate between business logic and presentation<br>- Handle error responses and status codes |
| **Service/Business Logic Layer** | - AuthenticationService (JWT, password hashing)<br>- ResourceService (upload, categorization, metadata extraction)<br>- RecommendationEngine (collaborative filtering, content-based filtering)<br>- UserPreferenceService (learning style tracking)<br>- SearchService (keyword matching, semantic search)<br>- NotificationService (study reminders, new resources)<br>- ActivityTrackingService (user behavior analytics) | Implements core domain logic for personalized study resource recommendations, user management, and intelligent resource discovery | - Enforce business rules (user roles, resource access)<br>- Execute recommendation algorithms<br>- Process resource metadata and tags<br>- Calculate similarity scores between resources<br>- Track user study patterns and preferences<br>- Generate personalized resource suggestions<br>- Manage user activity analytics |
| **Data Access Layer** | - SQLAlchemy ORM Models<br>- UserRepository (CRUD operations)<br>- ResourceRepository (resource storage/retrieval)<br>- RecommendationRepository (tracking, history)<br>- ActivityRepository (user interactions)<br>- Database Connection Manager<br>- Query Builders<br>- Transaction Handlers | Interfaces with PostgreSQL database through SQLAlchemy ORM to persist and retrieve user data, study resources, recommendations, and activity logs | - Execute SQL queries for data retrieval<br>- Persist user accounts, resources, and preferences<br>- Manage database transactions<br>- Handle data relationships (user-resource, resource-tags)<br>- Implement data validation constraints<br>- Perform joins for recommendation queries<br>- Maintain data integrity and foreign keys |

---

## 3. Component Responsibilities by Layer

### Presentation Layer Components

**React Frontend Application:**
- Render interactive UI for resource discovery and management
- Display personalized study resource recommendations
- Provide forms for user registration, login, and resource uploads
- Implement search and filtering interfaces for finding resources
- Show user dashboards with study progress and favorites
- Handle client-side routing and navigation

**Authentication UI:**
- Display login and registration forms with validation feedback
- Show error messages for invalid credentials
- Manage session state for logged-in users

**Resource Dashboard:**
- Display user's uploaded resources and favorites
- Show recommended resources based on user preferences
- Provide resource preview and download capabilities

---

### Application Layer Components

**Authentication Endpoints (`/api/auth/`):**
- `POST /register` - Handle new user registration requests
- `POST /login` - Authenticate users and issue JWT tokens
- `POST /logout` - Invalidate user sessions
- `GET /verify` - Verify JWT token validity

**Resource Management Endpoints (`/api/resources/`):**
- `POST /upload` - Accept and validate resource file uploads
- `GET /{resource_id}` - Retrieve specific resource details
- `PUT /{resource_id}` - Update resource metadata
- `DELETE /{resource_id}` - Remove resources
- `GET /user/{user_id}` - Get all resources uploaded by a user

**Recommendation Endpoints (`/api/recommendations/`):**
- `GET /personalized` - Generate personalized resource recommendations
- `GET /similar/{resource_id}` - Find similar study resources
- `GET /trending` - Get trending resources in user's field

**Request Validators:**
- Validate email format, password strength
- Check file types and sizes for uploads
- Ensure required fields are present in requests

---

### Service/Business Logic Layer Components

**AuthenticationService:**
- Hash passwords using bcrypt before storage
- Generate and validate JWT tokens for session management
- Implement role-based access control (student, instructor, tutor)
- Handle password reset and email verification logic

**ResourceService:**
- Process uploaded files (PDFs, documents, videos)
- Extract metadata (title, subject, difficulty level)
- Categorize resources by topic and course
- Generate tags for improved searchability
- Validate resource ownership and access permissions

**RecommendationEngine:**
- Implement collaborative filtering (user-based, item-based)
- Execute content-based filtering using resource attributes
- Calculate similarity scores between resources and users
- Generate personalized recommendation lists
- Weight recommendations by user study patterns and preferences

**UserPreferenceService:**
- Track user's preferred learning styles (visual, auditory, kinesthetic)
- Monitor resource interaction patterns (views, downloads, ratings)
- Update user preference profiles based on behavior
- Identify user's strong and weak subjects

**SearchService:**
- Perform keyword-based search across resources
- Implement semantic search for better relevance
- Apply filters (subject, difficulty, resource type)
- Rank search results by relevance and popularity

---

### Data Access Layer Components

**UserRepository:**
- `create_user(user_data)` - Insert new user records
- `get_user_by_email(email)` - Retrieve user by email
- `get_user_by_id(user_id)` - Retrieve user by ID
- `update_user(user_id, data)` - Update user information
- `delete_user(user_id)` - Remove user account

**ResourceRepository:**
- `create_resource(resource_data)` - Store new resource records
- `get_resource_by_id(resource_id)` - Retrieve resource details
- `get_resources_by_user(user_id)` - Get user's uploaded resources
- `get_resources_by_tags(tags)` - Search resources by tags
- `update_resource(resource_id, data)` - Update resource metadata
- `delete_resource(resource_id)` - Remove resource records

**RecommendationRepository:**
- `log_recommendation(user_id, resource_id, score)` - Track recommendations shown
- `get_recommendation_history(user_id)` - Retrieve past recommendations
- `update_recommendation_feedback(rec_id, feedback)` - Store user feedback

**ActivityRepository:**
- `log_activity(user_id, activity_type, resource_id)` - Record user actions
- `get_user_activity(user_id)` - Retrieve user interaction history
- `get_popular_resources()` - Query most accessed resources

**Database Connection Manager:**
- Establish and maintain PostgreSQL connections
- Handle connection pooling for performance
- Manage database session lifecycle
- Execute transaction rollbacks on errors

---

## 4. Data Flow Explanation

### Example Use Case: User Requests Personalized Study Recommendations

**Step-by-Step Data Flow:**

1. **Presentation Layer â†’ Application Layer**
   - User clicks "Get Recommendations" button in React dashboard
   - Frontend sends `GET /api/recommendations/personalized` request with JWT token
   - Request includes user ID extracted from token

2. **Application Layer Processing**
   - `RecommendationController` receives the request
   - Validates JWT token and extracts user identity
   - Checks user authorization (must be authenticated)
   - Forwards request to `RecommendationEngine` in Business Logic Layer

3. **Application Layer â†’ Business Logic Layer**
   - `RecommendationEngine.get_personalized_recommendations(user_id)` is called
   - Service retrieves user preferences from `UserPreferenceService`
   - Queries user activity history to understand past interactions

4. **Business Logic Layer â†’ Data Access Layer**
   - `UserRepository.get_user_by_id(user_id)` - Fetch user profile
   - `ActivityRepository.get_user_activity(user_id)` - Get interaction history
   - `ResourceRepository.get_all_resources()` - Retrieve available resources for comparison

5. **Data Access Layer â†’ Database**
   - SQLAlchemy ORM executes SQL queries:
     - `SELECT * FROM users WHERE id = ?`
     - `SELECT * FROM activities WHERE user_id = ? ORDER BY timestamp DESC`
     - `SELECT * FROM resources WHERE subject IN (user_interests)`
   - PostgreSQL returns result sets to Data Access Layer

6. **Data Access Layer â†’ Business Logic Layer**
   - Repositories return Python objects (User, Activity, Resource models)
   - `RecommendationEngine` receives structured data

7. **Business Logic Layer Processing**
   - Calculate similarity scores between user preferences and resources
   - Apply collaborative filtering algorithm using other users' behaviors
   - Rank resources by recommendation score
   - Filter out already viewed/downloaded resources
   - Select top 10 recommendations

8. **Business Logic Layer â†’ Application Layer**
   - Return list of recommended resources with scores
   - `RecommendationController` receives processed recommendations

9. **Application Layer â†’ Presentation Layer**
   - Format response as JSON:
     ```json
     {
       "recommendations": [
         {
           "resource_id": 123,
           "title": "Calculus Study Guide",
           "score": 0.95,
           "reason": "Based on your interest in Mathematics"
         },
         ...
       ]
     }
     ```
   - Send HTTP 200 response to frontend

10. **Presentation Layer Display**
    - React receives JSON response
    - Updates component state with recommendations
    - Renders resource cards with titles, scores, and reasons
    - User sees personalized study recommendations on screen

---

### Example Use Case: User Uploads a Study Resource

**Step-by-Step Data Flow:**

1. **Presentation Layer â†’ Application Layer**
   - User fills upload form (file, title, subject, tags)
   - Frontend sends `POST /api/resources/upload` with multipart/form-data
   - Includes JWT token for authentication

2. **Application Layer Processing**
   - `ResourceController` validates file type and size
   - Checks JWT token and user permissions
   - Forwards to `ResourceService`

3. **Business Logic Layer Processing**
   - `ResourceService.process_upload()`:
     - Save file to storage system
     - Extract metadata (page count, keywords)
     - Auto-generate tags using NLP
     - Validate resource completeness

4. **Data Access Layer Operations**
   - `ResourceRepository.create_resource()`:
     - Insert record into `resources` table
     - Link resource to user via foreign key
     - Store file path and metadata

5. **Database Transaction**
   - PostgreSQL executes INSERT statement
   - Returns new resource ID
   - Commits transaction

6. **Response Flow Back**
   - Data Access â†’ Business Logic: Resource object with ID
   - Business Logic â†’ Application: Success confirmation
   - Application â†’ Presentation: JSON response with resource details
   - Presentation: Display success message and show uploaded resource

---

## 5. Justification for Layered Architecture

The Layered (N-Tier) Architecture is ideal for the Smart Study Resource Recommender because:

**Separation of Concerns:** Each layer has a distinct responsibility, making the codebase easier to understand and maintain. The presentation layer focuses solely on UI, while business logic handles recommendation algorithms independently of how data is displayed or stored.

**Scalability:** The architecture allows individual layers to scale independently. If recommendation processing becomes computationally intensive, we can scale the business logic layer horizontally without affecting the presentation or data layers. Similarly, we can add read replicas to the database layer without modifying application code.

**Maintainability:** Changes to one layer have minimal impact on others. If we switch from React to Vue.js in the presentation layer, the API endpoints and business logic remain unchanged. If we migrate from PostgreSQL to MongoDB, only the data access layer needs modification.

**Testability:** Each layer can be tested in isolation using mock objects. We can unit test recommendation algorithms in the business logic layer without requiring a database or frontend. Integration tests can verify layer interactions systematically.

**Team Collaboration:** Different team members can work on different layers simultaneously without conflicts. Frontend developers can work on React components while backend developers implement recommendation algorithms, coordinating only through the defined API contracts.

**Reusability:** Business logic and data access layers can be reused across multiple interfaces. The same recommendation engine can serve web, mobile, and desktop clients through the application layer's REST API.

**Security:** The layered approach enforces security boundaries. User authentication happens at the application layer, authorization rules are enforced in the business logic layer, and the data access layer prevents SQL injection through parameterized queries. No layer can be bypassed to access sensitive data.

---