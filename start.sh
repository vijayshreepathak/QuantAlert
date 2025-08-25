#!/bin/bash

echo "🚀 Starting QuantAlert System..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
fi

# Build and start services
echo "📦 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ QuantAlert is starting up!"
echo ""
echo "📋 Service URLs:"
echo "   API Documentation: http://localhost:8000/docs"
echo "   Health Check:      http://localhost:8000/health"
echo "   Email Testing:     http://localhost:8025"
echo ""
echo "📝 Next steps:"
echo "   1. Run tests:      python test_system.py"
echo "   2. View logs:      docker-compose logs -f"
echo "   3. Stop services:  docker-compose down"
echo ""
echo "🎯 Ready to create price alerts!"
