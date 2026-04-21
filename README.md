# AI Résumeur de Documents

Projet IA — Résumé automatique de documents via un pipeline NLP et une API REST.

---

## Architecture

```
Document (PDF/DOCX/TXT)
                      ↓
Frontend React (port 5173)
• Upload + instructions
• Choix : Extractif / Abstractif
                       ↓ POST /summarize
API FastAPI (port 8000)
• Lecture fichier → file_reader
• Détection type → detect_doc_type
                       ↓
┌──────────────────────┴──────────────────────┐
↓                                            ↓
【EXTRACTIF】                        【ABSTRACTIF】
api/summarizer.py              src/summarize.py
• score_sentences()       • chunk_text_by_paragraphs()
• extractive_summary()        • summarize_chunks()
• apply_user_constraints()    • Groq (LLaMA 3.3 70B)
↓                                     ↓
└──────────────┬───────────────────────┘
↓
format_summary.py
↓
Résumé final
```

---

## Équipe

| Personne | Rôle | Dossier |
|---|---|---|
| Walae | Pipeline NLP | `src/` |
| Wissal | API REST + Docker | `api/` |
| Yousra | Frontend React | `frontend/` |

---

## Installation

### 1. Cloner le repo
```bash
git clone https://github.com/ouazzanitaybiwalae/AI_Agent_Resume_Docs.git
cd AI_Agent_Resume_Docs
```

### 2. Créer le fichier `.env`
```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxxx
```

### 3. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 4. Lancer l'API
```bash
uvicorn api.main:app --reload --port 8000
```

### 5. Lancer le frontend
```bash
cd frontend
npm install
npm run dev
```

L'app est accessible sur `http://localhost:5173`

---

## Lancement avec Docker

```bash
docker-compose up --build
```

- API : `http://localhost:8000`
- Frontend : `http://localhost:5173`
---

## Tests

```bash
pytest tests/test_pipeline.py -v
```

---

## Formats supportés

- PDF (texte extractible)
- DOCX (Word)
- TXT / Markdown

## Types de documents

- Rapport financier / annuel
- Article scientifique
- Compte-rendu de réunion
- Contrat juridique
- Transcription audio/vidéo
- Documentation technique
