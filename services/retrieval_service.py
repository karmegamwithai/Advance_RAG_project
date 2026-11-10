from flask import current_app
from services import mongodb_service
from services.embedding_service import generate_embedding

def retrieve_chunks(api_key: str, user_id: str, question: str,
                    document_id: str | None = None, limit: int = 5):
    query_vector = generate_embedding(api_key, question, purpose="query")

    vector_stage = {
        "index": current_app.config["VECTOR_INDEX_NAME"],
        "path": "embedding",
        "queryVector": query_vector,
        "numCandidates": max(limit * 20, 100),
        "limit": limit,
        "filter": {"user_id": user_id},
    }
    if document_id:
        vector_stage["filter"]["document_id"] = document_id

    pipeline = [
        {"$vectorSearch": vector_stage},
        {"$project": {
            "_id": 0,
            "document_id": 1,
            "filename": 1,
            "content": 1,
            "page_number": 1,
            "score": {"$meta": "vectorSearchScore"},
        }},
    ]
    return list(mongodb_service.chunks_collection.aggregate(pipeline))
