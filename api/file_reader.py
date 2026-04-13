import fitz  # PyMuPDF
from docx import Document
from io import BytesIO

def read_file(file_bytes: bytes, filename: str) -> str:
    
    if filename.endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    
    elif filename.endswith(".docx"):
        doc = Document(BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    
    elif filename.endswith(".txt"):
        return file_bytes.decode("utf-8")
    
    else:
        raise ValueError(f"Format non supporté : {filename}")