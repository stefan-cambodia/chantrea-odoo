from odoo import SUPERUSER_ID, api, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        if not self.env.context.get("chantrea_sans_accuse_reception"):
            tickets._chantrea_envoyer_accuse_reception()
        return tickets

    def _chantrea_envoyer_accuse_reception(self):
        """Accusé de réception au client, dans sa langue, publié dans le fil du
        ticket : la réponse du client revient dans le ticket."""
        modele = self.env.ref("chantrea_portail.modele_accuse_reception_ticket", raise_if_not_found=False)
        if not modele:
            return
        for ticket in self.filtered("partner_id.email"):
            # Publié par le compte système et signé par la société. Depuis l'espace
            # client, c'est le client qui crée le ticket : publié en son nom, il ne
            # serait ni signé par Chantrea ni notifié (Odoo ne notifie pas l'auteur
            # de l'action).
            ticket.with_user(SUPERUSER_ID).message_post_with_source(
                modele, subtype_xmlid="mail.mt_comment", author_id=ticket.company_id.partner_id.id)
