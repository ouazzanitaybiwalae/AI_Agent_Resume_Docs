# api/main.py
from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
import sys
import os

# Ajouter le dossier api au path pour les imports
sys.path.append(os.path.dirname(__file__))

from file_reader import read_file  # ← maintenant fonctionne
from summarizer import summarize_text
from detect_doc_type import detect_doc_type
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello():
    return {"message": "API opérationnelle"}

@app.post("/summarize")
async def summarize(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form(None),
    instructions: Optional[str] = Form(""),
    output_format: Optional[str] = Form("structuré"),
):
    content = await file.read()
    try:
        text = read_file(content, file.filename)
    except ValueError as e:
        return {"error": str(e)}

    if not doc_type or doc_type == "général" or doc_type == "auto":
        doc_type = detect_doc_type(text)
        print(f"Type détecté : {doc_type}")

    summary = summarize_text(
        text=text,
        doc_type=doc_type,
        instructions=instructions,
        output_format=output_format,
    )

    return {
        "filename": file.filename,
        "doc_type": doc_type,
        "summary": summary,
        "status": "ok"
    }
    # Vérifier la qualité de l'extraction
    if file.filename.endswith(".pdf") and len(text) < 500:
        return {
            "filename": file.filename,
            "warning": "⚠️ L'extraction du PDF a échoué. Le document contient peut-être des images ou une mise en page complexe. Pour un meilleur résultat, convertissez le PDF en TXT.",
            "summary": "Impossible d'extraire le texte de ce PDF. Veuillez convertir le fichier en TXT.",
            "status": "warning"
        }
