"""Matériel du client dans son espace : lecture seule, sans notes internes ni fournisseur.

Les recherches se font avec les droits du client (règle « matériel de la société
du client ») ; l'affichage utilise ensuite les enregistrements en sudo, limités par
le gabarit aux champs prévus pour le client.
"""
from odoo import http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.portal.controllers.portal import pager as portal_pager


class ChantreaParcPortail(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "equipment_count" in counters:
            Equipement = request.env["fsm.equipment"]
            values["equipment_count"] = Equipement.search_count([]) if Equipement.has_access("read") else 0
        return values

    @http.route(["/my/equipments", "/my/equipments/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_equipments(self, page=1, **kw):
        Equipement = request.env["fsm.equipment"]
        if not Equipement.has_access("read"):
            return request.redirect("/my")
        total = Equipement.search_count([])
        pager = portal_pager(url="/my/equipments", total=total, page=page, step=self._items_per_page)
        equipements = Equipement.search(
            [], order="chantrea_categorie, name", limit=self._items_per_page, offset=pager["offset"])
        values = self._prepare_portal_layout_values()
        values.update({
            "equipements": equipements.sudo(),
            "page_name": "equipment",
            "pager": pager,
            "default_url": "/my/equipments",
        })
        return request.render("chantrea_parc.portal_my_equipments", values)

    @http.route(["/my/equipment/<int:equipment_id>"], type="http", auth="user", website=True)
    def portal_my_equipment(self, equipment_id, **kw):
        try:
            equipement = self._document_check_access("fsm.equipment", equipment_id)
        except (AccessError, MissingError):
            return request.redirect("/my")
        # Tickets et interventions : seulement ce que le client a le droit de voir.
        tickets = request.env["helpdesk.ticket"].search([("id", "in", equipement.chantrea_ticket_ids.ids)])
        interventions = request.env["fsm.order"].search([("equipment_ids", "in", equipement.ids)])
        values = self._prepare_portal_layout_values()
        values.update({
            "equipement": equipement,
            "tickets": tickets.sudo(),
            "interventions": interventions.sudo(),
            "page_name": "equipment",
        })
        return request.render("chantrea_parc.portal_my_equipment", values)
