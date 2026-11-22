from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    chantrea_equipement_ids = fields.Many2many(
        "fsm.equipment", "chantrea_equipement_ticket_rel", "ticket_id", "equipment_id", string="Equipment",
        domain="[('chantrea_client_id', 'parent_of', partner_id)]")

    def action_create_order(self):
        """Intervention créée depuis le ticket : elle reprend ses équipements."""
        action = super().action_create_order()
        if self.chantrea_equipement_ids:
            action.setdefault("context", {})
            action["context"] = dict(action["context"],
                                     default_equipment_ids=[(6, 0, self.chantrea_equipement_ids.ids)])
        return action
