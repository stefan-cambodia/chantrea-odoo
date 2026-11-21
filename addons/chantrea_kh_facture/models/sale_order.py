from odoo import fields, models

from . import montants_khr


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _chantrea_valeurs_impression(self):
        """Montant indicatif en riels au taux officiel en vigueur à la date du devis."""
        self.ensure_one()
        if self.date_order:
            jour = fields.Datetime.context_timestamp(self, self.date_order).date()
        else:
            jour = fields.Date.context_today(self)
        enregistrement = self.env["res.currency.rate"]._chantrea_taux_a_la_date(jour, self.company_id)
        taux = enregistrement._chantrea_valeur(self.company_id) if enregistrement else 0.0
        return {
            "taux": taux,
            "date": enregistrement.name,
            "source": enregistrement.chantrea_source,
            "provisoire": True,
            "montants": montants_khr.calculer(
                self.currency_id, self.amount_untaxed, self.amount_tax, self.amount_total, taux,
                self.env.ref("base.USD"), self.env.ref("base.KHR")),
        }
