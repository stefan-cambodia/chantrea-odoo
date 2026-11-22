"""Correctif de sécurité de la route OCA « /ticket/close » (sans modifier le code OCA).

La route d'origine (helpdesk_mgmt, 19.0) :
- retrouve le ticket en sudo à partir du seul « ticket_id » envoyé par le
  navigateur, sans vérifier qu'il appartient au client connecté : n'importe
  quel client connecté peut fermer le ticket d'un autre client ;
- accepte une requête GET, donc sans protection CSRF : un simple lien piégé
  suffit à fermer un ticket à l'insu du client.

Ici : POST uniquement (jeton CSRF vérifié par Odoo), ticket lu avec les droits
du client connecté (règles d'accès du portail), étape vérifiée.
"""
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.helpdesk_mgmt.controllers.main import HelpdeskTicketController


class ChantreaHelpdeskTicketController(HelpdeskTicketController):

    @http.route()
    def submit_ticket(self, **kw):
        """Contrôle côté serveur de la catégorie (l'OCA ne la vérifie que dans le
        navigateur) : obligatoire si le réglage l'exige, et toujours une catégorie
        proposée dans l'espace client."""
        categorie_id = kw.get("category")
        categories = self._get_categories()
        try:
            categorie_ok = not categorie_id or int(categorie_id) in categories.ids
        except ValueError:
            categorie_ok = False
        obligatoire = request.env.company.helpdesk_mgmt_portal_category_id_required
        if not categorie_ok or (obligatoire and categories and not categorie_id):
            return request.redirect("/new/ticket")
        return super().submit_ticket(**kw)

    def _prepare_submit_ticket_vals(self, **kw):
        """Un ticket ouvert depuis l'espace client va à l'équipe d'assistance
        (le client ne choisit pas d'équipe) : file d'attente et temps passé suivis."""
        vals = super()._prepare_submit_ticket_vals(**kw)
        if not vals.get("team_id"):
            equipe = request.env.ref("chantrea_portail.equipe_assistance", raise_if_not_found=False)
            if equipe:
                vals["team_id"] = equipe.id
                vals["stage_id"] = equipe.sudo()._get_applicable_stages()[:1].id or vals.get("stage_id")
        return vals

    @http.route("/ticket/close", type="http", auth="user", methods=["POST"])
    def support_ticket_close(self, **kw):
        try:
            ticket = request.env["helpdesk.ticket"].browse(int(kw.get("ticket_id") or 0))
            stage = request.env["helpdesk.ticket.stage"].browse(int(kw.get("stage_id") or 0))
            # Lecture avec les droits du client : lève AccessError si le ticket n'est pas à lui.
            ticket.check_access("read")
            ticket.ensure_one()
            stage.check_access("read")
        except (AccessError, MissingError, ValueError):
            raise NotFound() from None
        if stage.exists() and stage.close_from_portal and not ticket.closed_date:
            ticket.sudo().stage_id = stage
        return request.redirect(f"/my/ticket/{ticket.id}")
