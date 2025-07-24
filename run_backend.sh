#!/bin/bash

# FastAPI Backend Runner Script
# This script sets up and runs the FastAPI backend server

set -e  # Exit on any error

echo "🚀 Starting FastAPI Backend..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python is not installed or not in PATH"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "🐍 Using Python: $($PYTHON_CMD --version)"

# Check if virtual environment exists, create if not
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash/MSYS)
    source "$VENV_DIR/Scripts/activate"
else
    # Linux/macOS
    source "$VENV_DIR/bin/activate"
fi

# Upgrade pip
# echo "⬆️  Upgrading pip..."
# pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

# Check if .env file exists, create a sample if not
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating sample .env file..."
    cat > .env << EOL
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Application Configuration
APP_NAME=FastAPI Backend
DEBUG=True
SECRET_KEY=your-secret-key-here-change-this-in-production

# Server Configuration
HOST=127.0.0.1
PORT=8000
EOL
    echo "📝 Sample .env file created. Please update it with your configuration."
fi

# Run the FastAPI server
echo "🌟 Starting FastAPI server..."
echo "📍 Server will be available at: http://127.0.0.1:8000"
echo "📖 API documentation at: http://127.0.0.1:8000/docs"
echo "🔍 Alternative docs at: http://127.0.0.1:8000/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with uvicorn directly or through main.py
if command -v uvicorn &> /dev/null; then
    uvicorn main:app --host 127.0.0.1 --port 8000 --reload
else
    # Fallback to running main.py directly
    $PYTHON_CMD main.py
fi
