# api/format_summary.py — Version robuste, extraction multi-formats
import re
import json

# ══════════════════════════════════════════════════════════════════════════════
# COUCHE 1 — NORMALISATION DES VALEURS NUMÉRIQUES
# ══════════════════════════════════════════════════════════════════════════════

def parse_decimal(raw: str) -> float | None:
    """
    Convertit '124,6' ou '124.6' ou '1 200 000' ou '1,200,000' en float.
    Détecte automatiquement le rôle de la virgule (séparateur décimal vs milliers).
    """
    if not raw:
        return None
    s = raw.strip()
    # Supprimer espaces et espaces insécables (séparateurs de milliers)
    s = re.sub(r'[\s\u00a0\u202f]', '', s)

    if ',' in s and '.' in s:
        # Ex: 1,200.50  → virgule = séparateur milliers, point = décimal
        if s.index(',') < s.index('.'):
            s = s.replace(',', '')
        else:
            s = s.replace('.', '').replace(',', '.')
    elif ',' in s:
        parts = s.split(',')
        # '1,200' → séparateur milliers  |  '124,6' → décimal
        if len(parts) == 2 and len(parts[1]) == 3 and parts[1].isdigit():
            s = s.replace(',', '')
        else:
            s = s.replace(',', '.')
    try:
        return float(s)
    except ValueError:
        return None


def format_value(raw_number: str, unit_str: str) -> str | None:
    """
    Retourne la valeur formatée en gardant le format d'origine pour la lisibilité.
    Ex: '124,6', 'M€'  →  '124,6 M€'
    """
    val = parse_decimal(raw_number)
    if val is None:
        return None
    unit = unit_str.strip() if unit_str else ""
    # Reformater le nombre avec virgule décimale (style français)
    if val == int(val):
        num_str = f"{int(val):,}".replace(',', '\u202f')
    else:
        num_str = raw_number.strip().replace('.', ',')
    return f"{num_str} {unit}".strip() if unit else num_str


# Patterns numériques réutilisables
_NUM = r'([\d]+(?:[,.\u202f\u00a0\s][\d]+)*)'
_UNIT_GROUP = (
    r'\s*(Md[€E]|M[€E]|M€|K[€E]|K€'
    r'|M\s*MAD|K\s*MAD|MAD|DH|€|\$'
    r'|milliards?\s*(?:d[\'u\u2019]euros?|€)?'
    r'|millions?\s*(?:d[\'u\u2019]euros?|€)?'
    r'|milliers?\s*(?:d[\'u\u2019]euros?|€)?)?'
)
_PCT_PATTERN = r'([\d]+(?:[,.][\d]+)?)\s*(%)'


# ══════════════════════════════════════════════════════════════════════════════
# COUCHE 2 — MOTEUR D'EXTRACTION GÉNÉRIQUE
# ══════════════════════════════════════════════════════════════════════════════

def _find_on_line(line: str, value_type: str = "money") -> tuple | None:
    """Extrait la première valeur numérique significative sur une ligne."""
    if value_type == "percent":
        # Cherche un % précédé ou non d'un +/-
        m = re.search(r'[+\-]?\s*([\d]+[,.][\d]+)\s*%', line)
        if not m:
            m = re.search(r'([\d]+[,.][\d]+)\s*%', line)
        if m:
            return m.group(1), '%'
        return None

    # Cherche nombre + unité optionnelle, en filtrant les années seules (4 chiffres)
    for m in re.finditer(_NUM + _UNIT_GROUP, line):
        num = m.group(1)
        unit = m.group(2) or ""
        num_clean = re.sub(r'[\s\u00a0\u202f,.]', '', num)
        # Ignorer les années isolées (4 chiffres sans unité)
        if re.fullmatch(r'\d{4}', num_clean) and not unit:
            continue
        # Ignorer les très petits nombres sans unité (probablement des indices)
        if re.fullmatch(r'\d{1,2}', num_clean) and not unit:
            continue
        return num, unit
    return None


def extract_kpi(text: str, keyword_patterns: list, value_type: str = "money") -> str | None:
    """
    Extrait un KPI en cherchant d'abord ligne par ligne (précis),
    puis globalement avec une fenêtre de 120 chars (fallback).
    """
    lines = text.split('\n')

    # ── Stratégie 1 : ligne par ligne ────────────────────────────────────────
    for kw in keyword_patterns:
        for line in lines:
            if re.search(kw, line, re.IGNORECASE):
                result = _find_on_line(line, value_type)
                if result:
                    num, unit = result
                    if value_type == "percent":
                        return f"{num.replace('.', ',')} %"
                    return format_value(num, unit)

    # ── Stratégie 2 : fenêtre glissante sur le texte complet ─────────────────
    for kw in keyword_patterns:
        if value_type == "percent":
            pattern = kw + r'.{0,80}?' + _PCT_PATTERN
        else:
            pattern = kw + r'.{0,120}?' + _NUM + _UNIT_GROUP
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if m:
            # Extraire tous les groupes numériques du match et prendre le dernier
            sub = m.group(0)
            matches = list(re.finditer(_NUM + _UNIT_GROUP, sub))
            for candidate in reversed(matches):
                num = candidate.group(1)
                unit = candidate.group(2) or ""
                num_clean = re.sub(r'[\s\u00a0\u202f,.]', '', num)
                if re.fullmatch(r'\d{4}', num_clean) and not unit:
                    continue
                if re.fullmatch(r'\d{1,2}', num_clean) and not unit:
                    continue
                if value_type == "percent":
                    return f"{num.replace('.', ',')} %"
                return format_value(num, unit)
    return None


# ══════════════════════════════════════════════════════════════════════════════
# COUCHE 3 — EXTRACTEURS PAR KPI
# ══════════════════════════════════════════════════════════════════════════════

def extract_chiffre_affaires(text: str) -> str | None:
    return extract_kpi(text, [
        r"chiffre\s*d.affaires\s*(?:consolid[eé]|net|total)?",
        r"\bCA\b(?!\s*\(contre)",
        r"revenus?\s*(?:consolid[eé]s?|totaux?)?",
        r"ventes?\s*(?:nettes?|totales?)?",
        r"s['\u2019](?:[eé]tablit|est)\s*[àa]",
    ], value_type="money")


def extract_croissance(text: str) -> str | None:
    """Cherche la croissance sur la ligne du CA en priorité."""
    lines = text.split('\n')
    for line in lines:
        if re.search(r"chiffre\s*d.affaires|\bCA\b", line, re.IGNORECASE):
            m = re.search(r'[+\-]\s*([\d]+[,.][\d]+)\s*%', line)
            if m:
                sign = '+' if '+' in m.group(0) or float(m.group(1).replace(',','.')) > 0 else '-'
                return f"{sign}{m.group(1).replace('.', ',')} %"
    return extract_kpi(text, [
        r"(?:progression|croissance|augmentation|hausse)\s*de\s*[+\-]?",
        r"en\s*(?:hausse|progression)\s*de\s*[+]?",
        r"taux\s*de\s*croissance",
        r"croissance\s*(?:annuelle|organique|du\s*CA)?",
    ], value_type="percent")


def extract_marge_brute(text: str) -> str | None:
    return extract_kpi(text, [
        r"marge\s*brute\s*(?:atteint|s['\u2019]établit|de|[eé]gale?)?",
        r"gross\s*(?:margin|profit)",
    ], value_type="money")


def extract_marge_brute_pct(text: str) -> str | None:
    """Extrait le % de marge brute ('soit 54,1 % du CA')."""
    for line in text.split('\n'):
        if re.search(r"marge\s*brute", line, re.IGNORECASE):
            m = re.search(r'soit\s*([\d]+[,.][\d]+)\s*%', line, re.IGNORECASE)
            if m:
                return f"{m.group(1).replace('.', ',')} %"
            m = re.search(r'([\d]+[,.][\d]+)\s*%\s*du\s*CA', line, re.IGNORECASE)
            if m:
                return f"{m.group(1).replace('.', ',')} %"
    return None


def extract_ebitda(text: str) -> str | None:
    return extract_kpi(text, [
        r"EBITDA",
        r"EBIT\b",
        r"exc[eé]dent\s*brut\s*d.exploitation",
        r"\bEBE\b",
        r"r[eé]sultat\s*(?:brut\s*)?d.exploitation",
    ], value_type="money")


def extract_resultat_net(text: str) -> str | None:
    return extract_kpi(text, [
        r"r[eé]sultat\s*net\s*(?:part\s*du\s*groupe|consolid[eé])?",
        r"b[eé]n[eé]fice\s*net",
        r"profit\s*net",
        r"r[eé]sultat\s*de\s*l.exercice",
        r"r[eé]sultat\s*apr[eè]s\s*imp[oô]t",
    ], value_type="money")


def extract_marge_nette(text: str) -> str | None:
    return extract_kpi(text, [
        r"marge\s*nette\s*(?:ressort|s['\u2019]établit|de|[eé]gale?)?",
        r"marge\s*nette",
        r"taux\s*de\s*marge\s*nette",
        r"profitabilit[eé]\s*nette",
    ], value_type="percent")


def extract_dividendes(text: str) -> str | None:
    """Cherche le dividende par action en priorité."""
    for line in text.split('\n'):
        if re.search(r"dividende", line, re.IGNORECASE):
            m = re.search(r'([\d]+[,.][\d]+)\s*[€$]\s*par\s*action', line, re.IGNORECASE)
            if m:
                return f"{m.group(1).replace('.', ',')} € / action"
            result = _find_on_line(line, "money")
            if result:
                num, unit = result
                return format_value(num, unit)
    return None


def extract_actifs(text: str) -> str | None:
    return extract_kpi(text, [
        r"actifs?\s*totaux?",
        r"total\s*(?:des\s*)?actifs?",
        r"total\s*bilan",
        r"somme\s*du\s*bilan",
    ], value_type="money")


def extract_capitaux_propres(text: str) -> str | None:
    return extract_kpi(text, [
        r"capitaux\s*propres",
        r"fonds\s*propres",
        r"avoir\s*des\s*actionnaires",
        r"equity\b",
    ], value_type="money")


def extract_tresorerie(text: str) -> str | None:
    return extract_kpi(text, [
        r"tr[eé]sorerie\s*(?:nette|disponible|totale)?",
        r"cash\s*(?:net|disponible)?",
        r"disponibilit[eé]s?",
        r"liquidit[eé]s?\s*(?:nettes?)?",
    ], value_type="money")


def extract_dette(text: str) -> str | None:
    return extract_kpi(text, [
        r"dette\s*(?:financi[eè]re\s*)?nette",
        r"endettement\s*(?:net|financier|total)?",
        r"dettes?\s*(?:financi[eè]res?|totales?)",
    ], value_type="money")


def extract_endettement(text: str) -> str | None:
    return extract_kpi(text, [
        r"ratio\s*d.endettement",
        r"(?:ratio\s*de\s*)?gearing",
        r"taux\s*d.endettement",
        r"levier\s*(?:financier)?",
    ], value_type="percent")


# ══════════════════════════════════════════════════════════════════════════════
# COUCHE 4 — TABLEAU DE BORD STANDARD (4 SECTIONS)
# ══════════════════════════════════════════════════════════════════════════════

def build_financial_dashboard(text: str) -> dict:
    """
    Tableau de bord financier structuré en 4 sections standard.
    """
    mb_val = extract_marge_brute(text)
    mb_pct = extract_marge_brute_pct(text)
    marge_brute_display = (
        f"{mb_val}  ({mb_pct})" if mb_val and mb_pct
        else mb_val or mb_pct
    )

    return {
        "revenus": {
            "label": "Revenus & Activité",
            "icon": "📈",
            "color": "#3B82F6",
            "kpis": [
                {"label": "Chiffre d'affaires", "value": extract_chiffre_affaires(text)},
                {"label": "Croissance",          "value": extract_croissance(text)},
                {"label": "Marge brute",         "value": marge_brute_display},
                {"label": "EBITDA / EBE",        "value": extract_ebitda(text)},
            ]
        },
        "rentabilite": {
            "label": "Rentabilité",
            "icon": "💰",
            "color": "#10B981",
            "kpis": [
                {"label": "Résultat net",  "value": extract_resultat_net(text)},
                {"label": "Marge nette",   "value": extract_marge_nette(text)},
                {"label": "Dividende",     "value": extract_dividendes(text)},
            ]
        },
        "bilan": {
            "label": "Structure du Bilan",
            "icon": "🏦",
            "color": "#8B5CF6",
            "kpis": [
                {"label": "Actifs totaux",         "value": extract_actifs(text)},
                {"label": "Capitaux propres",      "value": extract_capitaux_propres(text)},
                {"label": "Trésorerie nette",      "value": extract_tresorerie(text)},
                {"label": "Dette financière nette","value": extract_dette(text)},
            ]
        },
        "financement": {
            "label": "Financement & Risque",
            "icon": "⚖️",
            "color": "#F59E0B",
            "kpis": [
                {"label": "Ratio d'endettement", "value": extract_endettement(text)},
            ]
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# COUCHE 5 — RÉSUMÉ EXÉCUTIF NARRATIF
# ══════════════════════════════════════════════════════════════════════════════

def extract_executive_summary_financial(text: str) -> tuple:
    """
    Génère un résumé exécutif narratif à partir des KPIs extraits.
    Retourne (lignes_résumé, risques).
    """
    ca     = extract_chiffre_affaires(text)
    growth = extract_croissance(text)
    ebitda = extract_ebitda(text)
    rn     = extract_resultat_net(text)
    marge  = extract_marge_nette(text)
    cp     = extract_capitaux_propres(text)
    endet  = extract_endettement(text)
    treso  = extract_tresorerie(text)
    div    = extract_dividendes(text)

    lines = []

    if ca and growth:
        lines.append(f"Le chiffre d'affaires s'établit à <strong>{ca}</strong>, en progression de <strong>{growth}</strong>.")
    elif ca:
        lines.append(f"Le chiffre d'affaires atteint <strong>{ca}</strong>.")

    if ebitda:
        lines.append(f"L'EBITDA ressort à <strong>{ebitda}</strong>.")

    if rn and marge:
        lines.append(f"Le résultat net s'élève à <strong>{rn}</strong>, pour une marge nette de <strong>{marge}</strong>.")
    elif rn:
        lines.append(f"Le résultat net de l'exercice s'élève à <strong>{rn}</strong>.")

    if div:
        lines.append(f"Un dividende de <strong>{div}</strong> est proposé aux actionnaires.")

    if cp:
        lines.append(f"Les capitaux propres s'élèvent à <strong>{cp}</strong>.")
    if treso:
        lines.append(f"La trésorerie nette disponible est de <strong>{treso}</strong>.")
    if endet:
        try:
            pct = float(re.sub(r'[^\d.,]', '', endet).replace(',', '.'))
            niveau = "maîtrisé" if pct < 50 else "élevé — à surveiller"
        except ValueError:
            niveau = "à analyser"
        lines.append(f"Le ratio d'endettement de <strong>{endet}</strong> est {niveau}.")

    # Fallback : premières phrases informatives du document
    if not lines:
        for s in re.split(r'(?<=[.!?])\s+', text):
            s = s.strip()
            if (40 < len(s) < 250 and
                    any(kw in s.lower() for kw in
                        ['résultat', 'chiffre', 'bénéfice', 'marge', 'croissance', 'ebitda'])):
                lines.append(s)
                if len(lines) >= 3:
                    break

    # Risques explicitement mentionnés
    risks = []
    for m in re.finditer(
        r'(?:risque|menace|exposition|vulnérabilité|fragilité)[^.]{10,120}\.',
        text, re.IGNORECASE
    ):
        snippet = m.group(0).strip()
        if 20 < len(snippet) < 180:
            risks.append(snippet)

    return lines, risks[:3]


# ══════════════════════════════════════════════════════════════════════════════
# POINT D'ENTRÉE PRINCIPAL — RAPPORT FINANCIER
# ══════════════════════════════════════════════════════════════════════════════

def format_as_financial_full(text: str, instructions: str = "") -> str:
    """
    Retourne un JSON structuré avec résumé exécutif + tableau de bord.
    Les logs DEBUG sont affichés côté backend uniquement.
    """
    clean = clean_text_for_extraction(text)

    print("=" * 56)
    print("  [FINANCIAL] DEBUT EXTRACTION")
    print(f"  Texte nettoyé : {len(clean)} chars")
    print("=" * 56)

    exec_lines, risks = extract_executive_summary_financial(clean)
    dashboard = build_financial_dashboard(clean)

    # Logs qualité (backend uniquement — non visibles par l'utilisateur)
    total = sum(len(s["kpis"]) for s in dashboard.values())
    found = sum(1 for s in dashboard.values() for k in s["kpis"] if k["value"])
    print(f"\n  KPIs extraits : {found}/{total}\n")
    for section in dashboard.values():
        print(f"  [{section['icon']} {section['label']}]")
        for kpi in section["kpis"]:
            status = "OK" if kpi["value"] else "MANQUANT"
            print(f"    [{status:8s}] {kpi['label']:30s}: {kpi['value'] or '—'}")
    print("\n" + "=" * 56 + "\n")

    payload = {
        "type":              "financial",
        "title":             "RAPPORT FINANCIER — RÉSUMÉ EXÉCUTIF",
        "source":            "Rapport financier 2024",
        "executive_summary": exec_lines,
        "risks":             risks,
        "dashboard":         dashboard,
        # Rétrocompatibilité
        "data": {
            kpi["label"]: kpi["value"] or "—"
            for section in dashboard.values()
            for kpi in section["kpis"]
        }
    }
    return json.dumps(payload, ensure_ascii=False)


# ══════════════════════════════════════════════════════════════════════════════
# NETTOYAGE DU TEXTE
# ══════════════════════════════════════════════════════════════════════════════

def clean_text_for_extraction(text: str) -> str:
    """Nettoie sans perdre les valeurs numériques clés."""
    text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.MULTILINE)
    # Normaliser apostrophes et tirets typographiques
    text = text.replace('\u2019', "'").replace('\u2018', "'")
    text = text.replace('\u2013', '-').replace('\u2014', '-')
    # Espaces insécables → espace normale
    text = text.replace('\u00a0', ' ').replace('\u202f', ' ')
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()


# ══════════════════════════════════════════════════════════════════════════════
# UTILITAIRES PARTAGÉS (autres types de documents)
# ══════════════════════════════════════════════════════════════════════════════

def extract_bullets(text: str) -> list:
    return [
        re.sub(r'^[-•*]\s*', '', l.strip())
        for l in text.split('\n')
        if l.strip().startswith(('-', '•', '*')) and len(l.strip()) > 2
    ]


def detect_tables_and_charts(text: str) -> str:
    for p in [r'\|.*\|.*\|', r'\+-+\+', r'Tableau\s+\d+',
              r'Figure\s+\d+', r'Graphique\s+\d+']:
        if re.search(p, text, re.IGNORECASE):
            return ("\n\n**Note** : Le document contient des tableaux ou graphiques "
                    "représentés en texte. Les données visuelles peuvent être partiellement perdues.\n")
    return ""


def detect_contradictions(text: str) -> str:
    pairs = [
        (r'(oui|vrai|confirmé).{0,50}(non|faux|refusé)', "Affirmations contradictoires"),
        (r'(augmentation|hausse).{0,50}(diminution|baisse)',  "Évolution contradictoire"),
        (r'(obligation|doit).{0,50}(option|facultatif)',      "Nuance obligation/option"),
    ]
    found = [msg for pat, msg in pairs if re.search(pat, text, re.IGNORECASE)]
    if found:
        w = "\n\n**Avertissement** : Informations potentiellement contradictoires :\n"
        w += "".join(f"  • {c}\n" for c in found[:3])
        w += "\n> *Formulation prudente recommandée.*\n"
        return w
    return ""


def check_cascade_loss(original_text: str, summary_text: str) -> str:
    if not original_text:
        return ""
    rate = (1 - len(summary_text) / len(original_text)) * 100
    if rate > 30:
        return (f"\n\n**Alerte cascade** : Taux de compression {rate:.1f}% (>30%). "
                "Perte d'information significative possible.\n")
    return ""


def detect_language_mix(text: str) -> str:
    terms = list(set(re.findall(
        r'\b(?:API|NLP|LLM|ML|AI|REST|JSON|XML|HTTP|SDK|CLI|GUI|BERT|Transformer)\b', text)))
    if terms:
        return f"\n\n**Termes techniques conservés** : {', '.join(terms[:5])}\n"
    return ""


def extract_metadata(text: str) -> str:
    result = ""
    for label, pattern in [("Projet", r'Projet\s*[:\-]\s*(.+?)(?:\n|$)'),
                            ("Date",   r'Date\s*[:\-]\s*(.+?)(?:\n|$)')]:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            result += f"**{label}** : {m.group(1).strip()}\n"
    m = re.search(r'Participants\s*[:\-]\s*(.+?)(?:\n\n|\n\[)', text, re.DOTALL | re.IGNORECASE)
    if m:
        result += f"**Participants** : {m.group(1).strip().replace(chr(10), ', ')}\n"
    return result


def extract_exchanges_with_timestamps(text: str) -> list:
    pattern = r'\[(\d{2}:\d{2}:\d{2})\]\s*([A-Z0-9_]+)\s*:\s*(.+?)(?=\n\[|$)'
    return [
        f"**[{ts}] {spk}** : {content.strip()[:200]}"
        for ts, spk, content in re.findall(pattern, text, re.DOTALL)
        if content.strip()
    ]


def extract_executive_summary(text: str) -> list:
    m = re.search(
        r'(?:Synthèse|Executive Summary)[^\n]*\n(.*?)(?=\n\n|\n\[|\n\d+\.|\n\*\*)',
        text, re.DOTALL | re.IGNORECASE
    )
    if not m:
        return []
    return [
        re.sub(r'^[-*•]\s*', '', l.strip())
        for l in m.group(1).split('\n')
        if l.strip() and len(l.strip()) > 10
    ][:5]


def extract_action_items(text: str) -> list:
    table_m = re.search(r'\|.*\|.*\|\n\|[-:|]+\|\n((?:\|.*\|.*\|\n)+)', text)
    if table_m:
        actions = []
        for row in table_m.group(1).strip().split('\n'):
            cells = row.split('|')
            if len(cells) >= 3:
                resp, action = cells[1].strip(), cells[2].strip()
                deadline = cells[3].strip() if len(cells) > 3 else "À définir"
                if resp and action:
                    actions.append(f"**{resp}** : {action} (échéance : {deadline})")
        return actions
    return [m.strip() for m in re.findall(
        r'(?:Action|Tâche|Responsable)[^\n]*[:\-]\s*(.+?)(?:\n|$)', text, re.IGNORECASE
    )][:5]


def extract_decisions(text: str) -> list:
    return [m.strip() for m in re.findall(
        r'(?:Décision|Validé|Accepté)[^\n]*[:\-]\s*(.+?)(?:\n|$)', text, re.IGNORECASE
    ) if len(m.strip()) > 10]


def extract_pending_points(text: str) -> list:
    return [m.strip() for m in re.findall(
        r'(?:En suspens|À traiter|Point[^\n]*bloquant)[^\n]*[:\-]\s*(.+?)(?:\n|$)',
        text, re.DOTALL | re.IGNORECASE
    ) if len(m.strip()) > 10]


# ══════════════════════════════════════════════════════════════════════════════
# FORMATAGE PAR TYPE DE DOCUMENT
# ══════════════════════════════════════════════════════════════════════════════

def format_summary(summary_text: str, doc_type: str,
                   instructions: str = "", original_text: str = "") -> str:
    result = ""
    result += detect_tables_and_charts(original_text)
    result += detect_contradictions(original_text)
    result += check_cascade_loss(original_text, summary_text)
    result += detect_language_mix(original_text)
    formatters = {
        "compte_rendu_reunion":    format_as_actionable,
        "article_scientifique":    format_as_scientific,
        "contrat_juridique":       format_as_legal,
        "transcription_audio":     format_as_transcription,
        "documentation_technique": format_as_tech_guide,
    }
    fmt = formatters.get(doc_type)
    result += fmt(summary_text) if fmt else summary_text
    return result


def format_as_actionable(text: str) -> str:
    bullets = extract_bullets(text)
    result = "## COMPTE-RENDU ACTIONNABLE\n\n"
    decisions, tasks, pending = [], [], []
    for b in bullets:
        lower = b.lower()
        if any(k in lower for k in ['décision', 'validé', 'acté']):   decisions.append(b)
        elif any(k in lower for k in ['tâche', 'assigné', 'doit']):   tasks.append(b)
        elif any(k in lower for k in ['suspend', 'attente']):          pending.append(b)
        else:                                                           decisions.append(b)
    if decisions: result += "**DÉCISIONS ACTÉES**\n" + "".join(f"- {d}\n" for d in decisions[:5]) + "\n"
    if tasks:     result += "**TÂCHES ASSIGNÉES**\n" + "".join(f"- {t}\n" for t in tasks[:5])
    if pending:   result += "\n**POINTS EN SUSPENS**\n" + "".join(f"- {p}\n" for p in pending[:3])
    return result


def format_as_transcription(text: str) -> str:
    result = "CHRONOLOGIE THÉMATIQUE\n\n"
    meta = extract_metadata(text)
    if meta: result += meta + "\n"
    exchanges = extract_exchanges_with_timestamps(text)
    if exchanges: result += "**ÉCHANGES CLÉS**\n\n" + "".join(f"{e}\n" for e in exchanges[:10]) + "\n"
    summary = extract_executive_summary(text)
    if summary: result += "**SYNTHÈSE**\n\n" + "".join(f"• {s}\n" for s in summary) + "\n"
    actions = extract_action_items(text)
    if actions: result += "**ACTIONS À RÉALISER**\n\n" + "".join(f"• {a}\n" for a in actions[:5]) + "\n"
    decisions = extract_decisions(text)
    if decisions: result += "**DÉCISIONS PRISES**\n\n" + "".join(f"• {d}\n" for d in decisions[:3]) + "\n"
    pending = extract_pending_points(text)
    if pending: result += "**POINTS EN SUSPENS**\n\n" + "".join(f"• {p}\n" for p in pending[:3])
    return result


def format_as_legal(text: str) -> str:
    bullets = extract_bullets(text)
    result = "SYNTHÈSE OPÉRATIONNELLE DU CONTRAT\n\n"
    parties, objet, obligations, dates, clauses = [], [], [], [], []
    for b in bullets:
        lower = b.lower()
        if any(k in lower for k in ['partie', 'contractant']):            parties.append(b)
        elif any(k in lower for k in ['objet', 'obligation']):            objet.append(b)
        elif any(k in lower for k in ['doit', 'tenu', 'responsabilité']): obligations.append(b)
        elif any(k in lower for k in ['date', 'délai']):                  dates.append(b)
        elif any(k in lower for k in ['clause', 'résiliation']):          clauses.append(b)
    for title, items in [("PARTIES CONTRACTANTES", parties), ("OBJET DU CONTRAT", objet),
                         ("OBLIGATIONS RÉCIPROQUES", obligations), ("DATES ET DÉLAIS CLÉS", dates),
                         ("CLAUSES IMPORTANTES", clauses)]:
        if items:
            result += f"**{title}**\n" + "".join(f"• {i}\n" for i in items[:4]) + "\n"
    return result


def format_as_scientific(text: str) -> str:
    bullets = extract_bullets(text)
    result = "## RÉSUMÉ SCIENTIFIQUE\n\n"
    sections = {"Problématique": [], "Méthodologie": [], "Résultats": [], "Limites": []}
    for b in bullets:
        lower = b.lower()
        if any(k in lower for k in ['méthod', 'protocole']):   sections["Méthodologie"].append(b)
        elif any(k in lower for k in ['résultat', 'constat']): sections["Résultats"].append(b)
        elif any(k in lower for k in ['limit', 'biais']):      sections["Limites"].append(b)
        else:                                                   sections["Problématique"].append(b)
    for title, items in sections.items():
        if items:
            result += f"**{title}**\n" + "".join(f"- {i}\n" for i in items[:3]) + "\n"
    return result


def format_as_tech_guide(text: str) -> str:
    bullets = extract_bullets(text)
    result = "## GUIDE TECHNIQUE RAPIDE\n\n"
    prereqs, steps, troubleshoot, links = [], [], [], []
    for b in bullets:
        lower = b.lower()
        if any(k in lower for k in ['prérequis', 'requis']):  prereqs.append(b)
        elif any(k in lower for k in ['étape', 'configur']):  steps.append(b)
        elif any(k in lower for k in ['erreur', 'bug']):      troubleshoot.append(b)
        elif any(k in lower for k in ['lien', 'http']):       links.append(b)
        else:                                                  steps.append(b)
    for title, items in [("PRÉREQUIS", prereqs), ("ÉTAPES", steps),
                          ("DÉPANNAGE", troubleshoot), ("LIENS UTILES", links)]:
        if items:
            result += f"**{title}**\n" + "".join(f"- {i}\n" for i in items[:5]) + "\n"
    return result