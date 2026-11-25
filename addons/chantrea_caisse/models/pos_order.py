from odoo import fields, models

MODES_RENDU = [
    ("mixte", "Dollars + riels"),
    ("riels", "All in riels"),
    ("dollars", "All in dollars"),
]


class PosOrder(models.Model):
    _inherit = "pos.order"

    chantrea_taux = fields.Float(
        string="Till rate", digits=(12, 2), readonly=True,
        help="Riels for 1 US dollar, used by the till for this order.")
    chantrea_mode_rendu = fields.Selection(
        MODES_RENDU, string="Change given in", default="mixte", readonly=True,
        help="Dollars + riels: whole dollars in notes, the cents in riels (US coins do not circulate).")
    chantrea_rendu_usd = fields.Float(string="Change in dollars", digits=(12, 2), readonly=True)
    chantrea_rendu_khr = fields.Float(string="Change in riels", digits=(12, 0), readonly=True)


class PosPayment(models.Model):
    _inherit = "pos.payment"

    chantrea_especes_usd = fields.Float(
        string="Dollars received", digits=(12, 2), readonly=True,
        help="Cash: dollar notes handed over by the customer.")
    chantrea_montant_khr = fields.Float(
        string="Riels", digits=(12, 0), readonly=True,
        help="Cash: riel notes handed over by the customer. KHQR in riels: amount of the QR code.")
