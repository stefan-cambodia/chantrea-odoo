from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    chantrea_equipement_ids = fields.Many2many(
        "fsm.equipment", "chantrea_equipement_ticket_rel", "ticket_id", "equipment_id", string="Equipment",
        domain="[('chantrea_client_id', 'parent_of', partner_id)]")
