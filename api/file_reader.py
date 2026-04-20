# api/file_reader.py - Version améliorée pour PDFs
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO
import re

def read_file(file_bytes: bytes, filename: str) -> str:
    """
    Lit un fichier (PDF, DOCX, TXT) et retourne son contenu texte.
    Version améliorée pour les PDFs complexes.
    """
    if filename.endswith(".pdf"):
        return read_pdf_enhanced(file_bytes)
    
    elif filename.endswith(".docx"):
        doc = Document(BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    
    elif filename.endswith(".txt"):
        return file_bytes.decode("utf-8")
    
    else:
        raise ValueError(f"Format non supporté : {filename}")


def read_pdf_enhanced(file_bytes: bytes) -> str:
    """
    Extrait le texte d'un PDF avec meilleure préservation des phrases.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    all_text = []
    
    for page_num, page in enumerate(doc):
        # Extraire le texte de la page
        text = page.get_text()
        
        if text.strip():
            # Nettoyer le texte
            text = clean_pdf_text(text)
            all_text.append(text)
        else:
            # Si pas de texte, essayer d'extraire avec un autre paramètre
            text = page.get_text("words")
            if text:
                # Reconstruire des phrases à partir des mots
                words = [w[4] for w in text if w[4].strip()]
                text = " ".join(words)
                text = clean_pdf_text(text)
                all_text.append(text)
    
    doc.close()
    
    # Fusionner toutes les pages
    full_text = "\n\n".join(all_text)
    
    # Vérifier si l'extraction a fonctionné
    if len(full_text) < 100:
        # Essayer une autre méthode
        return read_pdf_alternative(file_bytes)
    
    return full_text


def read_pdf_alternative(file_bytes: bytes) -> str:
    """
    Méthode alternative d'extraction PDF.
    """
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text_pages = []
    
    for page in doc:
        # Extraire les blocs de texte
        blocks = page.get_text("dict")
        page_text = []
        
        for block in blocks.get("blocks", []):
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["text"].strip():
                            page_text.append(span["text"])
        
        if page_text:
            text_pages.append(" ".join(page_text))
        else:
            # Fallback
            text_pages.append(page.get_text())
    
    doc.close()
    
    result = "\n\n".join(text_pages)
    
    # Dernier nettoyage
    result = re.sub(r'(\w)\s+(\w)', r'\1 \2', result)  # Corriger les espaces entre lettres
    result = re.sub(r'\s+', ' ', result)  # Normaliser les espaces
    result = re.sub(r'\.\s*\.\s*\.', '.', result)  # Corriger les points multiples
    
    return result


def clean_pdf_text(text: str) -> str:
    """
    Nettoie le texte extrait d'un PDF.
    """
    # Supprimer les en-têtes/pieds de page trop courts
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        # Garder les lignes de plus de 20 caractères (sauf si chiffres)
        if len(line) > 20 or re.search(r'\d{4}', line):
            cleaned_lines.append(line)
        elif re.search(r'[A-Z]{4,}', line):  # Garder les mots en majuscules (titres)
            cleaned_lines.append(line)
    
    text = '\n'.join(cleaned_lines)
    
    # Nettoyer les caractères spéciaux
    text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\%\€\$\d]', ' ', text)
    
    # Corriger les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    
    # Restaurer les retours à la ligne après les points
    text = re.sub(r'(?<=[.!?])\s+(?=[A-ZÀ-Ü])', '\n', text)
    
    return text


def extract_sentences_from_pdf(text: str) -> list:
    """
    Extrait des phrases cohérentes du texte PDF.
    """
    # Découper par points, points d'interrogation, points d'exclamation
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ü"\'])', text)
    
    # Filtrer les phrases trop courtes ou trop longues
    valid_sentences = []
    for sent in sentences:
        sent = sent.strip()
        if 30 < len(sent) < 500:
            valid_sentences.append(sent)
    
    return valid_sentences


# Fonction de test rapide
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'rb') as f:
            content = f.read()
            text = read_file(content, sys.argv[1])
            print(f"Texte extrait ({len(text)} caractères):")
            print(text[:1000])