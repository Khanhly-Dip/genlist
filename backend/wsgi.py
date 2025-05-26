import os
import sys

# Add the backend directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(current_dir, '.env'))

# Import app after setting up paths
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001) 