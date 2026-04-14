import os
from typing import List
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """Tu es un assistant expert en synthèse de documents.
Tu reçois plusieurs résumés partiels d'un même document.
Ton rôle est de les fusionner en un résumé final unique, cohérent, sans répétition et bien structuré.
Tu ne dois jamais inventer d'informations. Réponds dans la même langue que les résumés."""


def build_merge_prompt(
    summaries: List[str],
    doc_type: str = "général",
    instructions: str = "",
    output_format: str = "structuré",
) -> str:
    summaries_text = "\n\n".join(
        [f"--- Résumé partiel {i+1} ---\n{s}" for i, s in enumerate(summaries)]
    )
    format_instructions = {
        "paragraphe": "Rédige le résumé final sous forme de paragraphes fluides et cohérents.",
        "bullet": "Rédige le résumé final sous forme de liste de points clés (bullet points).",
        "structuré": "Rédige le résumé final avec des sections claires : Contexte, Points clés, Conclusion.",
    }
    format_text = format_instructions.get(output_format, format_instructions["paragraphe"])
    prompt = f"""Voici plusieurs résumés partiels d'un document de type "{doc_type}".
Fusionne-les en un seul résumé final complet, sans redondance et sans perte d'information importante.
{format_text}
"""
    if instructions:
        prompt += f"\nInstructions supplémentaires : {instructions}\n"
    prompt += f"\n{summaries_text}\n\n--- RÉSUMÉ FINAL ---"
    return prompt


def merge_summaries(
    summaries: List[str],
    doc_type: str = "général",
    instructions: str = "",
    output_format: str = "structuré",
    max_tokens: int = 1000,
    verbose: bool = True,
) -> str:
    if not summaries:
        return ""
    if len(summaries) == 1:
        if verbose:
            print("  Un seul chunk — pas de fusion nécessaire.")
        return summaries[0]
    if verbose:
        print(f"  Fusion de {len(summaries)} résumés partiels...")
    prompt = build_merge_prompt(summaries, doc_type, instructions, output_format)
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    final_summary = response.choices[0].message.content.strip()
    if verbose:
        print(f"  ✓ Résumé final généré ({len(final_summary)} caractères)")
    return final_summary


def run_full_pipeline(
    text: str,
    doc_type: str = "général",
    instructions: str = "",
    output_format: str = "structuré",
    verbose: bool = True,
) -> str:
    from src.chunk_text import chunk_text_by_paragraphs
    from src.summarize import summarize_chunks

    if verbose:
        print("Démarrage du pipeline...")
    chunks = chunk_text_by_paragraphs(text)
    if verbose:
        print(f"  → {len(chunks)} chunk(s) créé(s)")
    summaries = summarize_chunks(
        chunks,
        doc_type=doc_type,
        instructions=instructions,
        verbose=verbose,
    )
    final = merge_summaries(
        summaries,
        doc_type=doc_type,
        instructions=instructions,
        output_format=output_format,
        verbose=verbose,
    )
    if verbose:
        print("Pipeline terminé !")
    return final