# src/merge.py
# Fusion des résumés locaux en un résumé final cohérent

import os
from typing import List
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-opus-4-5"

SYSTEM_PROMPT = """Tu es un assistant expert en synthèse de documents.
Tu reçois plusieurs résumés partiels d'un même document.
Ton rôle est de les fusionner en un résumé final unique, cohérent, sans répétition et bien structuré.
Tu ne dois jamais inventer d'informations. Réponds dans la même langue que les résumés."""


def build_merge_prompt(
    summaries: List[str],
    doc_type: str = "général",
    instructions: str = "",
    output_format: str = "paragraphe",
) -> str:
    """
    Construit le prompt pour fusionner les résumés partiels.

    Args:
        summaries:      Liste des résumés partiels
        doc_type:       Type de document original
        instructions:   Instructions utilisateur
        output_format:  Format souhaité : 'paragraphe', 'bullet', 'structuré'

    Returns:
        Prompt formaté
    """
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
    """
    Fusionne une liste de résumés partiels en un résumé final unique.

    Args:
        summaries:      Liste des résumés partiels
        doc_type:       Type de document
        instructions:   Instructions utilisateur
        output_format:  'paragraphe', 'bullet', ou 'structuré'
        max_tokens:     Longueur max du résumé final
        verbose:        Afficher la progression

    Returns:
        Résumé final (string)
    """
    if not summaries:
        return ""

    # Si un seul résumé, pas besoin de merger
    if len(summaries) == 1:
        if verbose:
            print("  Un seul chunk — pas de fusion nécessaire.")
        return summaries[0]

    if verbose:
        print(f"  Fusion de {len(summaries)} résumés partiels...")

    prompt = build_merge_prompt(summaries, doc_type, instructions, output_format)

    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    final_summary = response.content[0].text.strip()

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
    """
    Pipeline complet : chunk → summarize → merge.
    Fonction principale à appeler depuis l'API (Personne B).

    Args:
        text:           Texte complet du document
        doc_type:       Type de document
        instructions:   Instructions utilisateur
        output_format:  Format de sortie
        verbose:        Afficher la progression

    Returns:
        Résumé final
    """
    # Import ici pour éviter les imports circulaires
    from .chunk_text import chunk_text_by_paragraphs
    from .summarize import summarize_chunks

    if verbose:
        print("Démarrage du pipeline...")

    # Étape 1 : Découpage
    if verbose:
        print("Étape 1 : Découpage du texte...")
    chunks = chunk_text_by_paragraphs(text)
    if verbose:
        print(f"  → {len(chunks)} chunk(s) créé(s)")

    # Étape 2 : Résumé local
    if verbose:
        print("Étape 2 : Résumé de chaque chunk...")
    summaries = summarize_chunks(
        chunks,
        doc_type=doc_type,
        instructions=instructions,
        verbose=verbose,
    )

    # Étape 3 : Fusion
    if verbose:
        print("Étape 3 : Fusion des résumés...")
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


if __name__ == "__main__":
    # Test rapide
    test_summaries = [
        "L'IA est un domaine qui vise à simuler l'intelligence humaine via des algorithmes.",
        "Le machine learning permet aux systèmes d'apprendre sans être explicitement programmés.",
        "Les applications incluent la reconnaissance vocale, la vision par ordinateur et le NLP.",
    ]

    print("Test de merge_summaries...")
    result = merge_summaries(test_summaries, doc_type="article scientifique")
    print(f"\nRésumé final :\n{result}")