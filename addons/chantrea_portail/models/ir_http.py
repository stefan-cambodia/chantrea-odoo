from odoo import models
from odoo.http import request

# Modules dont le JavaScript affiche des textes dans l'espace client : messagerie
# d'un document (mail), double authentification, clés d'accès, liste des factures.
# Odoo ne charge leurs traductions côté client que si le module « website » est
# installé (c'est « website_mail » qui ajoute « mail ») : sans lui, ces textes
# restent en anglais dans toutes les langues. Voir docs/CORRECTIFS_OCA.md.
MODULES_JAVASCRIPT_CLIENT = ["mail", "auth_totp_portal", "auth_passkey_portal", "account_payment"]

# Langue d'un visiteur à sa première visite (ni langue dans l'adresse, ni cookie « frontend_lang »,
# pas connecté). Odoo prendrait celle du navigateur, et l'anglais à défaut.
LANGUE_PREMIERE_VISITE = "km_KH"


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        modules = super()._get_translation_frontend_modules_name()
        return modules + [m for m in MODULES_JAVASCRIPT_CLIENT if m not in modules]

    @classmethod
    def _match(cls, path):
        """Première visite en khmer, quelle que soit la langue du navigateur.

        Odoo choisit la langue des pages publiques dans cet ordre : adresse (/km/…, /en/…),
        cookie « frontend_lang », langue du contexte, langue par défaut. Pour un visiteur
        anonyme, la langue du contexte est celle de son navigateur (ou l'anglais) : on la
        remplace par le khmer. L'adresse et le cookie restent prioritaires, et Odoo pose le
        cookie dès la première page : le choix du sélecteur de langue est donc mémorisé.
        Les pages hors espace client (interface interne, API) ne sont pas concernées.
        """
        if hasattr(request, "is_frontend") or request.session.uid or request.cookies.get("frontend_lang"):
            return super()._match(path)
        env_navigateur = request.env
        request.update_context(lang=LANGUE_PREMIERE_VISITE)
        resultat = super()._match(path)  # peut rediriger vers /km/… (la réponse part aussitôt)
        if not getattr(request, "is_frontend", False):
            request.env = env_navigateur
        return resultat
