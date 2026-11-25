"""Chiffres et dates en khmer pour les documents imprimés.

- Chiffres khmers : ០ ១ ២ ៣ ៤ ៥ ៦ ៧ ៨ ៩ (U+17E0 à U+17E9).
- Date : « ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦ » (mois du calendrier solaire, comme le CLDR).
- Montants : même texte que la ligne anglaise, chiffres convertis. On garde volontairement
  les séparateurs anglais (1,234.50 → ១,២៣៤.៥០) plutôt que ceux du CLDR khmer
  (១.២៣៤,៥០) : les deux lignes d'un document se lisent ainsi chiffre pour chiffre.

Dans les gabarits de rapport, ces fonctions sont disponibles sous le nom « km »
(voir models/ir_actions_report.py) : km.date(d), km.date_heure(dt, fuseau), km.montant(v, devise),
km.champ(enregistrement, "champ") pour les cellules des tableaux.
"""
import datetime
import html
import re

import pytz

from odoo.tools.misc import formatLang

CHIFFRES = str.maketrans("0123456789", "០១២៣៤៥៦៧៨៩")

MOIS = (
    "មករា", "កុម្ភៈ", "មីនា", "មេសា", "ឧសភា", "មិថុនា",
    "កក្កដា", "សីហា", "កញ្ញា", "តុលា", "វិច្ឆិកា", "ធ្នូ",
)

FUSEAU_DEFAUT = "Asia/Phnom_Penh"


def chiffres(valeur):
    """Remplace les chiffres occidentaux par des chiffres khmers (le reste est gardé)."""
    if valeur is None or valeur is False:
        return ""
    return str(valeur).translate(CHIFFRES)


def date(jour):
    """date → « ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦ ». Un datetime est pris tel quel (déjà local)."""
    if not jour:
        return ""
    return f"ថ្ងៃទី{chiffres(f'{jour.day:02d}')} ខែ{MOIS[jour.month - 1]} ឆ្នាំ{chiffres(jour.year)}"


def heure_locale(moment, fuseau=None):
    """datetime UTC naïf (stockage Odoo) → datetime dans le fuseau donné (Phnom Penh par défaut)."""
    if not moment:
        return None
    if moment.tzinfo is None:
        moment = pytz.utc.localize(moment)
    return moment.astimezone(pytz.timezone(fuseau or FUSEAU_DEFAUT))


def date_heure(moment, fuseau=None):
    """datetime UTC naïf → « ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦ ម៉ោង ១៤:៣០ » à l'heure locale."""
    local = heure_locale(moment, fuseau)
    if not local:
        return ""
    return f"{date(local)} ម៉ោង {chiffres(local.strftime('%H:%M'))}"


class OutilsKm:
    """Objet passé aux gabarits sous le nom « km »."""

    def __init__(self, env):
        # Les documents sont rendus en anglais (t-lang="'en_US'") : mêmes séparateurs ici,
        # quelle que soit la langue de l'utilisateur qui imprime.
        self.env = env(context=dict(env.context, lang="en_US"))

    chiffres = staticmethod(chiffres)
    date_heure = staticmethod(date_heure)

    @staticmethod
    def date(jour):
        if isinstance(jour, datetime.datetime):
            # Un datetime d'Odoo est en UTC : on le ramène au jour de Phnom Penh.
            jour = heure_locale(jour)
        return date(jour)

    def nombre(self, valeur, decimales=0):
        """Nombre formaté comme en anglais (séparateur de milliers), chiffres khmers."""
        return chiffres(formatLang(self.env, valeur, digits=decimales))

    def montant(self, valeur, devise):
        """Montant avec symbole, formaté comme la ligne anglaise, chiffres khmers."""
        return chiffres(formatLang(self.env, valeur, currency_obj=devise))

    def champ(self, enregistrement, nom):
        """Valeur d'un champ telle que t-field l'imprime en anglais (mêmes décimales, symbole
        de la devise), chiffres khmers : « ៦.០០ », « $ ១៥០.០០ ». Pour les tableaux de lignes."""
        enregistrement = enregistrement.with_env(self.env)
        modele = f"ir.qweb.field.{enregistrement._fields[nom].type}"
        convertisseur = self.env[modele] if modele in self.env else self.env["ir.qweb.field"]
        rendu = convertisseur.record_to_html(enregistrement, nom, {})
        return chiffres(html.unescape(re.sub(r"<[^>]+>", "", str(rendu or ""))))
