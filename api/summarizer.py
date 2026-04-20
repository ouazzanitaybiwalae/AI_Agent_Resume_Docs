# api/summarizer.py - Version finale avec métriques backend
import sys
import os
import re
import math
from typing import List
from format_summary import format_summary, format_as_financial_full

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.chunk_text import chunk_text_by_paragraphs
from src.merge import merge_summaries


# ============================================
# MÉTRIQUES D'ÉVALUATION — LOGS BACKEND UNIQUEMENT
# L'utilisateur ne voit pas ces métriques,
# elles sont affichées dans les logs serveur.
# ============================================

def compute_coverage_score(original: str, summary: str) -> float:
    """
    Exhaustivité sélective : % de concepts clés du source retrouvés dans le résumé.
    Implémentation légère sans dépendance externe.
    """
    stop_words = {
        'le','la','les','un','une','des','et','ou','mais','donc','car','en',
        'dans','pour','par','avec','sans','sous','sur','de','du','il','elle',
        'on','nous','vous','ils','ce','cet','cette','ces','qui','que','dont',
        'où','est','sont','être','avoir','a','au','aux','pas','plus','très',
    }
    # Extraire les mots significatifs du texte original (fréquence > 1)
    orig_words = re.findall(r'\b\w{4,}\b', original.lower())
    freq = {}
    for w in orig_words:
        if w not in stop_words:
            freq[w] = freq.get(w, 0) + 1

    # Concepts clés = mots apparaissant ≥ 2 fois dans l'original
    key_concepts = {w for w, c in freq.items() if c >= 2}
    if not key_concepts:
        return 1.0

    summary_words = set(re.findall(r'\b\w{4,}\b', summary.lower()))
    covered = key_concepts & summary_words
    score = len(covered) / len(key_concepts)
    return round(score, 4)


def compute_concision_score(summary: str, target_bullets: int = 5) -> float:
    """
    Concision : pénalité si le nombre de puces dépasse target + 10%.
    Retourne un score entre 0 et 1.
    """
    bullets = [l for l in summary.split('\n') if l.strip().startswith(('-', '•'))]
    actual = len(bullets)
    if actual == 0:
        return 1.0
    limit = target_bullets * 1.10
    if actual <= limit:
        return 1.0
    # Pénalité proportionnelle au dépassement
    return round(max(0.0, 1.0 - (actual - limit) / target_bullets), 4)


def compute_compression_rate(original: str, summary: str) -> float:
    """Taux de compression : 1 - len(résumé) / len(original)."""
    if not original:
        return 0.0
    return round((1 - len(summary) / len(original)) * 100, 2)


def compute_simple_rouge_1(reference: str, hypothesis: str) -> dict:
    """
    ROUGE-1 simplifié (unigrammes) sans dépendance externe.
    Retourne precision, recall, f1.
    """
    ref_tokens = set(re.findall(r'\b\w+\b', reference.lower()))
    hyp_tokens = re.findall(r'\b\w+\b', hypothesis.lower())
    hyp_set = set(hyp_tokens)

    if not ref_tokens or not hyp_tokens:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    overlap = ref_tokens & hyp_set
    precision = len(overlap) / len(hyp_set) if hyp_set else 0.0
    recall    = len(overlap) / len(ref_tokens) if ref_tokens else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 4),
        "recall":    round(recall, 4),
        "f1":        round(f1, 4),
    }


def log_quality_metrics(original: str, summary: str, doc_type: str, num_sentences: int):
    """
    Calcule et affiche les métriques de qualité dans les logs backend.
    Non visible par l'utilisateur final.
    """
    coverage   = compute_coverage_score(original, summary)
    concision  = compute_concision_score(summary, num_sentences)
    compression = compute_compression_rate(original, summary)
    rouge      = compute_simple_rouge_1(original, summary)

    # Interprétation couverture
    cov_label = "✓ Bonne" if coverage >= 0.6 else ("⚠ Moyenne" if coverage >= 0.4 else "✗ Faible")
    con_label = "✓ Respectée" if concision >= 0.9 else "⚠ Dépassée"

    print("\n" + "═" * 52)
    print("  📊 MÉTRIQUES QUALITÉ DU RÉSUMÉ [BACKEND ONLY]")
    print("═" * 52)
    print(f"  Type document    : {doc_type}")
    print(f"  Taux compression : {compression:.1f}%")
    print(f"  Couverture       : {coverage:.2%}  {cov_label}")
    print(f"  Concision        : {concision:.2%}  {con_label}")
    print(f"  ROUGE-1 Precision: {rouge['precision']:.4f}")
    print(f"  ROUGE-1 Recall   : {rouge['recall']:.4f}")
    print(f"  ROUGE-1 F1       : {rouge['f1']:.4f}")
    print("═" * 52 + "\n")


# ============================================
# UTILITAIRES TEXTE
# ============================================

def extract_sentences(text: str) -> List[str]:
    """Découpe le texte en phrases (conservant la ponctuation)."""
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ü"\'\(])', text)
    return [s.strip() for s in sentences if s.strip()]


def extract_dates_and_responsibilities(text: str) -> str:
    result = "**DATES ET RESPONSABILITÉS**\n\n"

    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        r'\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{4}',
        r'(?:le\s+)?\d{1,2}\s+(?:janv|févr|mars|avr|mai|juin|juil|août|sept|oct|nov|déc)\.?\s+\d{4}',
    ]
    dates = []
    for p in date_patterns:
        dates.extend(re.findall(p, text, re.IGNORECASE))

    if dates:
        result += "**Dates détectées :**\n"
        for d in list(dict.fromkeys(dates))[:10]:
            result += f"• {d}\n"
        result += "\n"

    resp_patterns = [
        r'(?:responsable|chargé|en charge|doit)\s*(?:de)?\s*([^.\n]+)',
        r'(?:tâche|action|mission)\s*(?:de)?\s*([^.\n]+)',
        r'(\w+)\s*(?:doit|devra|doivent)\s*([^.\n]+)',
    ]
    responsibilities = []
    for p in resp_patterns:
        for m in re.findall(p, text, re.IGNORECASE):
            resp = (" ".join(m) if isinstance(m, tuple) else m).strip()
            if resp and len(resp) > 5:
                responsibilities.append(resp)

    if responsibilities:
        result += "**Responsabilités identifiées :**\n"
        for r in list(dict.fromkeys(responsibilities))[:10]:
            result += f"• {r}\n"
    return result


def extract_risks(text: str) -> str:
    result = "**ANALYSE DES RISQUES**\n\n"
    risk_keywords = ['risque', 'danger', 'problème', 'bloquant', 'critique', 'vulnérabilité']
    prob_keywords = ['probabilité', 'probable', 'possible', 'fréquent', 'rare', 'occasionnel']
    risks = []
    for sent in re.split(r'[.!?]', text):
        if any(kw in sent.lower() for kw in risk_keywords):
            prob = next((p.capitalize() for p in prob_keywords if p in sent.lower()), "Non spécifiée")
            clean = sent.strip()[:100]
            if len(clean) > 10:
                risks.append((clean, prob))

    if risks:
        result += "| Risque | Probabilité |\n|--------|-------------|\n"
        for risk, prob in risks[:8]:
            result += f"| {risk} | {prob} |\n"
    else:
        result += "Aucun risque clairement identifié dans le document.\n"
    return result


def simplify_for_non_expert(text: str) -> str:
    replacements = {
        r'\bAPI\b': 'interface de programmation',
        r'\bNLP\b': 'traitement du langage naturel',
        r'\bIA\b': 'intelligence artificielle',
        r'\bML\b': 'apprentissage automatique',
        r'\bLLM\b': 'grand modèle de langage',
        r'\bbackend\b': 'partie serveur',
        r'\bfrontend\b': "partie visible par l'utilisateur",
        r'\bREST\b': 'standard de communication web',
        r'\bBERT\b': 'modèle de compréhension du langage',
        r'\bTransformer\b': 'architecture de modèle IA',
        r'\bfine-tuning\b': 'réglage fin',
        r'\bdataset\b': 'ensemble de données',
        r'\btoken\b': 'unité de texte',
        r'\bembedding\b': 'représentation vectorielle',
    }
    simplified = text
    for pattern, replacement in replacements.items():
        simplified = re.sub(pattern, replacement, simplified, flags=re.IGNORECASE)
    simplified = re.sub(r'\d+st Conference on [^.]*\.', '', simplified)
    simplified = re.sub(r'arXiv:[^\s]+', '', simplified)
    simplified = re.sub(r'\s+', ' ', simplified).strip()
    return simplified


def compare_positions(text: str) -> str:
    result = "🔍 **COMPARAISON DES POSITIONS**\n\n"
    speakers = list(set(re.findall(r'([A-Z]{2,})\s*:', text)))[:4]
    if speakers:
        result += "**Intervenants identifiés :** " + ", ".join(speakers) + "\n\n"
        result += "**Points de convergence :**\n• Les intervenants s'accordent sur les objectifs principaux\n"
        result += "\n**Points de divergence :**\n• Des différences d'opinion existent sur les délais et priorités\n"
        result += "\n**Conclusion :**\n• Un consensus est à trouver sur les points de friction identifiés\n"
    else:
        result += "Aucun auteur ou intervenant clairement identifié.\n"
    return result


def format_hierarchical(text: str) -> str:
    bullets = [
        re.sub(r'^[-•]\s*', '', l.strip())
        for l in text.split('\n')
        if l.strip().startswith(('-', '•'))
    ]
    result = "**RÉSUMÉ HIÉRARCHIQUE**\n\n"
    if bullets:
        result += f"## {bullets[0][:50]}\n\n"
    for i, part in enumerate(bullets[1:4], 1):
        result += f"### Partie {i} : {part[:40]}\n"
        for j in range(1, 3):
            idx = (i - 1) * 2 + j + 3
            if idx < len(bullets):
                result += f"  - {bullets[idx][:60]}\n"
        result += "\n"
    return result


# ============================================
# SCORING EXTRACTIF
# ============================================

def score_sentences(sentences: List[str], text: str) -> List[tuple]:
    stop_words = {
        'le','la','les','un','une','des','et','ou','mais','donc','car','en',
        'dans','pour','par','avec','sans','sous','sur','de','du','il','elle',
        'on','nous','vous','ils','ce','cet','cette','ces','qui','que','dont',
        'où','a','au','aux','par','pas','plus','est','sont','être','avoir',
    }
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = {}
    for w in words:
        if w not in stop_words and len(w) > 2:
            word_freq[w] = word_freq.get(w, 0) + 1

    scored = []
    total = len(sentences)
    for i, sent in enumerate(sentences):
        score = 0
        # Position bias
        pos_ratio = i / total if total > 0 else 0
        if pos_ratio < 0.2:
            score += 3
        elif pos_ratio < 0.4:
            score += 2
        elif pos_ratio < 0.6:
            score += 1

        # Fréquence des mots
        for w in re.findall(r'\b\w+\b', sent.lower()):
            if w in word_freq and word_freq[w] > 1:
                score += min(word_freq[w] / 15, 2)

        # Pénalités longueur
        if len(sent) < 30:
            score -= 5
        if len(sent) > 300:
            score -= 1

        # Bonus contenu utile
        if re.search(r'\d{4}', sent):                                        score += 2
        if re.search(r'[0-9]+\s*%', sent):                                   score += 2
        if re.search(r'[0-9]+[,.]?[0-9]*\s*(?:M€|K€|MAD|millions?)', sent): score += 3
        if re.search(r'(?:décision|conclusion|important|clé|essentiel)', sent, re.I): score += 2

        scored.append((score, sent))
    return scored


def extractive_summary(text: str, num_sentences: int = 5) -> str:
    sentences = extract_sentences(text)
    if not sentences:
        return "- Aucune phrase extractible (document vide ou mal formaté)"
    if len(sentences) <= num_sentences:
        return "\n".join(f"- {s}" for s in sentences)

    scored = sorted(score_sentences(sentences, text), key=lambda x: x[0], reverse=True)
    total = len(sentences)
    selected = []

    # Répartition équitable par zones
    for i in range(num_sentences):
        zone_start = int(i * total / num_sentences)
        zone_end   = min(int((i + 1) * total / num_sentences) + 2, total)
        best, best_score = None, -1
        for score, sent in scored:
            for idx, s in enumerate(sentences):
                if s == sent and zone_start <= idx < zone_end:
                    if score > best_score and sent not in selected:
                        best_score, best = score, sent
                    break
        if best:
            selected.append(best)

    # Compléter si manque
    for score, sent in scored:
        if len(selected) >= num_sentences:
            break
        if sent not in selected:
            selected.append(sent)

    # Remettre en ordre d'apparition
    ordered = [s for s in sentences if s in selected and s not in (ordered := [])] # type: ignore
    # version propre :
    seen = set()
    ordered = []
    for s in sentences:
        if s in selected and s not in seen:
            seen.add(s)
            ordered.append(s)

    return "\n".join(f"- {s}" for s in ordered)


# ============================================
# CONTRAINTES UTILISATEUR
# ============================================

def parse_instructions(instructions: str) -> int:
    if not instructions:
        return 5
    m = re.search(r'(\d+)\s*(?:puces?|points?|bullet|phrases?)', instructions.lower())
    return int(m.group(1)) if m else 5


def detect_document_length(text: str) -> dict:
    length = len(text)
    sc = len(extract_sentences(text))
    if length > 50000 or sc > 500:
        return {"type": "very_long", "default_sentences": 12, "warning": "Document très long (>50k tokens)"}
    elif length > 20000 or sc > 200:
        return {"type": "long",      "default_sentences": 10, "warning": "Document long"}
    elif length > 5000  or sc > 50:
        return {"type": "medium",    "default_sentences": 8,  "warning": None}
    else:
        return {"type": "short",     "default_sentences": 5,  "warning": None}


def apply_user_constraints(summary: str, instructions: str, original_text: str = "") -> str:
    if not instructions:
        return summary
    lower = instructions.lower()

    # Nombre de puces
    m = re.search(r'(\d+)\s*(?:puces?|points?)', lower)
    if m:
        max_b = int(m.group(1))
        lines = summary.split('\n')
        bullets = [l for l in lines if l.strip().startswith(('-', '•'))]
        if len(bullets) > max_b:
            non_b = [l for l in lines if not l.strip().startswith(('-', '•'))]
            return '\n'.join(non_b) + '\n' + '\n'.join(bullets[:max_b])

    if any(k in lower for k in ["extrais uniquement les dates", "extrais les dates"]):
        return extract_dates_and_responsibilities(original_text or summary)

    if "non-expert" in lower or "vulgarisation" in lower:
        return "**Version vulgarisée**\n\n" + simplify_for_non_expert(summary)

    if "compare" in lower and any(k in lower for k in ["positions", "auteurs"]):
        return compare_positions(original_text or summary)

    if "hiérarchique" in lower:
        return format_hierarchical(summary)

    if "risques" in lower and any(k in lower for k in ["probabilités", "probabilite"]):
        return extract_risks(original_text or summary)

    return summary


# ============================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================

def summarize_text(
    text: str,
    doc_type: str = "général",
    instructions: str = "",
    output_format: str = "structuré",
) -> str:
    """
    Résumé extractif algorithmique avec métriques loguées côté backend.
    """
    # ── Rapport financier : extraction directe depuis le texte complet
    if doc_type == "rapport_financier":
        print("[SUMMARIZER] Mode rapport financier — extraction directe des KPIs...")
        result = format_as_financial_full(text, instructions)
        # Logguer les métriques (JSON non résumable classiquement)
        print(f"[SUMMARIZER] Payload financier généré ({len(result)} chars)")
        return result

    # ── Détection longueur
    length_info = detect_document_length(text)
    num_sentences = parse_instructions(instructions)

    if not instructions and length_info["default_sentences"] > num_sentences:
        num_sentences = length_info["default_sentences"]
        if length_info["warning"]:
            print(f"[SUMMARIZER] {length_info['warning']} — cible : {num_sentences} phrases")

    # ── Résumé extractif
    raw_summary = extractive_summary(text, num_sentences)

    # Vérification résumé trop court
    bullet_count = sum(1 for l in raw_summary.split('\n') if l.strip().startswith('-'))
    if bullet_count < 3 and len(text) > 10000:
        print("[SUMMARIZER] ⚠ Résumé trop court, augmentation...")
        raw_summary = extractive_summary(text, num_sentences * 2)

    # ── Formatage selon type de document
    formatted = format_summary(raw_summary, doc_type, instructions, text)

    # ── Contraintes utilisateur
    final = apply_user_constraints(formatted, instructions, text)

    # ── Métriques qualité — logs backend uniquement (non visibles par l'utilisateur)
    log_quality_metrics(text, final, doc_type, num_sentences)

    return final


if __name__ == "__main__":
    test = """
    L'intelligence artificielle (IA) a débuté en 1956 lors d'une conférence à Dartmouth.
    Le Deep Learning a véritablement accéléré le domaine à partir de 2010 avec AlexNet.
    Aujourd'hui, l'IA est utilisée dans de nombreux secteurs industriels et académiques.
    Les grands modèles de langage (LLM) comme GPT-4 ont transformé le traitement du texte.
    """
    result = summarize_text(test, doc_type="general", instructions="résumé en 3 puces")
    print(result)