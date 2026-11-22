from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _post(self, soft=True):
        valides = super()._post(soft)
        # La facture mensuelle d'un contrat est relue et validée : l'activité est faite.
        valides.activity_feedback(["chantrea_portail.activite_valider_facture"])
        return valides
