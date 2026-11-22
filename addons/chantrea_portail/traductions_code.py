"""Traductions des textes écrits dans le CODE d'Odoo et de l'OCA (Python et JavaScript).

Les textes stockés en base (pages, champs, courriels) sont importés par
models/traductions_clients.py. Ceux du code (tris et filtres des listes, fenêtre de
signature, messagerie d'un ticket…) ne passent pas par la base : Odoo les lit
dans le dossier i18n du module qui les contient. Comme on ne modifie ni Odoo ni
l'OCA, ce fichier complète cette lecture avec nos fichiers i18n_clients/<langue>*.po.

Branché par « post_load » (manifeste) : c'est le point d'extension prévu par Odoo
pour ce genre de complément. En cas de problème, le complément est ignoré et le
texte reste en anglais : il ne peut pas bloquer Odoo.
"""
import logging
import re
from pathlib import Path

import polib

from odoo.tools import file_path
from odoo.tools.translate import CodeTranslations

_logger = logging.getLogger(__name__)

# {langue de base ("km", "fr") : {module : [ligne, …]}}, lu une fois par processus.
_complements = {}


def fichiers_clients(langue):
    """Fichiers i18n_clients d'une langue : « km_KH » → km.po, km_pays.po…"""
    base = (langue or "").split("_")[0]
    try:
        dossier = Path(file_path("chantrea_portail/i18n_clients"))
    except FileNotFoundError:
        return []
    return sorted(f for f in dossier.glob("*.po") if f.stem == base or f.stem.startswith(base + "_"))


_references = {}  # {fichier : {module : {xmlid, …}}}, lu une fois par processus.


def references_par_module(fichier):
    """Enregistrements (pages, champs, étapes…) traduits par un fichier, par module d'origine."""
    cle = str(fichier)
    if cle not in _references:
        index = {}
        for entree in polib.pofile(cle):
            for reference, _ligne in entree.occurrences:
                if reference.startswith("model"):
                    xmlid = reference.rsplit(":", 1)[-1]
                    index.setdefault(xmlid.split(".", 1)[0], set()).add(xmlid)
        _references[cle] = index
    return _references[cle]


def _lignes_de_code(langue):
    base = (langue or "").split("_")[0]
    if base not in _complements:
        par_module = {}
        for fichier in fichiers_clients(base):
            for entree in polib.pofile(str(fichier)):
                if entree.obsolete or not entree.msgstr:
                    continue
                if not any(reference.startswith("code:") for reference, _ligne in entree.occurrences):
                    continue
                commentaires = entree.comment.split("\n")
                ligne = {
                    "type": "code", "src": entree.msgid, "value": entree.msgstr,
                    "comments": "\n".join(c for c in commentaires if not c.startswith("module")),
                }
                for commentaire in commentaires:
                    if commentaire.startswith("module"):
                        for module in re.findall(r"\w+", commentaire.split(":", 1)[-1]):
                            par_module.setdefault(module, []).append(ligne)
        _complements[base] = par_module
    return _complements[base]


def completer_traductions_du_code():
    """post_load : ajoute nos traductions à celles qu'Odoo lit dans chaque module."""
    if getattr(CodeTranslations._get_code_translations, "chantrea", False):
        return
    lecture_d_origine = CodeTranslations._get_code_translations

    def _get_code_translations(module_name, lang, filter_func):
        traductions = lecture_d_origine(module_name, lang, filter_func)
        try:
            for ligne in _lignes_de_code(lang).get(module_name, ()):
                if filter_func(ligne):
                    traductions[ligne["src"]] = ligne["value"]
        except Exception:
            _logger.exception("Complément de traduction ignoré (%s, %s)", module_name, lang)
        return traductions

    _get_code_translations.chantrea = True
    CodeTranslations._get_code_translations = staticmethod(_get_code_translations)
