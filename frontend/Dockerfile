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
