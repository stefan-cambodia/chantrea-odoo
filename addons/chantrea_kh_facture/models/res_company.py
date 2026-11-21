from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    chantrea_nom_km = fields.Char(
        "Company name in Khmer",
        help="Printed above the Latin name on quotations and invoices. Leave empty until it is registered.",
    )
    chantrea_taux_source = fields.Selection(
        [("gdt", "GDT (General Department of Taxation)"),
         ("nbc", "NBC (National Bank of Cambodia)")],
        string="Official USD/KHR rate source",
        default="gdt",
        required=True,
    )
    chantrea_taux_alerte_user_id = fields.Many2one(
        "res.users",
        string="Exchange rate alerts sent to",
        default=lambda self: self.env.ref("base.user_admin", raise_if_not_found=False),
        domain=[("share", "=", False)],
    )
