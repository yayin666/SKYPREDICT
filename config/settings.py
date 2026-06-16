import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Config
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "skypredict")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Recommendation Thresholds
THRESHOLD_HIGH_LOAD_FACTOR = 0.85
THRESHOLD_LOW_LOAD_FACTOR = 0.60
THRESHOLD_HIGH_GROWTH = 0.10
THRESHOLD_DECLINING_GROWTH = 0.0
