# api/format_summary.py - Version complète avec toutes les fonctions
import re

# ============================================
# FONCTIONS POUR RAPPORT FINANCIER
# ============================================

def format_as_financial_full(text: str, instructions: str = "") -> str:
    """
    Retourne un tableau HTML moderne pour les rapports financiers.
    """
    clean_text = clean_text_for_extraction(text)

    with open("debug_extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    
    # DEBUG : Afficher les 2000 premiers caractères du texte nettoyé
    print("=== TEXTE NETTOYÉ (début) ===")
    print(clean_text[:2000])
    print("==============================")
    
    # Extraire les indicateurs
    indicators = {
        "Chiffre d'affaires": extract_chiffre_affaires(clean_text),
        "Croissance": extract_croissance(clean_text),
        "Marge nette": extract_marge_nette(clean_text),
        "Résultat net": extract_resultat_net(clean_text),
        "Ratio d'endettement": extract_endettement(clean_text),
        "Actifs totaux": extract_actifs(clean_text),
        "Capitaux propres": extract_capitaux_propres(clean_text),
    }
    
    # DEBUG : Afficher ce qui a été trouvé
    print("=== INDICATEURS TROUVÉS ===")
    for k, v in indicators.items():
        print(f"{k}: {v}")
    print("============================")
    
    # Construire un tableau HTML moderne
    html = '''
    <div class="financial-table-container">
        <h3 class="financial-title">📊 RÉSUMÉ FINANCIER</h3>
        <table class="financial-table">
            <thead>
                <tr>
                    <th>Indicateur</th>
                    <th>Valeur</th>
                </tr>
            </thead>
            <tbody>
    '''
    
    for label, value in indicators.items():
        html += f'''
            <tr>
                <td class="indicator-label">{label}</td>
                <td class="indicator-value">{value}</td>
            </tr>
        '''
    
    html += '''
            </tbody>
        </table>
        <div class="financial-source">Source : Rapport financier 2025</div>
    </div>
    '''
    
    return html


def clean_text_for_extraction(text: str) -> str:
    """Nettoie le texte pour l'extraction."""
    text = re.sub(r'\n\s*\d+\.\d+\s+[A-Z]', '\n', text)
    text = re.sub(r'\n\s*\d+\.\s+[A-Z]', '\n', text)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if not re.match(r'^\s*\d+(?:\.\d+)?\s*$', line):
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)


def extract_chiffre_affaires(text: str) -> str:
    """Extrait le chiffre d'affaires - format: '2025 → 5 200 000 MAD' ou '2025 5 200 000'"""
    patterns = [
        r'2025\s*[→-]?\s*(\d+(?:\s?\d+)?)\s*MAD',
        r'2025\s+(\d+(?:\s?\d+)?)\s*[+]',
        r'Chiffre d[\'\"]affaires.*?2025.*?(\d+(?:\s?\d+)?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).replace(' ', '')
            try:
                num = int(value)
                return f"{num:,} MAD".replace(',', ' ')
            except:
                return f"{value} MAD"
    return None


def extract_croissance(text: str) -> str:
    """Extrait le taux de croissance."""
    patterns = [
        r'Variation\s*[+]\s*(\d+(?:[.,]\d+)?)\s*%',
        r'croissance.*?(\d+(?:[.,]\d+)?)\s*%',
        r'(\d+(?:[.,]\d+)?)\s*%\s*(?:de\s*)?(?:croissance|hausse|augmentation)',
        r'Croissance\s*:?\s*(\d+(?:[.,]\d+)?)\s*%',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '.')
            return f"{value} %"
    return None


def extract_marge_nette(text: str) -> str:
    """Extrait la marge nette."""
    patterns = [
        r'Marge nette\s*=\s*(\d+(?:[.,]\d+)?)\s*%',
        r'marge\s*nette.*?(\d+(?:[.,]\d+)?)\s*%',
        r'(\d+(?:[.,]\d+)?)\s*%\s*(?:de\s*)?marge\s*nette',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '.')
            return f"{value} %"
    return None

def extract_metadata(text: str) -> str:
    """Extrait les métadonnées (projet, date, participants)."""
    result = ""
    
    # Projet
    project_match = re.search(r'Projet\s*[:\-]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if project_match:
        result += f"**📁 Projet** : {project_match.group(1).strip()}\n"
    
    # Date
    date_match = re.search(r'Date\s*[:\-]\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
    if date_match:
        result += f"**📅 Date** : {date_match.group(1).strip()}\n"
    
    # Participants
    participants_match = re.search(r'Participants\s*[:\-]\s*(.+?)(?:\n\n|\n\[)', text, re.DOTALL | re.IGNORECASE)
    if participants_match:
        participants = participants_match.group(1).strip()
        # Nettoyer et formater
        participants = participants.replace('\n', ', ')
        result += f"**👥 Participants** : {participants}\n"
    
    return result

def extract_resultat_net(text: str) -> str:
    """Extrait le résultat net - format: 'Résultat net 2025 = 1 100 000 MAD'"""
    patterns = [
        r'Résultat\s+net\s+2025\s*[=:]\s*(\d+(?:\s?\d+)?)\s*MAD',
        r'Résultat\s+net.*?2025.*?(\d+(?:\s?\d+)?)\s*MAD',
        r'Bénéfice.*?2025.*?(\d+(?:\s?\d+)?)\s*MAD',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).replace(' ', '')
            try:
                num = int(value)
                return f"{num:,} MAD".replace(',', ' ')
            except:
                return f"{value} MAD"
    return None

def extract_exchanges_with_timestamps(text: str) -> list:
    """Extrait les échanges avec timestamps [hh:mm:ss]."""
    exchanges = []
    
    # Pattern pour capturer les timestamps et le contenu
    pattern = r'\[(\d{2}:\d{2}:\d{2})\]\s*([A-Z0-9_]+)\s*:\s*(.+?)(?=\n\[|$)'
    matches = re.findall(pattern, text, re.DOTALL)
    
    for match in matches:
        timestamp = match[0]
        speaker = match[1]
        content = match[2].strip()[:200]  # Limiter la longueur
        if content:
            exchanges.append(f"**[{timestamp}] {speaker}** : {content}")
    
    return exchanges


def extract_executive_summary(text: str) -> list:
    """Extrait la synthèse / executive summary."""
    summary = []
    
    # Chercher la section "Synthèse" ou "Executive Summary"
    pattern = r'(?:Synthèse|Executive Summary)[^\n]*\n(.*?)(?=\n\n|\n\[|\n\d+\.|\n\*\*)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        content = match.group(1)
        # Extraire les puces ou les lignes
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Enlever les tirets et astérisques
                line = re.sub(r'^[-*•]\s*', '', line)
                if line and len(line) > 10:
                    summary.append(line)
    
    return summary[:5]

def extract_action_items(text: str) -> list:
    """Extrait les actions à réaliser (action items)."""
    actions = []
    
    # Chercher le tableau ou la liste des actions
    # Pattern pour tableau markdown
    table_pattern = r'\|.*\|.*\|\n\|[-:|]+\|\n((?:\|.*\|.*\|\n)+)'
    match = re.search(table_pattern, text)
    
    if match:
        rows = match.group(1).strip().split('\n')
        for row in rows:
            cells = row.split('|')
            if len(cells) >= 3:
                responsible = cells[1].strip()
                action = cells[2].strip()
                deadline = cells[3].strip() if len(cells) > 3 else "À définir"
                if responsible and action:
                    actions.append(f"**{responsible}** : {action} (échéance: {deadline})")
    else:
        # Chercher les actions dans le texte
        action_pattern = r'(?:Action|Tâche|Responsable)[^\n]*[:\-]\s*(.+?)(?:\n|$)'
        matches = re.findall(action_pattern, text, re.IGNORECASE)
        for match in matches[:5]:
            actions.append(match.strip())
    
    return actions


def extract_decisions(text: str) -> list:
    """Extrait les décisions prises."""
    decisions = []
    
    # Chercher les décisions
    decision_pattern = r'(?:Décision|Validé|Accepté)[^\n]*[:\-]\s*(.+?)(?:\n|$)'
    matches = re.findall(decision_pattern, text, re.IGNORECASE)
    
    for match in matches:
        clean = match.strip()
        if clean and len(clean) > 10:
            decisions.append(clean)
    
    return decisions


def extract_pending_points(text: str) -> list:
    """Extrait les points en suspens."""
    pending = []
    
    # Chercher les points en suspens
    pending_pattern = r'(?:Point[^\n]*bloquant|En suspens|À traiter)[^\n]*[:\-]\s*(.+?)(?:\n|$)'
    matches = re.findall(pending_pattern, text, re.DOTALL | re.IGNORECASE)
    
    for match in matches:
        clean = match.strip()
        if clean and len(clean) > 10:
            pending.append(clean)
    
    return pending


def extract_endettement(text: str) -> str:
    """Extrait le ratio d'endettement - format: 'ratio d'endettement : 35,7 %'"""
    patterns = [
        r'ratio d[\'\"]endettement\s*:?\s*(\d+(?:[.,]\d+)?)\s*%',
        r'endettement\s*:?\s*(\d+(?:[.,]\d+)?)\s*%',
        r'(\d+(?:[.,]\d+)?)\s*%\s*(?:de\s*)?(?:endettement)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(',', '.')
            return f"{value} %"
    return None

def extract_actifs(text: str) -> str:
    """Extrait le total des actifs - additionne 'Actifs immobilisés' + 'Actifs circulants'"""
    immo_match = re.search(r'Actifs immobilisés\s+(\d+(?:\s?\d+)?)', text, re.IGNORECASE)
    circ_match = re.search(r'Actifs circulants\s+(\d+(?:\s?\d+)?)', text, re.IGNORECASE)
    
    if immo_match and circ_match:
        immo = int(immo_match.group(1).replace(' ', ''))
        circ = int(circ_match.group(1).replace(' ', ''))
        total = immo + circ
        return f"{total:,} MAD".replace(',', ' ')
    
    # Fallback
    match = re.search(r'Actifs?\s+Type.*?Actifs immobilisés\s+(\d+(?:\s?\d+)?).*?Actifs circulants\s+(\d+(?:\s?\d+)?)', text, re.DOTALL | re.IGNORECASE)
    if match:
        immo = int(match.group(1).replace(' ', ''))
        circ = int(match.group(2).replace(' ', ''))
        total = immo + circ
        return f"{total:,} MAD".replace(',', ' ')
    return None

def extract_capitaux_propres(text: str) -> str:
    """Extrait les capitaux propres - format: 'Capitaux propres 4 500 000'"""
    patterns = [
        r'Capitaux propres\s+(\d+(?:\s?\d+)?)',
        r'Capitaux propres\s*:?\s*(\d+(?:\s?\d+)?)\s*MAD',
        r'Capitaux propres\s*=\s*(\d+(?:\s?\d+)?)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).replace(' ', '')
            try:
                num = int(value)
                return f"{num:,} MAD".replace(',', ' ')
            except:
                return f"{value} MAD"
    return None


# ============================================
# FONCTIONS POUR LES AUTRES TYPES DE DOCUMENTS
# ============================================

def format_summary(summary_text: str, doc_type: str, instructions: str = "", original_text: str = "") -> str:
    """
    Formate le résumé selon le type de document.
    Intègre la détection des cas limites.
    """
    result = ""
    
    # 1. Détection des tableaux/graphiques
    result += detect_tables_and_charts(original_text)
    
    # 2. Détection des contradictions
    result += detect_contradictions(original_text)
    
    # 3. Détection de la perte en cascade
    result += check_cascade_loss(original_text, summary_text)
    
    # 4. Détection des langues mixtes
    result += detect_language_mix(original_text)
    
    # 5. Formatage selon le type de document
    if doc_type == "compte_rendu_reunion":
        result += format_as_actionable(summary_text)
    elif doc_type == "article_scientifique":
        result += format_as_scientific(summary_text)
    elif doc_type == "contrat_juridique":
        result += format_as_legal(summary_text)
    elif doc_type == "transcription_audio":
        result += format_as_transcription(summary_text)
    elif doc_type == "documentation_technique":
        result += format_as_tech_guide(summary_text)
    else:
        result += summary_text
    
    return result

def extract_bullets(text: str):
    """Extrait les lignes qui commencent par un tiret."""
    lines = text.split('\n')
    bullets = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('-') or stripped.startswith('•'):
            content = stripped[1:].strip()
            if content:
                bullets.append(content)
    return bullets

def detect_tables_and_charts(text: str) -> str:
    """
    Détecte la présence de tableaux ou graphiques dans le document.
    Retourne un message d'avertissement si nécessaire.
    """
    # Patterns pour détecter des tableaux
    table_patterns = [
        r'\|.*\|.*\|',           # Markdown table
        r'\+-+\+',               # ASCII table
        r'Tableau\s+\d+',        # "Tableau 1"
        r'Figure\s+\d+',         # "Figure 1"
        r'Graphique\s+\d+',      # "Graphique 1"
        r'\[\s*table\s*\]',      # [table]
    ]
    
    for pattern in table_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return "\n\n⚠️ **Note** : Le document contient des tableaux ou graphiques qui ont été simplifiés en texte. Les données structurées visuelles peuvent être partiellement perdues.\n"
    
    return ""

def detect_contradictions(text: str) -> str:
    """
    Détecte les contradictions ou biais dans le document.
    Retourne une formulation prudente si nécessaire.
    """
    contradictions = []
    
    # Patterns de contradiction
    contradiction_patterns = [
        (r'(oui|vrai|confirmé|accepté).{0,50}(non|faux|refusé|rejeté)', 
         "Présence d'affirmations contradictoires"),
        (r'(augmentation|hausse|croissance).{0,50}(diminution|baisse|décroissance)',
         "Évolution contradictoire des indicateurs"),
        (r'(obligation|doit|tenu).{0,50}(option|facultatif|possible)',
         "Nuances entre obligation et option"),
    ]
    
    for pattern, message in contradiction_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            contradictions.append(message)
    
    if contradictions:
        warning = "\n\n⚠️ **Avertissement** : Le document contient des informations potentiellement contradictoires :\n"
        for c in contradictions[:3]:
            warning += f"  • {c}\n"
        warning += "\n> *Formulation prudente recommandée : 'L'auteur affirme que... Certains passages suggèrent...'*\n"
        return warning
    
    return ""

def check_cascade_loss(original_text: str, summary_text: str) -> str:
    """
    Vérifie la perte d'information lors d'un résumé en cascade.
    Calcule le taux de compression et alerte si >30%.
    """
    original_len = len(original_text)
    summary_len = len(summary_text)
    
    if original_len == 0:
        return ""
    
    compression_rate = (1 - summary_len / original_len) * 100
    
    if compression_rate > 30:
        return f"\n\n⚠️ **Alerte cascade** : Le taux de compression est de {compression_rate:.1f}% (>30%). Une perte d'information significative peut s'être produite. Il est déconseillé de résumer ce résumé davantage.\n"
    
    return ""


def detect_language_mix(text: str) -> str:
    """
    Détecte la présence de langues mixtes ou termes techniques non traduits.
    """
    # Caractères latins vs autres
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    other_chars = len(re.findall(r'[^\x00-\x7F]', text))
    
    if other_chars > 0 and latin_chars > other_chars * 2:
        return "\n\n🌐 **Note linguistique** : Le document contient un mélange de langues. Les termes techniques non traduits ont été conservés entre crochets pour préserver leur sens.\n"
    
    # Détection de termes techniques en anglais
    tech_terms = re.findall(r'\b(?:API|NLP|LLM|ML|AI|REST|JSON|XML|HTTP|HTTPS|TCP|IP|SDK|IDE|CLI|GUI)\b', text)
    if tech_terms:
        unique_terms = list(set(tech_terms))
        return f"\n\n🔧 **Termes techniques** : Les termes suivants ont été conservés dans leur langue d'origine : {', '.join(unique_terms[:5])}\n"
    
    return ""



def format_as_actionable(text: str) -> str:
    """Format compte-rendu actionnable."""
    bullets = extract_bullets(text)
    
    result = "## 📋 COMPTE-RENDU ACTIONNABLE\n\n"
    
    decisions = []
    tasks = []
    pending = []
    
    for bullet in bullets:
        lower = bullet.lower()
        if 'décision' in lower or 'validé' in lower or 'acté' in lower:
            decisions.append(bullet)
        elif 'tâche' in lower or 'assigné' in lower or 'doit' in lower:
            tasks.append(bullet)
        elif 'suspend' in lower or 'attente' in lower:
            pending.append(bullet)
        else:
            decisions.append(bullet)
    
    if decisions:
        result += "**✅ DÉCISIONS ACTÉES**\n"
        for d in decisions[:5]:
            result += f"- {d}\n"
        result += "\n"
    
    if tasks:
        result += "**🎯 TÂCHES ASSIGNÉES**\n"
        for t in tasks[:5]:
            result += f"- {t}\n"
    
    return result

def format_as_transcription(text: str) -> str:
    """
    Format transcription audio/vidéo : chronologie thématique.
    Extrait les timestamps, intervenants, sujets, décisions.
    """
    bullets = extract_bullets(text)
    
    result = "🎙️ CHRONOLOGIE THÉMATIQUE\n\n"
    
    # Extraire les métadonnées (projet, date, participants)
    metadata = extract_metadata(text)
    if metadata:
        result += metadata
        result += "\n"
    
    # Extraire les échanges avec timestamps
    exchanges = extract_exchanges_with_timestamps(text)
    if exchanges:
        result += "**💬 ÉCHANGES CLÉS**\n\n"
        for exchange in exchanges[:10]:  # Limiter à 10 échanges
            result += f"{exchange}\n"
        result += "\n"
    
    # Extraire la synthèse (executive summary)
    summary = extract_executive_summary(text)
    if summary:
        result += "**📋 SYNTHÈSE**\n\n"
        for item in summary[:5]:
            result += f"• {item}\n"
        result += "\n"
    
    # Extraire les actions (action items)
    actions = extract_action_items(text)
    if actions:
        result += "**✅ ACTIONS À RÉALISER**\n\n"
        for action in actions[:5]:
            result += f"• {action}\n"
        result += "\n"
    
    # Extraire les décisions
    decisions = extract_decisions(text)
    if decisions:
        result += "**📌 DÉCISIONS PRISES**\n\n"
        for decision in decisions[:3]:
            result += f"• {decision}\n"
        result += "\n"
    
    # Extraire les points en suspens
    pending = extract_pending_points(text)
    if pending:
        result += "**⏳ POINTS EN SUSPENS**\n\n"
        for point in pending[:3]:
            result += f"• {point}\n"
    
    return result


def format_as_legal(text: str) -> str:
    """Format contrat juridique : synthèse opérationnelle."""
    bullets = extract_bullets(text)
    
    result = "⚖️ SYNTHÈSE OPÉRATIONNELLE DU CONTRAT\n\n"
    
    # Classification des informations
    parties = []
    objet = []
    obligations = []
    dates = []
    clauses = []
    
    for bullet in bullets:
        lower = bullet.lower()
        if 'partie' in lower or 'contractant' in lower or 'créancier' in lower or 'débiteur' in lower:
            parties.append(bullet)
        elif 'objet' in lower or 'obligation' in lower:
            objet.append(bullet)
        elif 'doit' in lower or 'tenu' in lower or 'charge' in lower or 'responsabilité' in lower:
            obligations.append(bullet)
        elif 'date' in lower or 'délai' in lower or 'prescrit' in lower:
            dates.append(bullet)
        elif 'clause' in lower or 'résiliation' in lower or 'pénalité' in lower or 'annulation' in lower:
            clauses.append(bullet)
    
    if parties:
        result += "**👥 PARTIES CONTRACTANTES**\n"
        for p in parties[:3]:
            result += f"• {p}\n"
        result += "\n"
    
    if objet:
        result += "**📜 OBJET DU CONTRAT**\n"
        for o in objet[:3]:
            result += f"• {o}\n"
        result += "\n"
    
    if obligations:
        result += "**⚡ OBLIGATIONS RÉCIPROQUES**\n"
        for ob in obligations[:4]:
            result += f"• {ob}\n"
        result += "\n"
    
    if dates:
        result += "**📅 DATES ET DÉLAIS CLÉS**\n"
        for d in dates[:3]:
            result += f"• {d}\n"
        result += "\n"
    
    if clauses:
        result += "**⚠️ CLAUSES IMPORTANTES**\n"
        for c in clauses[:3]:
            result += f"• {c}\n"
    
    return result


def format_as_scientific(text: str) -> str:
    """Format article scientifique."""
    bullets = extract_bullets(text)
    
    result = "## 🔬 RÉSUMÉ SCIENTIFIQUE\n\n"
    
    sections = {
        "Problématique": [],
        "Méthodologie": [],
        "Résultats": [],
        "Limites": []
    }
    
    for bullet in bullets:
        lower = bullet.lower()
        if 'méthod' in lower or 'protocole' in lower:
            sections["Méthodologie"].append(bullet)
        elif 'résultat' in lower or 'constat' in lower:
            sections["Résultats"].append(bullet)
        elif 'limit' in lower or 'biais' in lower:
            sections["Limites"].append(bullet)
        else:
            sections["Problématique"].append(bullet)
    
    for title, content in sections.items():
        if content:
            result += f"**📌 {title}**\n"
            for item in content[:3]:
                result += f"- {item}\n"
            result += "\n"
    
    return result