# src/chunk_text.py
# Découpage intelligent du texte en chunks

import tiktoken
from typing import List


# Modèle d'encodage utilisé par Claude (compatible cl100k_base)
ENCODING_MODEL = "cl100k_base"

# Taille maximale par chunk (en tokens) — laisser de la marge pour le prompt
MAX_TOKENS_PER_CHUNK = 3000

# Chevauchement entre chunks pour ne pas perdre le contexte
OVERLAP_TOKENS = 100


def count_tokens(text: str) -> int:
    """
    Compte le nombre de tokens dans un texte.

    Args:
        text: Le texte à analyser

    Returns:
        Nombre de tokens
    """
    enc = tiktoken.get_encoding(ENCODING_MODEL)
    return len(enc.encode(text))


def chunk_text(
    text: str,
    max_tokens: int = MAX_TOKENS_PER_CHUNK,
    overlap_tokens: int = OVERLAP_TOKENS,
) -> List[str]:
    """
    Découpe un texte long en chunks de taille contrôlée (en tokens).
    Utilise un chevauchement pour préserver le contexte entre les chunks.

    Args:
        text:           Le texte complet à découper
        max_tokens:     Nombre maximum de tokens par chunk
        overlap_tokens: Nombre de tokens de chevauchement entre chunks

    Returns:
        Liste de chunks (strings)
    """
    enc = tiktoken.get_encoding(ENCODING_MODEL)
    tokens = enc.encode(text)
    total_tokens = len(tokens)

    # Si le texte est déjà petit, pas besoin de découper
    if total_tokens <= max_tokens:
        return [text]

    chunks = []
    start = 0

    while start < total_tokens:
        end = min(start + max_tokens, total_tokens)

        # Décoder les tokens de ce chunk en texte
        chunk_tokens = tokens[start:end]
        chunk_text_decoded = enc.decode(chunk_tokens)
        chunks.append(chunk_text_decoded)

        # Avancer avec overlap pour ne pas perdre le contexte
        start += max_tokens - overlap_tokens

        # Eviter une boucle infinie si overlap >= max_tokens
        if overlap_tokens >= max_tokens:
            break

    return chunks


def chunk_text_by_paragraphs(
    text: str,
    max_tokens: int = MAX_TOKENS_PER_CHUNK,
) -> List[str]:
    """
    Découpe le texte en respectant les paragraphes (meilleure cohérence sémantique).
    Regroupe les paragraphes jusqu'à atteindre max_tokens.

    Args:
        text:       Le texte complet
        max_tokens: Taille maximale par chunk en tokens

    Returns:
        Liste de chunks cohérents sémantiquement
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current_chunk = []
    current_tokens = 0

    for paragraph in paragraphs:
        para_tokens = count_tokens(paragraph)

        # Si le paragraphe seul dépasse la limite, on le découpe par tokens
        if para_tokens > max_tokens:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = []
                current_tokens = 0
            # Découpage forcé du paragraphe trop long
            sub_chunks = chunk_text(paragraph, max_tokens=max_tokens)
            chunks.extend(sub_chunks)
            continue

        # Si ajouter ce paragraphe dépasse la limite, sauvegarder le chunk actuel
        if current_tokens + para_tokens > max_tokens:
            if current_chunk:
                chunks.append("\n\n".join(current_chunk))
            current_chunk = [paragraph]
            current_tokens = para_tokens
        else:
            current_chunk.append(paragraph)
            current_tokens += para_tokens

    # Ajouter le dernier chunk s'il reste quelque chose
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks if chunks else [text]


if __name__ == "__main__":
    # Test rapide
    sample_text = """
    Ceci est un texte de test pour vérifier le chunking.
    Il contient plusieurs paragraphes.

    Deuxième paragraphe avec du contenu supplémentaire.
    On veut vérifier que le découpage fonctionne bien.

    Troisième paragraphe pour allonger le texte.
    """ * 10  # Multiplier pour simuler un long document

    print(f"Tokens total : {count_tokens(sample_text)}")
    chunks = chunk_text_by_paragraphs(sample_text)
    print(f"Nombre de chunks : {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i+1} : {count_tokens(chunk)} tokens")