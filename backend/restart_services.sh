#!/bin/bash

# Kill existing Gunicorn process more aggressively
pkill -9 -f gunicorn

# Wait for port to be released
sleep 2

# Reload Nginx configuration
sudo nginx -s reload

# Start Gunicorn
cd /home/exp/aiservice/backend
source venv/bin/activate

# Install required packages
pip install gunicorn flask flask-cors python-dotenv openai

# Set Python path and start server
export PYTHONPATH=$PYTHONPATH:/home/exp/aiservice/backend
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 "app:create_app()" 