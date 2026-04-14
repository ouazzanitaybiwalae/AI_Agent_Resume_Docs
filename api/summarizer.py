import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Ajouter le dossier racine au path pour accéder à src/
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.merge import run_full_pipeline


def summarize_text(
    text: str,
    doc_type: str = "général",
    instructions: str = "",
    output_format: str = "structuré",
) -> str:
    return run_full_pipeline(
        text=text,
        doc_type=doc_type,
        instructions=instructions,
        output_format=output_format,
        verbose=True,
    )