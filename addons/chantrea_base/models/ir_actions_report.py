from odoo import models

from odoo.addons.chantrea_base.outils_km import OutilsKm


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _get_rendering_context(self, report, docids, data):
        """Ajoute « km » (chiffres et dates en khmer) aux valeurs de tous les rapports."""
        data = super()._get_rendering_context(report, docids, data)
        data.setdefault("km", OutilsKm(self.env))
        return data
