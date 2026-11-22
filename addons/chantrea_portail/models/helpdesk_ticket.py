from odoo import SUPERUSER_ID, api, models
from odoo.tools import formataddr


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model_create_multi
    def create(self, vals_list):
        tickets = super().create(vals_list)
        if not self.env.context.get("chantrea_sans_accuse_reception"):
            tickets._chantrea_envoyer_accuse_reception()
        return tickets

    @api.model
    def message_new(self, msg, custom_values=None):
        """Ticket créé par un courriel reçu : canal « Courriel ». L'OCA le déduit d'un
        contexte (« fetchmail_cron_running ») qu'Odoo 19 ne transmet plus à la création
        du ticket : le canal restait vide. Voir docs/CORRECTIFS_OCA.md."""
        valeurs = dict(custom_values or {})
        canal = self.env.ref("helpdesk_mgmt.helpdesk_ticket_channel_email", raise_if_not_found=False)
        if canal and not valeurs.get("channel_id"):
            valeurs["channel_id"] = canal.id
        return super().message_new(msg, custom_values=valeurs)

    def _chantrea_envoyer_accuse_reception(self):
        """Accusé de réception au client, dans sa langue, publié dans le fil du
        ticket : la réponse du client revient dans le ticket."""
        modele = self.env.ref("chantrea_portail.modele_accuse_reception_ticket", raise_if_not_found=False)
        if not modele:
            return
        adresse_par_defaut = self.env["ir.mail_server"]._get_default_from_address()
        for ticket in self.filtered("partner_id.email"):
            # Publié par le compte système et signé par la société. Depuis l'espace
            # client, c'est le client qui crée le ticket : publié en son nom, il ne
            # serait ni signé par Chantrea ni notifié (Odoo ne notifie pas l'auteur
            # de l'action).
            # L'expéditeur est donné ici : dès qu'on impose l'auteur, Odoo ne reprend
            # plus celui du modèle de courriel, et le client recevait une adresse nue,
            # sans le nom de la société. Si la société a une adresse, les réponses du
            # client y reviennent.
            societe = ticket.company_id
            expediteur = societe.partner_id.email_formatted or (
                adresse_par_defaut and formataddr((societe.name, adresse_par_defaut)))
            ticket.with_user(SUPERUSER_ID).message_post_with_source(
                modele, subtype_xmlid="mail.mt_comment",
                author_id=societe.partner_id.id, email_from=expediteur or False)
