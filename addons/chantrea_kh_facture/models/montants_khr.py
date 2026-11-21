"""Conversion des totaux d'un document entre USD et KHR.

Règle d'arrondi (riel sans décimales, arrondi au plus proche, 0,5 vers le haut) :
- total KHR = arrondi(total USD × taux)
- TVA KHR   = arrondi(TVA USD × taux)
- HT KHR    = total KHR − TVA KHR   (la somme HT + TVA = total, toujours)
"""
from odoo.tools import float_round


def riel(valeur):
    return float_round(valeur, precision_rounding=1.0)


def calculer(devise, ht, tva, total, taux, usd, khr):
    """Renvoie les montants en KHR et le total en USD, ou None si incalculable."""
    if not taux or devise not in (usd, khr):
        return None
    if devise == usd:
        total_khr = riel(total * taux)
        tva_khr = riel(tva * taux)
        return {
            "ht_khr": total_khr - tva_khr,
            "tva_khr": tva_khr,
            "total_khr": total_khr,
            "total_usd": total,
        }
    # Document en riels : l'équivalent en dollars est donné pour information.
    return {
        "ht_khr": ht,
        "tva_khr": tva,
        "total_khr": total,
        "total_usd": usd.round(total / taux),
    }
