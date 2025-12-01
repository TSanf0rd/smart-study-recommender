from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
import os

#Initialization of FastAPI applicaiton (Turning the Server on)
#  When you run this and visit http://localhost:8000/api/docs, you will see the API documentation.
app = FastAPI(
    title="Smart Study Recommender API",
    description="AI-powered study resource recommendation system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

#CORS Configuration (Cross-Origin Resource Sharing)
# By default, the API only allows requests from the frontend running on http://localhost:3000.
# You can set the FRONTEND_URL environment variable to allow requests from other domains.
# By default, browsers say "No way! These are different origins - I won't let them talk!" This is a security feature, but it breaks your app
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True, # Can send cookies/auth tokens
    allow_origins=[frontend_url, "http://localhost:3000"], # Which websites are allowed to talk to your API
    allow_methods=["*"], # Which HTTP methods (GET, POST, PUT, DELETE, etc.) are allowed [*] means all methods
    allow_headers=["*"], # Which custom headers are allowed
)

#Temportary Data Storage (In-Memory)
# Structure: {email: user_data}
# user_data: {id: int, name: str, email: EmailStr, password: str, created_at: datetime, updated_at: datetime}
users_db: Dict[str, dict] = {}
# This data disappears when the server stops/restarts. In Sprint 2 will add PostgreSQl for permanent storate

#Pydantic Models (Data Visualization) Blueprints or contracts for the data
# 1. Define what the data looks like - what fields are required, what data types are allowed
# 2. Validate automatically - if someone tries to send data that doesn't match the rules, it will raise an error - Pydantic rejects it
# 3. Generate documentation - FastAPI uses these to create the interactive docs page


class UserRegister(BaseModel):
    username:str
    email: EmailStr
    password: str
    role: Optional[str] = "student" # student, instructor, tutor

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "passoword": "securepassword123",
                "role": "student"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    passoword: str

    class Conflig:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "password": "securepassword123"
            }
        }

class UserResponse(BaseModel):
    username: str
    email: str
    role: str
    created_at: str


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return{
        "message": "Smart Study Resource Recommender API",
        "version": "0.1.0",
        "status": "running",
        "documentation": "/api/docs"
    }

# Health Check endpoint
# Are you Alice and Working?
# Front-end will display "Connected" or "Disconnected"
# React frontend checks if the backend is Running
# Monoitoring tools can ping if the server crashed 
# Gives debugging info (how many users, is DB connected)
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "users_registered": len(users_db),
        "database_connected": False # Will be true when we connect to PostgresSQL
    }

# User Registration endpoint
# @app.post(...): This endpoint accepts POST requests (used for creating/submitting data)
# "/api/auth/register": The URL path
# response_model=UserResponse: Tells FastAPI what data structure to return (and validates it)
# status_code=status.HTTP_201_CREATED: Returns HTTP 201 (standard for "successfully created something")
@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserRegister): # FastAPI automatically parses the JSON request body into a UserRegister object
    """
    Register a new user

    -**username**: Unique username
    -**email**: Valid email address
    -**password**: User password (will be hashed in Sprint 2)
    -**role**: User role(student, instructor, tutor)
    """
    # Check if user already exists, if email already a key, raise an error
    if user.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exits :( whop-whop"
        )
    
    # Check if username is taken
    # Looks through all users to see if anyone has that username 
    for existing_user in users_db.values():
        if existing_user["username"] == user.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                details="Username already taken :( choose another one"
            )

    # Validate role
    # Makes sure they picked a valid role
    valid_roles = ["student", "instructor", "tutor"]
    if user.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            details=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Create user (In Sprint 2, we'll hash the password and save to database)
    # Creates user dictionary and stores it with email as the key
    user_data ={
        "username": user.username,
        "email": user.email,
        "password": user.password, # WARNING NO PLAIN TEXT PASSWORDS in production
        "role": user.role,
        "created_at": datetime.now().isoformat()

    }

    users_db[user.email] = user_data

    # Return user info (without password)
    return UserResponse(
        username=user_data["username"],
        email=user_data["email"],
        role=user_data["role"],
        created_at=user_data["created_at"]
    )

# User Login endpoint
# 1. Takes an email and Password from the request
# 2. Checks passwords 
# 3. Compares passwords 
# 4. Returns user info on success
# Secure Note: Notice it says "Invalid email or password" for both cases. You never want to say "Email doesn't exist" because that helps hackers figure out which emails are registered!

@app.post("/api/auth/login")
async def login_user(credentials: UserLogin):
    """
    Login user
    
    - **email**: User's email
    - **password**: User's password
    
    Returns user information on successful login
    """
    # Check if user exists
    if credentials.email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user = users_db[credentials.email]
    
    # Check password (In Sprint 2, we'll use proper password hashing)
    if user["password"] != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Return success with user info (In Sprint 2, we'll return a JWT token)
    return {
        "message": "Login successful",
        "user": {
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"]
        }
    }

# Get all users (for testing - will be removed or restricted in Sprint 2)
@app.get("/api/users")
async def get_users():
    """Get all registered users (for testing purposes)"""
    users_list = []
    for user in users_db.values():
        users_list.append({
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"]
        })
    return {"users": users_list, "total": len(users_list)}

# Run the application
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True  # Auto-reload on code changes
    )