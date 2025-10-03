#!/bin/bash
# Production Deployment Script for AI Assistant Platform

set -e

echo "🚀 Starting production deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build and start services
echo "📦 Building Docker images..."
docker-compose build

echo "🔄 Starting services..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 30

# Check health
echo "🏥 Checking service health..."
if curl -f http://localhost:8004/api/system/health > /dev/null 2>&1; then
    echo "✅ API service is healthy"
else
    echo "❌ API service is not responding"
    docker-compose logs ai-assistant-api
    exit 1
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend service is healthy"
else
    echo "❌ Frontend service is not responding"
    docker-compose logs frontend
    exit 1
fi

echo "🎉 Production deployment completed successfully!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 API: http://localhost:8004"
echo "📊 Health: http://localhost:8004/api/system/health"
