#!/bin/bash

# Kill existing Gunicorn process
pkill -f gunicorn

# Reload Nginx configuration
sudo nginx -s reload

# Start Gunicorn
source venv/bin/activate
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app 