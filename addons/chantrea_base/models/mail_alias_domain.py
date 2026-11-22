from odoo import fields, models, tools


class MailAliasDomain(models.Model):
    _inherit = "mail.alias.domain"

    # Odoo propose « notifications » : dès que le domaine d'alias est créé (réception des
    # courriels, docs/DEPLOIEMENT.md), tous les courriels partiraient de
    # notifications@domaine, une adresse que le service d'envoi n'autorise pas forcément.
    # On propose à la place EMAIL_FROM (.env), la seule adresse d'expédition autorisée.
    default_from = fields.Char(default=lambda self: tools.config.get("email_from") or "notifications")
