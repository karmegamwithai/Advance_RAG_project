from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_pages_into_chunks(pages, chunk_size=1000, chunk_overlap=150):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    output = []
    for page in pages:
        page_text = (page.get("text") or "").strip()
        if not page_text:
            continue
        for piece in splitter.split_text(page_text):
            output.append({
                "content": piece,
                "page_number": page["page_number"],
            })
    return output
