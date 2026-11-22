from odoo import models

# Modules dont le JavaScript affiche des textes dans l'espace client : messagerie
# d'un document (mail), double authentification, clés d'accès, liste des factures.
# Odoo ne charge leurs traductions côté client que si le module « website » est
# installé (c'est « website_mail » qui ajoute « mail ») : sans lui, ces textes
# restent en anglais dans toutes les langues. Voir docs/CORRECTIFS_OCA.md.
MODULES_JAVASCRIPT_CLIENT = ["mail", "auth_totp_portal", "auth_passkey_portal", "account_payment"]


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        modules = super()._get_translation_frontend_modules_name()
        return modules + [m for m in MODULES_JAVASCRIPT_CLIENT if m not in modules]
