from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from config import set_user_gemini_key, delete_user_gemini_key
from services.gemini_service import get_gemini_client

settings_bp = Blueprint("settings", __name__)

@settings_bp.post("/gemini-key")
@login_required
def save_gemini_key():
    data = request.get_json(silent=True) or {}
    api_key = (data.get("api_key") or "").strip()
    if not api_key:
        return jsonify({"error": "api_key is required."}), 400
    try:
        client = get_gemini_client(api_key)
        # Validate the key with a small embedding request.
        client.models.embed_content(
            model="gemini-embedding-2",
            contents="API key validation",
        )
        set_user_gemini_key(session["user_id"], api_key)
        return jsonify({
            "message": "Gemini API key validated and stored in server memory for this session."
        })
    except Exception as exc:
        return jsonify({"error": f"Gemini key validation failed: {str(exc)}"}), 400

@settings_bp.delete("/gemini-key")
@login_required
def remove_gemini_key():
    delete_user_gemini_key(session["user_id"])
    return jsonify({"message": "User-supplied Gemini key removed."})
