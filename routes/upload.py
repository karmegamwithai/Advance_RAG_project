from flask import Blueprint, request, jsonify, session
from routes.auth import login_required
from config import get_user_gemini_key
from services.document_service import process_pdf

upload_bp = Blueprint("upload", __name__)

@upload_bp.post("/upload")
@login_required
def upload_document():
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        return jsonify({"error": "Choose a PDF file using the 'file' field."}), 400

    api_key = get_user_gemini_key(session["user_id"])
    if not api_key:
        return jsonify({"error": "Add your Gemini API key at POST /api/settings/gemini-key first."}), 400

    try:
        result = process_pdf(uploaded_file, session["user_id"], api_key)
        return jsonify({"message": "PDF indexed successfully.", **result}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        # Avoid returning secrets or internal stack traces to clients.
        return jsonify({"error": "PDF processing failed. Check the server log."}), 500
