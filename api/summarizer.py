import os
from dotenv import load_dotenv

load_dotenv()

def summarize_text(text: str) -> str:
    # Résumé simple en attendant de brancher Claude ou OpenAI
    words = text.split()
    if len(words) <= 100:
        return text
    return " ".join(words[:100]) + "..."