"""Lecture du taux officiel USD/KHR publié en ligne.

Fonctions pures (sans Odoo) pour pouvoir être testées sur des pages
enregistrées. Elles ne renvoient QUE des valeurs lues sur la page :
jamais de valeur par défaut, jamais d'estimation.
"""
import re
from datetime import date

import requests

URL_GDT = "https://www.tax.gov.kh/en/exchange-rate"
URL_NBC = "https://www.nbc.gov.kh/english/economic_research/exchange_rate.php"

EN_TETES = {
    "User-Agent": "Mozilla/5.0 (compatible; ChantreaOdoo/1.0)",
    "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.8",
}

# Garde-fous : une valeur hors de ces bornes est rejetée, jamais corrigée.
TAUX_MIN, TAUX_MAX = 2000, 8000
ECART_MAX = 0.05  # 5 % d'écart maximum avec le taux précédent


class ErreurTaux(Exception):
    """Le taux n'a pas pu être lu de façon sûre."""


def _nombre(texte):
    return float(texte.replace(",", "").strip())


def analyser_gdt(page):
    """Page « Exchange Rate » du GDT : tableau Release Date / Symbol / Official Rate.

    Chaque ligne contient un bloc JSON-LD avec "datePublished": "AAAA-MM-JJ".
    Renvoie {date: taux}.
    """
    taux = {}
    for ligne in re.findall(r"<tr\b.*?</tr>", page, flags=re.S | re.I):
        if "USD/KHR" not in ligne:
            continue
        jour = re.search(r'"datePublished"\s*:\s*"(\d{4}-\d{2}-\d{2})"', ligne)
        valeurs = re.findall(r"<td[^>]*>\s*(\d[\d,]*(?:\.\d+)?)\s*</td>", ligne)
        if jour and len(valeurs) == 1:
            taux[date.fromisoformat(jour.group(1))] = _nombre(valeurs[0])
    return taux


def analyser_nbc(page):
    """Page « Exchange Rate » de la Banque nationale du Cambodge.

    « Exchange Rate on : AAAA-MM-JJ » puis « Official Exchange Rate : NNNN KHR / USD ».
    Renvoie {date: taux}.
    """
    texte = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page))
    jour = re.search(r"Exchange Rate on\s*:\s*(\d{4}-\d{2}-\d{2})", texte)
    valeur = re.search(r"Official Exchange Rate\s*:\s*(\d[\d,]*(?:\.\d+)?)\s*KHR\s*/\s*USD", texte)
    if jour and valeur:
        return {date.fromisoformat(jour.group(1)): _nombre(valeur.group(1))}
    return {}


SOURCES = {
    "gdt": (URL_GDT, analyser_gdt),
    "nbc": (URL_NBC, analyser_nbc),
}


def telecharger(source, timeout=30):
    """Télécharge et analyse la page de la source. Lève ErreurTaux en cas d'échec."""
    url, analyser = SOURCES[source]
    try:
        reponse = requests.get(url, headers=EN_TETES, timeout=timeout)
        reponse.raise_for_status()
    except requests.RequestException as erreur:
        raise ErreurTaux(f"{url} : {erreur}") from erreur
    taux = analyser(reponse.text)
    if not taux:
        raise ErreurTaux(f"{url} : format de page non reconnu, aucun taux lu")
    return taux


def verifier(valeur, precedent=None):
    """Renvoie un message d'erreur si la valeur est invraisemblable, sinon None."""
    if not TAUX_MIN <= valeur <= TAUX_MAX:
        return f"{valeur:g} hors de la plage plausible ({TAUX_MIN}–{TAUX_MAX})"
    if precedent and abs(valeur - precedent) / precedent > ECART_MAX:
        return f"{valeur:g} s'écarte de plus de {ECART_MAX:.0%} du taux précédent ({precedent:g})"
    return None
