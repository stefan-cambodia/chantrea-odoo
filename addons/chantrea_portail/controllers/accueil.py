"""Page d'accueil de l'espace client : tableau de bord Chantrea Systems.

Tous les comptes sont faits avec les droits du client connecté : les règles
d'accès limitent chaque chiffre aux données de SA société.
"""
from odoo import fields
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal

# Rubriques standard retirées de l'accueil des clients :
# - déjà présentes dans le tableau de bord (tickets, interventions, matériel,
#   contrats, devis, factures) ;
# - ou sans objet pour un client (projets, tâches et feuilles de temps internes,
#   achats et factures fournisseurs, signature de documents à distance, désactivée).
# Les pages elles-mêmes restent protégées par les droits et règles d'accès :
# ceci ne règle que ce que l'accueil propose.
RUBRIQUES_MASQUEES = frozenset({
    "/my/tickets", "/my/fsm_orders", "/my/equipments", "/my/contracts",
    "/my/quotes", "/my/invoices",
    "/my/projects", "/my/tasks", "/my/timesheets",
    "/my/rfq", "/my/purchase", "/my/sign_requests",
})


class ChantreaAccueil(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if not counters:  # page d'accueil (les compteurs JS passent une liste non vide)
            values["chantrea"] = self._chantrea_tableau_de_bord()
        return values

    def _chantrea_tableau_de_bord(self):
        env = request.env

        def compter(modele, domaine):
            Modele = env[modele]
            return Modele.search_count(domaine) if Modele.has_access("read") else 0

        aujourd_hui = fields.Date.context_today(env.user)
        factures = env["account.move"].search([
            ("move_type", "=", "out_invoice"), ("state", "=", "posted"),
            ("payment_state", "in", ("not_paid", "partial")),
        ]) if env["account.move"].has_access("read") else env["account.move"]
        usd = env.ref("base.USD")
        return {
            "tickets_ouverts": compter("helpdesk.ticket", [("closed", "=", False)]),
            "interventions_ouvertes": compter("fsm.order", [("stage_id.is_closed", "=", False)]),
            "interventions_total": compter("fsm.order", []),
            "contrats_actifs": compter("contract.contract", [
                "|", ("date_end", "=", False), ("date_end", ">=", aujourd_hui)]),
            "equipements": compter("fsm.equipment", []),
            "garanties_bientot": compter("fsm.equipment", [("chantrea_etat_garantie", "=", "bientot")]),
            "devis_a_valider": compter("sale.order", [("state", "=", "sent")]),
            "factures_a_payer": len(factures),
            "montant_a_payer": sum(factures.filtered(lambda f: f.currency_id == usd).mapped("amount_residual")),
            "devise_usd": usd,
            "societe": env.company.sudo(),
            "rubriques_masquees": RUBRIQUES_MASQUEES,
        }
