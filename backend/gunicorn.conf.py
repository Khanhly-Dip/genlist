import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Gunicorn config
bind = "0.0.0.0:5001"
workers = 4
worker_class = "sync"
timeout = 120
accesslog = "logs/access.log"
errorlog = "logs/error.log"
capture_output = True
enable_stdio_inheritance = True 