# Smart Study Resource Recommender 📚
## AI-Powered Personalized Learning Platform

**Team 24:** Tyler Sanford, Josh England, Kendric Jones  
**Course:** Software Engineering  
**Sprint:** 3 - Advanced Architecture Implementation  
**Status:**  Active Development

---

## Project Overview

The Smart Study Resource Recommender is an intelligent platform that helps students discover personalized study materials through AI-powered recommendations. The system uses advanced architectural patterns including CQRS (Command Query Responsibility Segregation) and Event-Driven Architecture to provide scalable, maintainable, and high-performance resource management.

### Key Features

- 🔐 **User Authentication** - Secure registration and login for students, instructors, and tutors
- 📤 **Resource Upload** - Upload and share study materials with automatic tagging
- 🎯 **Personalized Recommendations** - AI-powered suggestions based on learning preferences
- 📊 **Activity Tracking** - Comprehensive analytics on resource usage and engagement
- ⭐ **Rating System** - Community-driven quality assessment
- 🔔 **Event-Driven Processing** - Asynchronous notifications and updates

---

## 🏗️ Architecture

### Sprint 3 Architecture Highlights

Our system implements enterprise-grade architectural patterns:

#### **CQRS Pattern**
- Separate read and write operations for optimal performance
- Commands handle state changes (register, upload, rate)
- Queries handle data retrieval (profile, resources, recommendations)

#### **Event-Driven Architecture**
- Asynchronous event processing for scalability
- Loose coupling through publish-subscribe pattern
- 5 event types with multiple handlers each

#### **Layered N-Tier Design**
```
┌─────────────────────────────┐
│   Presentation Layer        │  React Frontend
├─────────────────────────────┤
│   Application Layer         │  FastAPI Routes
├─────────────────────────────┤
│   Business Logic Layer      │  Command/Query Handlers
├─────────────────────────────┤
│   Data Access Layer         │  Repositories
└─────────────────────────────┘
```

#### **Low-Cohesion Database**
- 14 independent tables across 5 domains
- No foreign key constraints for performance
- Application-layer data validation
- Mapping tables for relationships

---

## ✨ Sprint 3 Features

### Implemented Use Cases

1. **User Registration with Event Notification**
   - Multi-table user creation (auth, profile, preferences)
   - Automatic welcome email and analytics
   - Event-driven preference initialization

2. **Resource Upload with Auto-Tagging**
   - File upload and metadata management
   - NLP-based automatic tag generation
   - Asynchronous follower notifications

3. **View Resource with Activity Tracking**
   - Detailed view analytics (duration, device, session)
   - Real-time statistics updates
   - User preference learning

4. **Rate Resource with Stats Update**
   - 1-5 star rating system with reviews
   - Automatic average calculation
   - Owner notifications

5. **Generate Personalized Recommendations**
   - Hybrid recommendation algorithm
   - Content-based and collaborative filtering
   - Confidence scoring and explanations

### Design Patterns (10 Implemented)

**Creational:**
- Singleton (Event Bus)
- Factory (Command Creation)
- Builder (Multi-step Repository)

**Structural:**
- Repository (Data Access)
- Adapter (Database Interface)
- Facade (Handler Simplification)
- Decorator (Event Logging)

**Behavioral:**
- Command (CQRS Commands)
- Observer (Event Subscribers)
- Strategy (Recommendation Algorithms)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Installation

#### Backend Setup

```bash
# Clone repository
git clone https://github.com/[your-username]/smart-study-recommender.git
cd smart-study-recommender/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Frontend Setup

```bash
cd frontend
npm install
```

### Running the Application

#### Sprint 3: CQRS+EDA Implementation

```bash
# Terminal 1: Start CQRS/EDA Backend
cd backend
python cqrs_eda_implementation.py
```

Server runs at: **http://localhost:8000**  
API Docs: **http://localhost:8000/docs**

#### Sprint 1: Basic Authentication (Original)

```bash
# Terminal 1: Start Basic Backend
cd backend
python main.py

# Terminal 2: Start Frontend
cd frontend
npm start
```

Frontend: **http://localhost:3000**

---

## 🧪 Testing

### Run Test Suite

```bash
cd backend
bash test_cqrs_eda.sh
```

### Expected Output

```
==========================================
Testing CQRS+EDA Implementation
==========================================

1️⃣ Use Case 1: User Registration ✅
2️⃣ Use Case 2: Resource Upload ✅
3️⃣ Use Case 3: View Resource ✅
4️⃣ Use Case 4: Rate Resource ✅
5️⃣ Use Case 5: Generate Recommendations ✅

✅ All 5 Use Cases Tested Successfully!
```

### Manual Testing

**Test User Registration:**
```bash
curl -X POST http://localhost:8000/api/cqrs/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "secure123",
    "role": "student",
    "full_name": "Test User"
  }'
```

**Test Resource Upload:**
```bash
curl -X POST http://localhost:8000/api/cqrs/resources/upload \
  -F "title=Calculus Guide" \
  -F "description=Study notes" \
  -F "resource_type=pdf" \
  -F "difficulty_level=intermediate" \
  -F "uploader_user_id=user-123" \
  -F "file_name=calculus.pdf"
```

---

## 📡 API Endpoints

### CQRS Commands (Write Operations)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cqrs/auth/register` | POST | Register new user |
| `/api/cqrs/resources/upload` | POST | Upload resource |
| `/api/cqrs/resources/{id}/view` | POST | Log resource view |
| `/api/cqrs/resources/{id}/rate` | POST | Rate resource |
| `/api/cqrs/recommendations/generate` | POST | Generate recommendations |

### CQRS Queries (Read Operations)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cqrs/users/{id}` | GET | Get user profile |
| `/api/cqrs/resources/{id}` | GET | Get resource details |
| `/api/cqrs/events` | GET | Get event log |

### Basic Auth (Sprint 1)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Basic registration |
| `/api/auth/login` | POST | Basic login |
| `/api/users` | GET | List all users |
| `/api/health` | GET | Health check |

---

## 📁 Project Structure

```
smart-study-recommender/
├── backend/
│   ├── main.py                      # Sprint 1: Basic auth
│   ├── cqrs_eda_implementation.py   # Sprint 3: CQRS+EDA
│   ├── test_cqrs_eda.sh            # Test suite
│   ├── requirements.txt             # Python dependencies
│   └── Dockerfile                   # Backend container
├── frontend/
│   ├── src/
│   │   ├── App.js                   # Main React component
│   │   └── App.css                  # Styling
│   ├── package.json                 # Node dependencies
│   └── Dockerfile                   # Frontend container
├── docs/
│   ├── SPRINT_3_REPORT.md          # Comprehensive report
│   ├── CODE_REVIEW_CHECKLIST.md    # Quality checklist
│   ├── WEEK_3_ACTION_PLAN.md       # Day-by-day plan
│   ├── architecture_design.md       # Architecture docs
│   ├── database_design.md           # Database schema
│   ├── api_integration.md           # API documentation
│   └── use_case_implementation.md   # Use case details
├── .gitignore
└── README.md
```

---

## 🗄️ Database Design

### Low-Cohesion Schema (14 Tables)

**User Domain:**
- `users_auth` - Authentication credentials
- `users_profile` - User information
- `users_preferences` - Learning preferences

**Resource Domain:**
- `resources_metadata` - Resource information
- `resources_content` - File storage
- `resources_stats` - Usage statistics

**Activity Domain:**
- `activities_views` - View tracking
- `activities_downloads` - Download tracking
- `activities_ratings` - Ratings/reviews

**Recommendation Domain:**
- `recommendations_generated` - AI recommendations
- `recommendations_feedback` - User feedback

**Tag Domain:**
- `tags_master` - All available tags
- `mapping_resource_tags` - Resource-tag relationships
- `mapping_user_interests` - User interests

### Why Low-Cohesion?

- ✅ Better performance (no JOINs)
- ✅ Independent scaling per table
- ✅ Flexible schema evolution
- ✅ Optimized caching strategies

---

## 🎨 Tech Stack

### Backend
- **Framework:** FastAPI 0.104.1
- **Language:** Python 3.11
- **Validation:** Pydantic 2.5.0
- **Server:** Uvicorn 0.24.0
- **Future:** PostgreSQL, Redis, AWS S3

### Frontend
- **Framework:** React 18
- **Language:** JavaScript ES6+
- **Styling:** CSS3
- **Build:** npm/Create React App

### Architecture
- **Patterns:** CQRS, EDA, Repository, Command
- **Design:** Layered N-Tier
- **Database:** Low-Cohesion (14 tables)

---

## 📚 Documentation

- **[Sprint 3 Report](docs/SPRINT_3_REPORT.md)** - Comprehensive project report
- **[Architecture Design](docs/architecture_design.md)** - System architecture
- **[Database Design](docs/database_design.md)** - Low-cohesion schema
- **[API Integration](docs/api_integration.md)** - REST API documentation
- **[Use Cases](docs/use_case_implementation.md)** - CQRS+EDA use cases
- **[Code Review Checklist](docs/CODE_REVIEW_CHECKLIST.md)** - Quality guidelines
- **[Week 3 Plan](docs/WEEK_3_ACTION_PLAN.md)** - Development schedule

---

## 🔄 Development Workflow

### Branching Strategy

```bash
# Main branch - production-ready code
git checkout main

# Development branch - active development
git checkout development

# Feature branches
git checkout -b feature/new-feature
```

### Commit Convention

```bash
feat: Add new feature
fix: Bug fix
docs: Documentation update
refactor: Code refactoring
test: Add tests
```

### Sprint Releases

- **Sprint 1:** v0.1.0 - Basic Authentication
- **Sprint 2:** v0.2.0 - (Planned) Database Integration
- **Sprint 3:** v0.3.0 - CQRS+EDA Architecture ✅

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000
kill -9 [PID]

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Tests fail

```bash
# Ensure server is running
python cqrs_eda_implementation.py &

# Check server health
curl http://localhost:8000/

# Run tests again
bash test_cqrs_eda.sh
```

### Frontend issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Start development server
npm start
```

---

## 🚧 Roadmap

### Sprint 4 (Planned)
- [ ] PostgreSQL database integration
- [ ] JWT authentication
- [ ] Real file upload (AWS S3)
- [ ] ML-powered recommendations
- [ ] Advanced search with filters
- [ ] User profile management

### Sprint 5 (Planned)
- [ ] Real-time notifications
- [ ] Mobile responsive design
- [ ] Analytics dashboard
- [ ] Social features
- [ ] Study group creation
- [ ] Progress tracking

---

## 👥 Team

**Team 24:**
- **Tyler Sanford** - Architecture & Backend
- **Josh England** - Database & Testing
- **Kendric Jones** - Frontend & Integration

**Instructor:** [Instructor Name]  
**Course:** Software Engineering  
**Semester:** Fall 2025

---

## 📄 License

This project is developed for educational purposes as part of a software engineering course.

---

## 🙏 Acknowledgments

- FastAPI documentation and community
- React documentation
- Design Patterns: Gang of Four
- CQRS Journey by Microsoft
- Event-Driven Architecture resources

---

---

**Last Updated:** December 7, 2025  
**Version:** 0.3.0-sprint3  
**Status:** Active Development

---

## 🎯 Quick Links

- [📖 Sprint 3 Report](docs/SPRINT_3_REPORT.md)
- [🏗️ Architecture](docs/architecture_design.md)
- [🗄️ Database](docs/database_design.md)
- [📡 API Docs](http://localhost:8000/docs)
- [✅ Checklist](docs/CODE_REVIEW_CHECKLIST.md)
