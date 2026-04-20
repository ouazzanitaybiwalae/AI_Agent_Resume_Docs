# src/merge.py - Version simplifiée
from typing import List

def merge_summaries(
    summaries: List[str],
    doc_type: str = "général",
    instructions: str = "",
    output_format: str = "structuré",
    verbose: bool = True,
) -> str:
    """Fusion simple : concatène et garde les lignes uniques."""
    if not summaries:
        return ""
    
    # Concaténer
    merged = "\n".join(summaries)
    
    # Garder les lignes uniques
    lines = merged.split("\n")
    seen = set()
    unique = []
    
    for line in lines:
        line_clean = line.strip()
        if line_clean and line_clean not in seen:
            seen.add(line_clean)
            unique.append(line)
    
    return "\n".join(unique)