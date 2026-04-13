# src/summarize.py
# Résumé local de chaque chunk via l'API Anthropic (Claude)

import os
from typing import List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

# Client Anthropic
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Modèle Claude à utiliser
MODEL = "claude-opus-4-5"

# Prompt système pour le résumé
SYSTEM_PROMPT = """Tu es un assistant expert en résumé de documents.
Ton rôle est de produire des résumés fidèles, concis et structurés.
Tu ne dois jamais inventer d'informations absentes du texte source.
Réponds toujours dans la même langue que le document fourni."""


def build_summary_prompt(chunk: str, doc_type: str = "général", instructions: str = "") -> str:
    """
    Construit le prompt utilisateur pour résumer un chunk.

    Args:
        chunk:        Le texte du chunk à résumer
        doc_type:     Type de document (rapport, article, contrat, etc.)
        instructions: Instructions spécifiques de l'utilisateur

    Returns:
        Prompt formaté
    """
    base_prompt = f"""Voici un extrait d'un document de type "{doc_type}".
Résume cet extrait en identifiant les idées clés, les faits importants et les points essentiels.
Sois concis mais exhaustif sur les éléments importants.
"""
    if instructions:
        base_prompt += f"\nInstructions spécifiques : {instructions}\n"

    base_prompt += f"\n---\nEXTRAIT :\n{chunk}\n---\n\nRÉSUMÉ :"
    return base_prompt


def summarize_single_chunk(
    chunk: str,
    doc_type: str = "général",
    instructions: str = "",
    max_tokens: int = 500,
) -> str:
    """
    Résume un seul chunk via l'API Claude.

    Args:
        chunk:        Texte à résumer
        doc_type:     Type de document
        instructions: Instructions utilisateur optionnelles
        max_tokens:   Longueur max du résumé en tokens

    Returns:
        Résumé du chunk (string)
    """
    prompt = build_summary_prompt(chunk, doc_type, instructions)

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.content[0].text.strip()


def summarize_chunks(
    chunks: List[str],
    doc_type: str = "général",
    instructions: str = "",
    max_tokens_per_chunk: int = 500,
    verbose: bool = True,
) -> List[str]:
    """
    Résume une liste de chunks, un par un.

    Args:
        chunks:                Liste de chunks à résumer
        doc_type:              Type de document
        instructions:          Instructions utilisateur
        max_tokens_per_chunk:  Tokens max par résumé
        verbose:               Afficher la progression

    Returns:
        Liste de résumés locaux
    """
    summaries = []

    for i, chunk in enumerate(chunks):
        if verbose:
            print(f"  Résumé chunk {i+1}/{len(chunks)}...")

        summary = summarize_single_chunk(
            chunk,
            doc_type=doc_type,
            instructions=instructions,
            max_tokens=max_tokens_per_chunk,
        )
        summaries.append(summary)

        if verbose:
            print(f"  ✓ Chunk {i+1} résumé ({len(summary)} caractères)")

    return summaries


if __name__ == "__main__":
    # Test rapide
    test_chunk = """
    L'intelligence artificielle (IA) est un domaine de l'informatique qui vise à créer
    des systèmes capables de réaliser des tâches qui nécessitent normalement l'intelligence humaine.
    Ces tâches incluent la reconnaissance vocale, la prise de décision, la traduction entre langues,
    et la perception visuelle. L'IA moderne utilise principalement des techniques d'apprentissage
    automatique (machine learning) et d'apprentissage profond (deep learning) pour analyser
    de grandes quantités de données et améliorer ses performances au fil du temps.
    """

    print("Test de summarize_single_chunk...")
    result = summarize_single_chunk(test_chunk, doc_type="article scientifique")
    print(f"Résumé : {result}")