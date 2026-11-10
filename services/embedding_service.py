from flask import current_app
from google.genai import types
from services.gemini_service import get_gemini_client

def generate_embedding(api_key: str, text: str, purpose: str = "document", title: str = ""):
    client = get_gemini_client(api_key)
    model = current_app.config["GEMINI_EMBEDDING_MODEL"]
    dimensions = current_app.config["EMBEDDING_DIMENSIONS"]

    # Gemini Embedding 2 uses task-oriented text prefixes in the input.
    if purpose == "query":
        prepared_text = f"task: question answering | query: {text}"
    else:
        prepared_text = f"title: {title or 'none'} | text: {text}"

    result = client.models.embed_content(
        model=model,
        contents=prepared_text,
        config=types.EmbedContentConfig(output_dimensionality=dimensions),
    )
    if not result.embeddings or not result.embeddings[0].values:
        raise RuntimeError("Gemini returned an empty embedding.")
    vector = result.embeddings[0].values
    if len(vector) != dimensions:
        raise RuntimeError(
            f"Embedding dimension mismatch: expected {dimensions}, received {len(vector)}"
        )
    return vector
