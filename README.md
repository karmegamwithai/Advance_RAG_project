# Flask RAG

Flask + MongoDB Atlas Vector Search + Gemini Embedding 2 + Gemini chat generation.

## 1. Setup

```powershell
uv sync
Copy-Item .env.example .env
```

Edit `.env` with your MongoDB Atlas URI and a long random `FLASK_SECRET_KEY`.
Keep `.env` private. Do not commit it.

## 2. Create MongoDB Vector Search index

Create database `rag_database`, collection `document_chunks`, then create a Vector Search index named `rag_vector_index` using `vector-index.json`.
The index dimensions must match `EMBEDDING_DIMENSIONS` in `.env`.

## 3. Run

```powershell
uv run python app.py
```

## 4. API workflow

All routes except `/` and `/api/auth/register`, `/api/auth/login` require a logged-in session cookie.

Register:
```http
POST /api/auth/register
Content-Type: application/json

{"email":"you@example.com","password":"at-least-8-characters"}
```

Set the user's Gemini key:
```http
POST /api/settings/gemini-key
Content-Type: application/json

{"api_key":"YOUR_GEMINI_API_KEY"}
```

Upload a PDF using multipart/form-data, field name `file`:
```http
POST /api/upload
```

Ask a question:
```http
POST /api/chat
Content-Type: application/json

{"question":"Summarize the main topic","limit":5}
```

Optionally restrict retrieval to one uploaded document:
```json
{"question":"What is the conclusion?","document_id":"DOCUMENT_ID_FROM_UPLOAD"}
```

Logout:
```http
POST /api/auth/logout
```

## Notes

- The user-supplied Gemini key is held only in process memory for this starter project. It is not written to MongoDB or the browser cookie, and it is lost when the server restarts. This is suitable for local development only. For multi-worker or production deployment, use a proper encrypted secret store / KMS and authorization controls.
- The starter implements PDF text extraction, not OCR. Scanned PDFs need an OCR step.
- MongoDB Atlas Vector Search index creation is a one-time Atlas setup step; normal MongoDB indexes are created by the app.
- `gemini-embedding-2` is used for both document and query embeddings with the same 768-dimensional output.
- For production: set `FLASK_DEBUG=false`, use HTTPS, add CSRF protection for cookie-authenticated browser requests, rate-limit endpoints, add file malware scanning, and move long PDF ingestion into a background worker.
