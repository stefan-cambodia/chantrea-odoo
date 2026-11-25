from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pos_chantrea_taux_mode = fields.Selection(related="pos_config_id.chantrea_taux_mode", readonly=False)
    pos_chantrea_taux_fixe = fields.Float(related="pos_config_id.chantrea_taux_fixe", readonly=False)
    pos_chantrea_arrondi_khr = fields.Integer(related="pos_config_id.chantrea_arrondi_khr", readonly=False)
    pos_chantrea_taux_caisse = fields.Float(related="pos_config_id.chantrea_taux_caisse")
