# ===========================================
# BACKEND DOCKERFILE (FastAPI + Uvicorn)
# ===========================================

# Use lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED 1

# Install system dependencies needed for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# Copy all backend files into image
COPY . /app

# Expose FastAPI port
EXPOSE 8000

# Run the backend API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]