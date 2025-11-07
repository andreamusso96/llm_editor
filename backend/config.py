import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

# Get database configuration from environment variables
DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_HOST = os.getenv('POSTGRES_HOST')
DB_PORT = os.getenv('POSTGRES_PORT')
DB_NAME = os.getenv('POSTGRES_DB')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

print(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, GOOGLE_API_KEY)

# Construct database URL with psycopg2 adapter
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

LLM_MODEL_NAME = "gemini-2.5-pro" # This is likely the best model for this task.
# LLM_MODEL_NAME="gemini-2.5-flash-preview-05-20"
# LLM_MODEL_NAME="gemini-1.5-flash-8b" # This is the cheapest model.