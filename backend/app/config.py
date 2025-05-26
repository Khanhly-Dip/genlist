import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    MODEL_NAME = os.getenv('MODEL_NAME', 'gpt-4o-mini')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', 2000))
    TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7)) 