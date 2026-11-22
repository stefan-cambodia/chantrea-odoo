"""Bases déjà installées : applique data/refus_inconnus.xml (l'adresse d'assistance
n'accepte que les contacts connus). Ce fichier est « noupdate » : une simple mise à jour
du module ne le relit pas."""
from odoo import SUPERUSER_ID, api
from odoo.tools import convert_file


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    convert_file(env, "chantrea_portail", "data/refus_inconnus.xml", None, mode="init", noupdate=True)
