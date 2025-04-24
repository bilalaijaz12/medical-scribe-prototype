import os

# API Keys
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
LLM_MODEL = os.environ.get('LLM_MODEL', 'anthropic/claude-3-opus-20240229')

# Flask Config
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
DEBUG = os.environ.get('FLASK_ENV') == 'development'

# Audio Config
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size