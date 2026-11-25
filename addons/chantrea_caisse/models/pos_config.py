import math

from odoo import api, fields, models


def arrondir_riels(montant, pas, sens="proche"):
    """Arrondit un montant en riels au pas des billets (100 ៛ par défaut).
    sens = « haut » pour ce que le client doit payer (la caisse n'y perd jamais),
    « proche » pour la monnaie rendue. Même règle que static/src/js/riels.js."""
    pas = pas or 1
    if sens == "haut":
        return math.ceil(round(montant / pas, 6)) * pas
    return math.floor(montant / pas + 0.5) * pas


class PosConfig(models.Model):
    _inherit = "pos.config"

    chantrea_taux_mode = fields.Selection(
        [("officiel", "Official rate of the day"), ("fixe", "Fixed till rate")],
        string="Riel rate", default="officiel", required=True,
        help="Official rate: the last USD/KHR rate published by the GDT (or NBC), as on invoices. "
             "Fixed rate: the rate posted in the shop, for example 4,000 riels per dollar.")
    chantrea_taux_fixe = fields.Float(
        string="Fixed till rate", default=4000.0, digits=(12, 2),
        help="Riels for 1 US dollar, used when the till rate is fixed.")
    chantrea_arrondi_khr = fields.Integer(
        string="Riel rounding", default=100,
        help="Smallest riel note given back. Amounts to pay in riels are rounded up to it, "
             "change in riels to the nearest.")
    chantrea_taux_caisse = fields.Float(
        string="Till rate (riels per dollar)", compute="_compute_chantrea_taux_caisse", digits=(12, 2),
        help="Rate the till uses today. Read again each time the till is opened.")

    @api.depends("chantrea_taux_mode", "chantrea_taux_fixe")
    @api.depends_context("date")
    def _compute_chantrea_taux_caisse(self):
        Taux = self.env["res.currency.rate"]
        aujourd_hui = fields.Date.context_today(self)
        for config in self:
            if config.chantrea_taux_mode == "fixe":
                config.chantrea_taux_caisse = config.chantrea_taux_fixe
                continue
            enregistrement = Taux._chantrea_taux_a_la_date(aujourd_hui, config.company_id)
            config.chantrea_taux_caisse = enregistrement._chantrea_valeur(config.company_id) if enregistrement else 0.0

    _check_taux_fixe = models.Constraint(
        "CHECK(chantrea_taux_mode != 'fixe' OR chantrea_taux_fixe > 0)",
        "The fixed till rate must be greater than zero.",
    )
    _check_arrondi_khr = models.Constraint(
        "CHECK(chantrea_arrondi_khr > 0)",
        "The riel rounding must be greater than zero.",
    )
