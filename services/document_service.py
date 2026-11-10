from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from flask import current_app
from services import mongodb_service
from services.embedding_service import generate_embedding
from services.chunking_service import split_pages_into_chunks
from utils.pdf_loader import extract_pdf_pages
from utils.text_cleaner import clean_text

ALLOWED_EXTENSIONS = {"pdf"}

def process_pdf(file_storage, user_id: str, api_key: str):
    original_name = secure_filename(file_storage.filename or "")
    if not original_name or "." not in original_name:
        raise ValueError("Please select a PDF file.")
    extension = original_name.rsplit(".", 1)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Only PDF files are supported.")

    document_id = str(uuid4())
    user_folder = Path(current_app.config["UPLOAD_FOLDER"]) / user_id
    user_folder.mkdir(parents=True, exist_ok=True)
    saved_path = user_folder / f"{document_id}.pdf"
    file_storage.save(saved_path)

    try:
        pages = extract_pdf_pages(str(saved_path))
        for page in pages:
            page["text"] = clean_text(page["text"])

        chunks = split_pages_into_chunks(pages)
        if not chunks:
            raise ValueError("The PDF did not contain usable text.")

        now = datetime.now(timezone.utc)
        records = []
        for index, chunk in enumerate(chunks):
            vector = generate_embedding(
                api_key=api_key,
                text=chunk["content"],
                purpose="document",
                title=original_name,
            )
            records.append({
                "user_id": user_id,
                "document_id": document_id,
                "filename": original_name,
                "chunk_index": index,
                "content": chunk["content"],
                "page_number": chunk["page_number"],
                "embedding": vector,
                "created_at": now,
            })

        if records:
            mongodb_service.chunks_collection.insert_many(records)

        mongodb_service.documents_collection.insert_one({
            "document_id": document_id,
            "user_id": user_id,
            "filename": original_name,
            "page_count": len(pages),
            "chunk_count": len(records),
            "created_at": now,
            "status": "indexed",
        })

        return {
            "document_id": document_id,
            "filename": original_name,
            "page_count": len(pages),
            "chunk_count": len(records),
        }
    except Exception:
        saved_path.unlink(missing_ok=True)
        raise
