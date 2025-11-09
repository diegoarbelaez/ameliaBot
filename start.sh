#!/bin/bash

# BotDO - Quick Start Script
# This script validates environment and starts the application

set -e  # Exit on error

echo "================================"
echo "🚀 BotDO Application Starter"
echo "================================"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo ""
    echo "📝 Please create your .env file first:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    echo ""
    echo "📖 See documentation/ENV_SETUP.md for detailed instructions"
    exit 1
fi

echo "✅ Found .env file"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Validate environment variables
echo "🔍 Validating environment variables..."
echo ""

if command -v python3 &> /dev/null; then
    python3 backend/validate_env.py
    validation_result=$?
elif command -v python &> /dev/null; then
    python backend/validate_env.py
    validation_result=$?
else
    echo "⚠️  Warning: Python not found, skipping validation"
    echo "   Environment validation will happen when starting the backend"
    validation_result=0
fi

if [ $validation_result -ne 0 ]; then
    echo ""
    echo "❌ Environment validation failed!"
    echo "Please fix the errors above before starting the application."
    exit 1
fi

echo ""
echo "================================"
echo "🎯 Starting Docker services..."
echo "================================"
echo ""

# Start docker-compose
docker-compose up --build

# This will run until stopped with Ctrl+C

