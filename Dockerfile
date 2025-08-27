# Multi-stage Docker build for ChronoGuard Pro

# Backend Stage
FROM python:3.11-slim as backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY backend/ .

# Expose backend port
EXPOSE 8000

# Start command for backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Stage
FROM node:18-alpine as frontend-build

WORKDIR /app

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm install

# Copy frontend source code
COPY frontend/ .

# Build frontend
RUN npm run build

# Production Frontend Stage
FROM node:18-alpine as frontend

WORKDIR /app

# Copy built application
COPY --from=frontend-build /app/.next ./.next
COPY --from=frontend-build /app/package.json ./
COPY --from=frontend-build /app/node_modules ./node_modules

# Expose frontend port
EXPOSE 3000

# Start command for frontend
CMD ["npm", "start"]