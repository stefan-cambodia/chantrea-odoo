import pytz

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from .fsm_equipment import contenu_interdit

CHAMPS_SURVEILLES = ("description", "todo", "resolution", "location_directions")


class FsmOrder(models.Model):
    _inherit = "fsm.order"

    # Instructions au technicien : internes, illisibles par le client (même par l'API).
    todo = fields.Html(groups="base.group_user")

    @api.constrains(*CHAMPS_SURVEILLES)
    def _check_chantrea_aucun_secret(self):
        for intervention in self:
            for champ in CHAMPS_SURVEILLES:
                if contenu_interdit(intervention.sudo()[champ]):
                    libelle = intervention._fields[champ]._description_string(self.env)
                    raise ValidationError(self.env._(
                        "« %(field)s » seems to contain an IP address, a password or a login. "
                        "Passwords, IP addresses and access credentials must never be stored in Odoo.",
                        field=libelle))

    def _get_report_base_filename(self):
        """Nom du PDF téléchargé depuis l'espace client."""
        self.ensure_one()
        return f"Service report - {self.name}"

    def _chantrea_heure_locale(self, valeur):
        """Date et heure dans le fuseau du site (Phnom Penh par défaut), quel que
        soit l'utilisateur qui imprime le rapport (un client n'a pas toujours de fuseau)."""
        if not valeur:
            return ""
        fuseau = pytz.timezone(self.location_id.tz or "Asia/Phnom_Penh")
        return pytz.utc.localize(valeur).astimezone(fuseau).strftime("%d/%m/%Y %H:%M")

    def _chantrea_client(self):
        """Société cliente de l'intervention (propriétaire du site)."""
        self.ensure_one()
        return (self.location_id.owner_id or self.location_id.partner_id).commercial_partner_id
