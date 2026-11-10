import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# For local development only: user-supplied keys are held in process memory,
# never in the Flask cookie or MongoDB. They are lost when the server restarts.
_USER_GEMINI_KEYS = {}

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "change-this-development-secret")
    MONGODB_URI = os.getenv("MONGODB_URI", "")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "rag_database")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-2")
    GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash")
    EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "768"))
    VECTOR_INDEX_NAME = os.getenv("VECTOR_INDEX_NAME", "rag_vector_index")
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024
    DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"

def set_user_gemini_key(user_id: str, api_key: str):
    _USER_GEMINI_KEYS[user_id] = api_key

def get_user_gemini_key(user_id: str) -> str:
    return _USER_GEMINI_KEYS.get(user_id) or Config.GEMINI_API_KEY

def delete_user_gemini_key(user_id: str):
    _USER_GEMINI_KEYS.pop(user_id, None)
