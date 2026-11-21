import re

from odoo import api, fields, models
from odoo.exceptions import UserError

from . import montants_khr
from .res_currency_rate import SOURCES_TAUX

TYPES_FACTURE = [
    ("tva", "VAT invoice"),
    ("commerciale", "Commercial invoice"),
]


class AccountMove(models.Model):
    _inherit = "account.move"

    chantrea_type_facture = fields.Selection(
        TYPES_FACTURE, string="Cambodian invoice type",
        compute="_compute_chantrea_type_facture", store=True, readonly=False, precompute=True,
        tracking=True,
        help="VAT invoice: the customer's VAT number (VATTIN) is required.\n"
             "Commercial invoice: for customers not registered for VAT.",
    )
    chantrea_taux_khr = fields.Float(
        "USD/KHR rate", digits=(12, 2), copy=False, tracking=True,
        help="Riels for 1 US dollar. Fixed when the invoice is confirmed, from the official "
             "rate in force on the invoice date. Can be entered by hand on a draft.",
    )
    chantrea_taux_date = fields.Date("Rate date", copy=False, tracking=True)
    chantrea_taux_source = fields.Selection(SOURCES_TAUX, string="Rate source", copy=False, tracking=True)

    chantrea_devise_khr_id = fields.Many2one(
        "res.currency", string="Riel currency", default=lambda self: self.env.ref("base.KHR"), readonly=True)
    chantrea_devise_usd_id = fields.Many2one(
        "res.currency", string="US dollar currency", default=lambda self: self.env.ref("base.USD"), readonly=True)
    chantrea_ht_khr = fields.Monetary(
        "Untaxed amount (KHR)", currency_field="chantrea_devise_khr_id",
        compute="_compute_chantrea_montants", store=True)
    chantrea_tva_khr = fields.Monetary(
        "VAT (KHR)", currency_field="chantrea_devise_khr_id",
        compute="_compute_chantrea_montants", store=True)
    chantrea_total_khr = fields.Monetary(
        "Total (KHR)", currency_field="chantrea_devise_khr_id",
        compute="_compute_chantrea_montants", store=True)
    chantrea_total_usd = fields.Monetary(
        "Total (USD)", currency_field="chantrea_devise_usd_id",
        compute="_compute_chantrea_montants", store=True)

    # ------------------------------------------------------------------
    # Calculs
    # ------------------------------------------------------------------
    def _chantrea_est_facture_client(self):
        return self.move_type in ("out_invoice", "out_refund")

    @api.depends("partner_id", "move_type")
    def _compute_chantrea_type_facture(self):
        for move in self:
            if not move._chantrea_est_facture_client():
                move.chantrea_type_facture = False
            elif move.state == "draft" or not move.chantrea_type_facture:
                vat = move.partner_id.commercial_partner_id.vat
                move.chantrea_type_facture = "tva" if vat else "commerciale"

    def _chantrea_montants(self, taux):
        self.ensure_one()
        return montants_khr.calculer(
            self.currency_id, self.amount_untaxed, self.amount_tax, self.amount_total, taux,
            self.env.ref("base.USD"), self.env.ref("base.KHR"))

    @api.depends("amount_untaxed", "amount_tax", "amount_total", "currency_id", "chantrea_taux_khr")
    def _compute_chantrea_montants(self):
        for move in self:
            valeurs = move._chantrea_montants(move.chantrea_taux_khr) or {}
            move.chantrea_ht_khr = valeurs.get("ht_khr", 0.0)
            move.chantrea_tva_khr = valeurs.get("tva_khr", 0.0)
            move.chantrea_total_khr = valeurs.get("total_khr", 0.0)
            move.chantrea_total_usd = valeurs.get("total_usd", 0.0)

    # ------------------------------------------------------------------
    # Validation : contrôle du type et taux figé
    # ------------------------------------------------------------------
    def _post(self, soft=True):
        # Contrôles AVANT la validation : rien n'est validé si l'un d'eux échoue.
        for move in self.filtered(lambda m: m._chantrea_est_facture_client()):
            move._chantrea_verifier_type()
            move._chantrea_verifier_taux_disponible()
        posted = super()._post(soft)
        for move in posted.filtered(lambda m: m._chantrea_est_facture_client()):
            move._chantrea_fixer_taux()
        return posted

    def _chantrea_trouver_taux(self):
        """Taux officiel en vigueur à la date de la facture (enregistrement, ou vide)."""
        jour = self.invoice_date or fields.Date.context_today(self)
        return self.env["res.currency.rate"]._chantrea_taux_a_la_date(jour, self.company_id)

    def _chantrea_verifier_taux_disponible(self):
        self.ensure_one()
        if self.chantrea_taux_khr or (self.move_type == "out_refund" and self.reversed_entry_id.chantrea_taux_khr):
            return
        if not self._chantrea_trouver_taux():
            raise UserError(self.env._(
                "No USD/KHR exchange rate is recorded on or before %(date)s: the invoice cannot be confirmed.\n"
                "Enter the official rate in Invoicing › Configuration › USD/KHR rates, "
                "or on the invoice itself (Cambodia tab).",
                date=self.invoice_date or fields.Date.context_today(self)))

    def _chantrea_verifier_type(self):
        self.ensure_one()
        _ = self.env._
        if self.currency_id not in (self.env.ref("base.USD") | self.env.ref("base.KHR")):
            raise UserError(_("Customer invoices must be in US dollars or riels (%(name)s).", name=self.display_name))
        if not self.chantrea_type_facture:
            raise UserError(_("Choose the Cambodian invoice type (VAT or commercial) for %(name)s.",
                              name=self.display_name))
        client = self.partner_id.commercial_partner_id
        if self.chantrea_type_facture == "tva" and not client.vat:
            raise UserError(_(
                "A VAT invoice requires the customer's VAT number (VATTIN).\n"
                "Enter it on the customer « %(partner)s », or choose « Commercial invoice ».",
                partner=client.display_name))

    def _chantrea_fixer_taux(self):
        """Mémorise sur la facture le taux, sa date et sa source. N'invente jamais de taux."""
        self.ensure_one()
        if self.chantrea_taux_khr:  # saisi à la main sur le brouillon
            self.write({
                "chantrea_taux_source": self.chantrea_taux_source or "manuel",
                "chantrea_taux_date": self.chantrea_taux_date or self.invoice_date,
            })
            return
        origine = self.reversed_entry_id
        if self.move_type == "out_refund" and origine.chantrea_taux_khr:
            # Un avoir reprend le taux de la facture qu'il annule.
            self.write({
                "chantrea_taux_khr": origine.chantrea_taux_khr,
                "chantrea_taux_date": origine.chantrea_taux_date,
                "chantrea_taux_source": origine.chantrea_taux_source,
            })
            return
        taux = self._chantrea_trouver_taux()
        if not taux:  # contrôlé avant validation ; ne devrait pas arriver
            raise UserError(self.env._("No USD/KHR exchange rate is recorded on or before %(date)s.",
                                       date=self.invoice_date))
        self.write({
            "chantrea_taux_khr": taux._chantrea_valeur(self.company_id),
            "chantrea_taux_date": taux.name,
            "chantrea_taux_source": taux.chantrea_source or "manuel",
        })

    def button_draft(self):
        res = super().button_draft()
        # Remis en brouillon : le taux sera de nouveau fixé à la validation,
        # sauf s'il avait été saisi à la main.
        self.filtered(lambda m: m._chantrea_est_facture_client() and m.chantrea_taux_source != "manuel").write({
            "chantrea_taux_khr": 0.0,
            "chantrea_taux_date": False,
            "chantrea_taux_source": False,
        })
        return res

    # ------------------------------------------------------------------
    # Numérotation : une seule série continue, sans remise à zéro annuelle
    # ------------------------------------------------------------------
    def _get_starting_sequence(self):
        sequence = super()._get_starting_sequence()
        if self.journal_id.type == "sale" and self._chantrea_est_facture_client():
            # « INV/2026/00000 » devient « INV/000000 » (et « RINV/000000 » pour les avoirs).
            sequence = re.sub(r"/\d{2,4}(?:-\d{2})?/0+$", "/000000", sequence)
        return sequence

    # ------------------------------------------------------------------
    # Impression
    # ------------------------------------------------------------------
    def _get_name_invoice_report(self):
        self.ensure_one()
        if self._chantrea_est_facture_client():
            return "chantrea_kh_facture.document_facture_kh"
        return super()._get_name_invoice_report()

    def _chantrea_valeurs_impression(self):
        """Taux et montants à imprimer. Sur un brouillon : taux provisoire (non mémorisé)."""
        self.ensure_one()
        if self.chantrea_taux_khr:
            taux, jour, source = self.chantrea_taux_khr, self.chantrea_taux_date, self.chantrea_taux_source
        else:
            jour_facture = self.invoice_date or fields.Date.context_today(self)
            enregistrement = self.env["res.currency.rate"]._chantrea_taux_a_la_date(jour_facture, self.company_id)
            taux = enregistrement._chantrea_valeur(self.company_id) if enregistrement else 0.0
            jour, source = enregistrement.name, enregistrement.chantrea_source
        return {
            "taux": taux,
            "date": jour,
            "source": source,
            "provisoire": self.state != "posted",
            "montants": self._chantrea_montants(taux),
        }
