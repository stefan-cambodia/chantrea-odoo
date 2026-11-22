from odoo import fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _recurring_create_invoice(self, date_ref=False):
        """Les factures mensuelles restent en brouillon (comportement OCA) : une
        activité « À valider » est posée sur chacune, pour qu'aucune n'échappe à la
        relecture. Le taux USD/KHR sera fixé à la validation."""
        factures = super()._recurring_create_invoice(date_ref)
        type_activite = self.env.ref("chantrea_portail.activite_valider_facture")
        # Sans conditions de paiement, Odoo prend la date du jour comme échéance :
        # pour une facture mensuelle, l'échéance est la date de la facture.
        for facture in factures.filtered(lambda f: not f.invoice_payment_term_id and f.invoice_date):
            facture.invoice_date_due = facture.invoice_date
        for facture in factures:
            contrat = self.filtered(lambda c: facture in c._get_related_invoices())[:1]
            responsable = (
                contrat.user_id
                or facture.company_id.chantrea_taux_alerte_user_id
                or self.env.ref("base.user_admin")
            )
            facture.activity_schedule(
                activity_type_id=type_activite.id,
                summary=self.env._("Validate the monthly invoice"),
                note=self.env._("Invoice created by contract %(contract)s. Check it, then confirm it.",
                                contract=contrat.display_name),
                user_id=responsable.id,
                date_deadline=facture.invoice_date or fields.Date.context_today(self),
            )
        return factures
