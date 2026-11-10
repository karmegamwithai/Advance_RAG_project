from flask import current_app
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError

mongo_client = None
db = None
users_collection = None
documents_collection = None
chunks_collection = None

def init_mongo(app):
    global mongo_client, db, users_collection, documents_collection, chunks_collection

    uri = app.config.get("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is missing. Add it to your .env file.")

    mongo_client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    mongo_client.admin.command("ping")

    db = mongo_client[app.config["DATABASE_NAME"]]
    users_collection = db["users"]
    documents_collection = db["documents"]
    chunks_collection = db["document_chunks"]

    users_collection.create_index("email", unique=True)
    documents_collection.create_index([("user_id", ASCENDING), ("created_at", -1)])
    chunks_collection.create_index([("user_id", ASCENDING), ("document_id", ASCENDING)])
    app.logger.info("Connected to MongoDB Atlas")

def get_db():
    if db is None:
        raise RuntimeError("MongoDB has not been initialized.")
    return db
