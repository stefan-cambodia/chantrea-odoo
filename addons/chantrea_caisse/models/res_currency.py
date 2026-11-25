from odoo import api, models
from odoo.fields import Domain


class ResCurrency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _load_pos_data_domain(self, data, config):
        """La caisse affiche aussi les montants en riels : le riel est chargé avec la devise de la caisse."""
        domaine = super()._load_pos_data_domain(data, config)
        khr = self.env.ref("base.KHR", raise_if_not_found=False)
        if not khr:
            return domaine
        return Domain.OR([[("id", "=", khr.id)], domaine])
