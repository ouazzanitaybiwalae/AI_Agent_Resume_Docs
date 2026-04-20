# api/detect_doc_type.py
def detect_doc_type(text: str) -> str:
    """Détecte automatiquement le type de document basé sur le contenu du texte."""
    text_lower = text.lower()
    
    # Rapport financier
    if any(word in text_lower for word in [
        "chiffre d'affaires", "marge", "cagr", "résultat net", 
        "ebitda", "bilan", "compte de résultat", "actif", "passif"
    ]):
        return "rapport_financier"
    
    # Article scientifique
    elif any(word in text_lower for word in [
        "méthodologie", "résultats", "hypothèse", "protocole", 
        "étude", "publication", "revue de littérature", "conclusion"
    ]):
        return "article_scientifique"
    
    # Compte-rendu de réunion
    elif any(word in text_lower for word in [
        "décision", "tâche", "assigné", "compte rendu", 
        "action", "responsable", "point bloquant", "ordre du jour"
    ]):
        return "compte_rendu_reunion"
    
    # Contrat juridique
    elif any(word in text_lower for word in [
        "parties", "obligations", "clause", "contrat", 
        "signataire", "article", "cgv", "conditions générales"
    ]):
        return "contrat_juridique"
    
    # Transcription audio/vidéo
    elif any(word in text_lower for word in [
        "transcription", "intervenant", "désaccord", 
        "citation", "enregistrement", "micro", "audio"
    ]):
        return "transcription_audio"
    
    # Documentation technique
    elif any(word in text_lower for word in [
        "installation", "prérequis", "configuration", 
        "dépannage", "commande", "sudo", "api", "endpoint"
    ]):
        return "documentation_technique"
    
    # Par défaut
    else:
        return "general"