from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_chantrea_taux_mode = fields.Selection(related="pos_config_id.chantrea_taux_mode", readonly=False)
    pos_chantrea_taux_fixe = fields.Float(related="pos_config_id.chantrea_taux_fixe", readonly=False)
    pos_chantrea_arrondi_khr = fields.Integer(related="pos_config_id.chantrea_arrondi_khr", readonly=False)
    pos_chantrea_taux_caisse = fields.Float(related="pos_config_id.chantrea_taux_caisse")
    chantrea_bakong_token = fields.Char(
        string="Bakong API token", config_parameter="chantrea_caisse.bakong_token",
        groups="base.group_system",
        help="Token of the Bakong API of the National Bank of Cambodia (valid 90 days). "
             "With it, the till sees by itself that a KHQR code has been paid.")
    chantrea_bakong_url = fields.Char(
        string="Bakong API address", config_parameter="chantrea_caisse.bakong_url",
        groups="base.group_system",
        help="Empty: https://api-bakong.nbc.gov.kh. Test environment: https://sit-api-bakong.nbc.gov.kh.")
