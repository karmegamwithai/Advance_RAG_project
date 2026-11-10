from flask import Blueprint, request, jsonify, session, current_app
from routes.auth import login_required
from config import get_user_gemini_key
from services.retrieval_service import retrieve_chunks
from services.gemini_service import generate_answer

chat_bp = Blueprint("chat", __name__)

@chat_bp.post("/chat")
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    document_id = data.get("document_id")
    try:
        limit = max(1, min(int(data.get("limit", 5)), 10))
    except (TypeError, ValueError):
        return jsonify({"error": "limit must be an integer."}), 400

    if not question:
        return jsonify({"error": "question is required."}), 400

    api_key = get_user_gemini_key(session["user_id"])
    if not api_key:
        return jsonify({"error": "Add your Gemini API key at POST /api/settings/gemini-key first."}), 400

    try:
        matches = retrieve_chunks(
            api_key=api_key,
            user_id=session["user_id"],
            question=question,
            document_id=document_id,
            limit=limit,
        )
        if not matches:
            return jsonify({
                "answer": "I couldn't find relevant information in your uploaded documents.",
                "sources": [],
            })

        context_parts = []
        sources = []
        for item in matches:
            context_parts.append(
                f"Source: {item.get('filename')} | Page: {item.get('page_number')}\n"
                f"{item.get('content')}"
            )
            sources.append({
                "filename": item.get("filename"),
                "page_number": item.get("page_number"),
                "score": item.get("score"),
                "document_id": item.get("document_id"),
            })

        answer = generate_answer(
            api_key=api_key,
            question=question,
            context="\n\n---\n\n".join(context_parts),
        )
        return jsonify({"answer": answer, "sources": sources})
    except Exception:
        current_app.logger.exception("Chat request failed")
        return jsonify({"error": "Chat request failed. Check the server log."}), 500
