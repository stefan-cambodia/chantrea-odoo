from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    chantrea_khqr_riels = fields.Boolean(
        string="QR code in riels",
        help="The KHQR code asks for the amount in riels, converted at the till rate "
             "and rounded up to the riel rounding. Otherwise it asks for dollars.")

    @api.model
    def _load_pos_data_fields(self, config):
        return super()._load_pos_data_fields(config) + ["qr_code_method", "chantrea_khqr_riels"]

    @api.constrains("chantrea_khqr_riels", "payment_method_type", "qr_code_method")
    def _check_chantrea_khqr_riels(self):
        for methode in self.filtered("chantrea_khqr_riels"):
            if methode.payment_method_type != "qr_code" or methode.qr_code_method != "emv_qr":
                raise ValidationError(_(
                    "Only a QR code payment method (EMV / KHQR) can ask for riels: %s.", methode.name))
