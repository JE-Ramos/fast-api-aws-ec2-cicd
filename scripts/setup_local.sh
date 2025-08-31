#!/bin/bash

echo "Setting up FastAPI local development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing application dependencies..."
pip install --upgrade pip
pip install -r app/requirements.txt
pip install pytest pytest-cov flake8 black

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env file with your AWS credentials"
fi

echo ""
echo "Setup complete! To run the application locally:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run the app: uvicorn app.main:app --reload --port 8000"
echo "3. Or use: make run"
echo ""
echo "Access the API at:"
echo "  - http://localhost:8000"
echo "  - API docs: http://localhost:8000/docs"
echo "  - ReDoc: http://localhost:8000/redoc"