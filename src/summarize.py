import os
from typing import List
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """Tu es un assistant expert en résumé de documents.
Ton rôle est de produire des résumés fidèles, concis et structurés.
Tu ne dois jamais inventer d'informations absentes du texte source.
Réponds toujours dans la même langue que le document fourni."""


def build_summary_prompt(chunk: str, doc_type: str = "général", instructions: str = "") -> str:
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
    prompt = build_summary_prompt(chunk, doc_type, instructions)

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()


def summarize_chunks(
    chunks: List[str],
    doc_type: str = "général",
    instructions: str = "",
    max_tokens_per_chunk: int = 500,
    verbose: bool = True,
) -> List[str]:
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