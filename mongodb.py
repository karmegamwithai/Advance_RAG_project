
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "rag_database")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI is missing from .env")

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000
)

# Test MongoDB connection
client.admin.command("ping")

db = client[DATABASE_NAME]

# Collection for document chunks
chunks_collection = db["document_chunks"]

print("MongoDB connected successfully!")
