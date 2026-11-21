from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _chantrea_adresse_ligne(self):
        """Adresse sur une ligne, pour les documents imprimés."""
        self.ensure_one()
        morceaux = [self.street, self.street2, self.city, self.state_id.name, self.country_id.name]
        return ", ".join(m for m in morceaux if m)
