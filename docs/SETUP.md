# Setup Instructions

## Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 16+** and npm (for frontend)
- **Docker & Docker Compose** (optional, recommended for easy setup)
- **Git** (for version control)

---

## Quick Start with Docker (Recommended)

This is the easiest way to get everything running:

```bash
# Clone the repository
git clone https://github.com/YOUR-USERNAME/smart-study-recommender.git
cd smart-study-recommender

# Start all services (database, backend, frontend)
docker-compose up --build
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs
- PostgreSQL: localhost:5432

**Stop all services:**
```bash
docker-compose down
```

---

## Manual Setup (Without Docker)

### Step 1: Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (copy from .env.example)
cp .env.example .env

# Run the backend
python main.py
```

Backend will be running at: **http://localhost:8000**

---

### Step 2: Frontend Setup

```bash
# Open a new terminal
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

Frontend will be running at: **http://localhost:3000**

---

### Step 3: Database Setup (Optional for Sprint 1)

For Sprint 1, we're using in-memory storage, so no database is required yet.

For Sprint 2, we'll set up PostgreSQL:

```bash
# Using Docker for PostgreSQL only
docker run -d \
  --name study_recommender_db \
  -e POSTGRES_DB=study_recommender \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  ankane/pgvector:latest
```

---

## Verification Steps

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-XX...",
  "users_registered": 0,
  "database_connected": false
}
```

### 2. Check Frontend

Open your browser and navigate to http://localhost:3000

You should see the Smart Study Resource Recommender login page.

### 3. Test Authentication

1. Click on "Register"
2. Fill in the form:
   - Username: testuser
   - Email: test@example.com
   - Password: password123
   - Role: Student
3. Click "Register"
4. Switch to "Login"
5. Enter the same credentials
6. You should see a welcome dashboard

---

## API Endpoints (Sprint 1)

### Health Check
```
GET /api/health
```

### Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword",
  "role": "student"
}
```

### Login User
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepassword"
}
```

### Get All Users (Testing Only)
```
GET /api/users
```

---

## Troubleshooting

### Backend won't start
- **Error: "Port 8000 already in use"**
  - Solution: Kill the process using port 8000 or change the port in `.env`
  
- **Error: "ModuleNotFoundError"**
  - Solution: Make sure virtual environment is activated and dependencies are installed

### Frontend won't start
- **Error: "Port 3000 already in use"**
  - Solution: Kill the process or set a different port: `PORT=3001 npm start`
  
- **Error: "Cannot GET /api/..."**
  - Solution: Make sure backend is running on port 8000

### Docker issues
- **Error: "Cannot connect to Docker daemon"**
  - Solution: Make sure Docker Desktop is running

- **Services won't start**
  - Solution: Try `docker-compose down -v` then `docker-compose up --build`

---

## Development Workflow

### Making changes to backend:
1. Edit files in `backend/`
2. The server auto-reloads (if running with `--reload`)
3. Test at http://localhost:8000/api/docs

### Making changes to frontend:
1. Edit files in `frontend/src/`
2. React automatically reloads in the browser
3. Check browser console for errors

### Committing changes:
```bash
# Always work on development branch
git checkout development

# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: Add user registration validation"

# Push to GitHub
git push origin development
```


## Next Steps (Sprint 2)

- [ ] Connect to PostgreSQL database
- [ ] Implement proper password hashing
- [ ] Add JWT token authentication
- [ ] Create database models
- [ ] Implement file upload functionality
- [ ] Add user profile management

---

## Support

If you encounter issues:
1. Check this documentation
2. Review error messages carefully
3. Check GitHub Issues
4. Ask your team members
5. Contact the instructor

---

**Team 24**: Tyler Sanford, Josh England, Kendric Jones  
**Last Updated**: Sprint 1 - Week 2