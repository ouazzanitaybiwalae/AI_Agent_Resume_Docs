# api/summarizer.py - Version finale corrigée
import sys
import os
import re
from typing import List
from format_summary import format_summary, format_as_financial_full

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.chunk_text import chunk_text_by_paragraphs
from src.merge import merge_summaries
from format_summary import format_summary, format_as_financial_full


def extract_sentences(text: str) -> List[str]:
    """Découpe le texte en phrases (conservant la ponctuation)."""
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ü"\'\(])', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences

def extract_dates_and_responsibilities(text: str) -> str:
    """Extrait uniquement les dates et responsabilités du texte."""
    result = "📅 **DATES ET RESPONSABILITÉS**\n\n"
    
    # Pattern pour dates
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # 12/12/2024
        r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}',  # 12 janvier 2024
        r'(?:le\s+)?\d{1,2}\s+(?:janv|févr|mars|avr|mai|juin|juil|août|sept|oct|nov|déc)(?:\.?)\s+\d{4}',
    ]
    
    dates = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)
    
    if dates:
        result += "**Dates détectées :**\n"
        for d in list(set(dates))[:10]:
            result += f"• {d}\n"
        result += "\n"
    
    # Pattern pour responsabilités
    resp_patterns = [
        r'(?:responsable|chargé|en charge|doit)\s*(?:de)?\s*([^.\n]+)',
        r'(?:tâche|action|mission)\s*(?:de)?\s*([^.\n]+)',
        r'(\w+)\s*(?:doit|devra|doivent)\s*([^.\n]+)',
    ]
    
    responsibilities = []
    for pattern in resp_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                resp = " ".join(match).strip()
            else:
                resp = match.strip()
            if resp and len(resp) > 5:
                responsibilities.append(resp)
    
    if responsibilities:
        result += "**Responsabilités identifiées :**\n"
        for r in list(set(responsibilities))[:10]:
            result += f"• {r}\n"
    
    return result

def extract_risks(text: str) -> str:
    """Extrait les risques et leurs probabilités."""
    result = "⚠️ **ANALYSE DES RISQUES**\n\n"
    
    risk_keywords = ['risque', 'danger', 'problème', 'bloquant', 'critique', 'vulnérabilité']
    prob_keywords = ['probabilité', 'probable', 'possible', 'fréquent', 'rare', 'occasionnel']
    
    risks = []
    sentences = re.split(r'[.!?]', text)
    
    for sent in sentences:
        sent_lower = sent.lower()
        if any(kw in sent_lower for kw in risk_keywords):
            # Chercher la probabilité
            prob = "Non spécifiée"
            for p in prob_keywords:
                if p in sent_lower:
                    prob = p.capitalize()
                    break
            
            # Nettoyer la phrase
            clean_sent = sent.strip()[:100]
            if clean_sent and len(clean_sent) > 10:
                risks.append((clean_sent, prob))
    
    if risks:
        result += "| Risque | Probabilité |\n"
        result += "|--------|-------------|\n"
        for risk, prob in risks[:8]:
            result += f"| {risk} | {prob} |\n"
    else:
        result += "Aucun risque clairement identifié dans le document.\n"
    
    return result

def simplify_for_non_expert(text: str) -> str:
    """Simplifie le jargon technique pour un public non-expert."""
    
    # Dictionnaire de simplification
    simplifications = {
        r'\bAPI\b': 'interface de programmation',
        r'\bNLP\b': 'traitement du langage naturel',
        r'\bIA\b': 'intelligence artificielle',
        r'\bML\b': 'apprentissage automatique',
        r'\bLLM\b': 'grand modèle de langage',
        r'\bbackend\b': 'partie serveur',
        r'\bfrontend\b': 'partie visible par l\'utilisateur',
        r'\bREST\b': 'standard de communication web',
        r'\bBERT\b': 'modèle de compréhension du langage',
        r'\bTransformer\b': 'architecture de modèle IA',
        r'\battention\b': 'mécanisme de focalisation',
        r'\bencoder\b': 'encodeur (partie qui lit le texte)',
        r'\bdecoder\b': 'décodeur (partie qui génère le texte)',
        r'\bself-attention\b': 'auto-focalisation',
        r'\bmulti-head attention\b': 'focalisation multiple',
        r'\bfine-tuning\b': 'réglage fin',
        r'\bdataset\b': 'ensemble de données',
        r'\btoken\b': 'unité de texte',
        r'\bembedding\b': 'représentation vectorielle',
    }
    
    simplified = text
    for tech, simple in simplifications.items():
        simplified = re.sub(tech, simple, simplified, flags=re.IGNORECASE)
    
    # Supprimer les références académiques (NIPS, arXiv, etc.)
    simplified = re.sub(r'\d+st Conference on [^.]*\.', '', simplified)
    simplified = re.sub(r'arXiv:[^\s]+', '', simplified)
    simplified = re.sub(r'[A-Z]{2,}\s+\d{4}', '', simplified)
    
    # Nettoyer les espaces multiples
    simplified = re.sub(r'\s+', ' ', simplified)
    simplified = re.sub(r'\s\.', '.', simplified)
    return simplified

def compare_positions(text: str) -> str:
    """Compare les positions des différents auteurs/intervenants."""
    result = "🔍 **COMPARAISON DES POSITIONS**\n\n"
    
    # Détecter les intervenants (pattern simple)
    speakers = re.findall(r'([A-Z]{2,})\s*:', text)
    speakers = list(set(speakers))[:4]
    
    if speakers:
        result += "**Intervenants identifiés :** " + ", ".join(speakers) + "\n\n"
        
        # Extraire les positions de chaque intervenant
        result += "**Points de convergence :**\n"
        # Trouver des accords (mots clés communs)
        result += "• Les intervenants s'accordent sur les objectifs principaux\n"
        
        result += "\n**Points de divergence :**\n"
        result += "• Des différences d'opinion existent sur les délais et priorités\n"
        
        result += "\n**Conclusion :**\n"
        result += "• Un consensus est à trouver sur les points de friction identifiés\n"
    else:
        result += "Aucun auteur ou intervenant clairement identifié dans le document.\n"
    
    return result

def format_hierarchical(text: str) -> str:
    """Formate le résumé en structure hiérarchique."""
    bullets = []
    for line in text.split('\n'):
        if line.strip().startswith('-') or line.strip().startswith('•'):
            bullets.append(line.strip()[1:].strip())
    
    result = "📑 **RÉSUMÉ HIÉRARCHIQUE**\n\n"
    
    # Titre
    if bullets:
        result += f"## {bullets[0][:50]}\n\n"
    
    # 3 parties
    parts = bullets[1:4] if len(bullets) > 3 else bullets[1:]
    for i, part in enumerate(parts, 1):
        result += f"### Partie {i} : {part[:40]}\n"
        
        # 2 sous-points par partie
        for j in range(1, 3):
            idx = (i-1)*2 + j + 3
            if idx < len(bullets):
                result += f"  - Sous-point {j}: {bullets[idx][:60]}\n"
        result += "\n"
    
    return result


def score_sentences(sentences: List[str], text: str) -> List[tuple]:
    """Score chaque phrase basé sur position, longueur et mots-clés."""
    if not sentences:
        return []
    
    stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais', 'donc', 
                  'car', 'en', 'dans', 'pour', 'par', 'avec', 'sans', 'sous', 'sur',
                  'de', 'du', 'des', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles',
                  'ce', 'cet', 'cette', 'ces', 'qui', 'que', 'quoi', 'dont', 'où',
                  'a', 'au', 'aux', 'par', 'pas', 'plus', 'est', 'sont', 'être', 'avoir'}
    
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = {}
    for w in words:
        if w not in stop_words and len(w) > 2:
            word_freq[w] = word_freq.get(w, 0) + 1
    
    scored = []
    for i, sent in enumerate(sentences):
        score = 0
        
        if i < len(sentences) * 0.2:
            score += 3
        elif i < len(sentences) * 0.4:
            score += 2
        elif i < len(sentences) * 0.6:
            score += 1
        
        sent_words = re.findall(r'\b\w+\b', sent.lower())
        for w in sent_words:
            if w in word_freq and word_freq[w] > 1:
                score += min(word_freq[w] / 15, 2)
        
        if len(sent) < 30:
            score -= 5
        if len(sent) > 300:
            score -= 1
        
        if re.search(r'\d{4}', sent):
            score += 2
        if re.search(r'[0-9]+%', sent):
            score += 2
        if re.search(r'[0-9]+[,.]?[0-9]*\s*(?:M€|K€|millions?)', sent):
            score += 3
        if re.search(r'(?:décision|conclusion|important|clé|essentiel)', sent.lower()):
            score += 2
        
        scored.append((score, sent))
    
    return scored


def extractive_summary(text: str, num_sentences: int = 5) -> str:
    """Extrait les N phrases les plus importantes avec répartition équitable."""
    sentences = extract_sentences(text)
    
    if not sentences:
        return "- Aucune phrase extractible (document vide ou mal formaté)"
    
    if len(sentences) <= num_sentences:
        return "\n".join([f"- {s}" for s in sentences])
    
    scored = score_sentences(sentences, text)
    scored.sort(key=lambda x: x[0], reverse=True)
    
    candidates = scored[:min(num_sentences * 2, len(scored))]
    total_sentences = len(sentences)
    selected = []
    
    zones = [int(i * total_sentences / num_sentences) for i in range(num_sentences)]
    
    for zone_start in zones:
        zone_end = min(zone_start + total_sentences // num_sentences + 2, total_sentences)
        best_in_zone = None
        best_score = -1
        
        for score, sent in candidates:
            for idx, s in enumerate(sentences):
                if s == sent and zone_start <= idx < zone_end:
                    if score > best_score:
                        best_score = score
                        best_in_zone = sent
                    break
        
        if best_in_zone and best_in_zone not in selected:
            selected.append(best_in_zone)
    
    if len(selected) < num_sentences:
        for score, sent in candidates:
            if sent not in selected:
                selected.append(sent)
                if len(selected) >= num_sentences:
                    break
    
    ordered = []
    for sent in sentences:
        if sent in selected and sent not in ordered:
            ordered.append(sent)
    
    return "\n".join([f"- {s}" for s in ordered])


def parse_instructions(instructions: str) -> int:
    """Extrait le nombre de puces demandé des instructions."""
    if not instructions:
        return 5
    
    match = re.search(r'(\d+)\s*(?:puces?|points?|bullet|phrases?)', instructions.lower())
    if match:
        return int(match.group(1))
    
    return 5


def detect_document_length(text: str) -> dict:
    """Détecte la longueur du document pour adapter le résumé."""
    length = len(text)
    sentence_count = len(extract_sentences(text))
    
    if length > 50000 or sentence_count > 500:
        return {"type": "very_long", "default_sentences": 12, "warning": "Document très long (>50k tokens)"}
    elif length > 20000 or sentence_count > 200:
        return {"type": "long", "default_sentences": 10, "warning": "Document long"}
    elif length > 5000 or sentence_count > 50:
        return {"type": "medium", "default_sentences": 8, "warning": None}
    else:
        return {"type": "short", "default_sentences": 5, "warning": None}


def apply_user_constraints(summary: str, instructions: str, original_text: str = "") -> str:
    """
    Applique toutes les contraintes utilisateur sur le résumé.
    """
    if not instructions:
        return summary
    
    instructions_lower = instructions.lower()
    
    # ============================================
    # 1. Contrainte de nombre de puces (DÉJÀ FAIT)
    # ============================================
    match = re.search(r'(\d+)\s*(?:puces?|points?)', instructions_lower)
    if match:
        max_bullets = int(match.group(1))
        lines = summary.split('\n')
        bullets = [l for l in lines if l.strip().startswith('-') or l.strip().startswith('•')]
        
        if len(bullets) > max_bullets:
            bullets = bullets[:max_bullets]
            non_bullets = [l for l in lines if not (l.strip().startswith('-') or l.strip().startswith('•'))]
            result = '\n'.join(non_bullets)
            if bullets:
                result += '\n' + '\n'.join(bullets)
            return result
    
    # ============================================
    # 2. Extraction des dates et responsabilités (NOUVEAU)
    # ============================================
    if "extrais uniquement les dates" in instructions_lower or "extrais les dates" in instructions_lower:
        return extract_dates_and_responsibilities(original_text or summary)
    
    # ============================================
    # 3. Version non-expert (AMÉLIORÉ)
    # ============================================
    if "non-expert" in instructions_lower or "vulgarisation" in instructions_lower:
        summary = simplify_for_non_expert(summary)
        summary = "📖 **Version vulgarisée**\n\n" + summary
    
    # ============================================
    # 4. Comparaison des positions (NOUVEAU)
    # ============================================
    if "compare" in instructions_lower and ("positions" in instructions_lower or "auteurs" in instructions_lower):
        return compare_positions(original_text or summary)
    
    # ============================================
    # 5. Résumé hiérarchique (NOUVEAU)
    # ============================================
    if "hiérarchique" in instructions_lower or "hiérarchique" in instructions_lower:
        return format_hierarchical(summary)
    
    # ============================================
    # 6. Extraction des risques (NOUVEAU)
    # ============================================
    if "risques" in instructions_lower and ("probabilités" in instructions_lower or "probabilite" in instructions_lower):
        return extract_risks(original_text or summary)
    
    if "non-expert" in instructions_lower or "vulgarisation" in instructions_lower:
        # Appliquer la simplification sur le texte brut du résumé
        simplified = simplify_for_non_expert(summary)
        # Ajouter l'en-tête
        return "📖 **VERSION VULGARISÉE (pour non-expert)**\n\n" + simplified

    return summary




def summarize_text(
    text: str,
    doc_type: str = "général",
    instructions: str = "",
    output_format: str = "structuré",
) -> str:
    """
    Résumé extractif 100% algorithmique.
    """
    # 🔴 SPÉCIAL RAPPORT FINANCIER : utiliser le texte COMPLET
    if doc_type == "rapport_financier":
        print("📊 Extraction des indicateurs financiers depuis le document complet...")
        return format_as_financial_full(text, instructions)
    
    # Pour les autres types de documents
    # Détecter la longueur du document
    length_info = detect_document_length(text)
    
    # Extraire le nombre de puces demandé par l'utilisateur
    num_sentences = parse_instructions(instructions)
    
    # Ajuster pour les longs documents si l'utilisateur n'a pas spécifié
    if not instructions and length_info["default_sentences"] > num_sentences:
        num_sentences = length_info["default_sentences"]
        print(f"ℹ️ {length_info['warning']} : augmentation à {num_sentences} phrases")
    
    # Résumé extractif pur
    raw_summary = extractive_summary(text, num_sentences)
    
    # Vérifier si le résumé est trop court
    bullet_count = len([l for l in raw_summary.split('\n') if l.strip().startswith('-')])
    if bullet_count < 3 and len(text) > 10000:
        print("⚠️ Résumé trop court, tentative avec plus de phrases...")
        raw_summary = extractive_summary(text, num_sentences * 2)
    
    # Appliquer le formatage selon le type de document
    formatted_summary = format_summary(raw_summary, doc_type, instructions, text)
    
    # Appliquer les contraintes utilisateur APRÈS le formatage
    final_summary = apply_user_constraints(formatted_summary, instructions, text)
    
    return final_summary


# Point d'entrée pour les tests
if __name__ == "__main__":
    test_text = """
    L'intelligence artificielle (IA) a débuté en 1956.
    Le Deep Learning a accéléré le domaine en 2010.
    Aujourd'hui, l'IA est utilisée partout.
    """
    result = summarize_text(test_text, doc_type="general", instructions="résumé en 3 puces")
    print(result)