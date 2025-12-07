<<<<<<< HEAD
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
=======
# ===========================================
# FRONTEND DOCKERFILE (React + Node.js)
# ===========================================

# Use Node 18
FROM node:18

# Create app directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY smart-study-ui/package*.json ./

# Install node modules
RUN npm install

# Copy all frontend code
COPY smart-study-ui/. .

# Expose port for React dev server
EXPOSE 3000

# Start React app
CMD ["npm", "start"]
>>>>>>> 4904945f7071cac7644f3f5d27ecec9cf8783f57
