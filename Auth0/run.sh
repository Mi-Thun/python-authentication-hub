#!/bin/bash

set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Check for .env file, create from example.env if missing
if [ ! -f ".env" ]; then
    if [ -f "example.env" ]; then
        cp example.env .env
        echo ".env file created from example.env."
    else
        echo "Error: .env file not found and example.env does not exist."
        exit 1
    fi
fi

# Export environment variables from .env
export $(grep -v '^#' .env | xargs)

# Run Flask app
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --port=7000
