from google import genai
from google.genai import types
from flask import current_app

def get_gemini_client(api_key: str):
    if not api_key:
        raise ValueError("Gemini API key is missing. Add it in API settings.")
    return genai.Client(api_key=api_key)

def generate_answer(api_key: str, question: str, context: str) -> str:
    client = get_gemini_client(api_key)
    model = current_app.config["GEMINI_CHAT_MODEL"]

    prompt = f"""
You are a helpful document question-answering assistant.
Answer the user's question using only the supplied document context.
If the answer is not present in the context, say you could not find it in the uploaded documents.
Do not invent facts. Mention source filenames and page numbers when available.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}
"""
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.2),
    )
    return response.text or "I could not generate an answer."
