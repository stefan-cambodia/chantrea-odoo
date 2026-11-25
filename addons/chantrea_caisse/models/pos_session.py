from odoo import models


class PosSession(models.Model):
    _inherit = "pos.session"

    def _chantrea_riels_du_tiroir(self):
        """Dollars et riels entrés et sortis du tiroir pendant la session.

        Odoo compte le tiroir en dollars. Les billets en dollars sont comptés tels quels
        (dollars reçus − dollars rendus) ; les riels valent le reste, ce qui comprend les
        arrondis de chaque vente. Compter exactement les billets attendus ne crée donc aucun écart.
        Le fond de caisse est compté avec les dollars."""
        self.ensure_one()
        especes = self.payment_method_ids.filtered(lambda pm: pm.type == "cash")[:1]
        commandes = self._get_closed_orders()
        paiements = commandes.payment_ids.filtered(lambda p: p.payment_method_id == especes)
        recus = paiements.filtered(lambda p: not p.is_change)
        riels_recus = sum(recus.mapped("chantrea_montant_khr"))
        riels_rendus = sum(commandes.mapped("chantrea_rendu_khr"))
        dollars_recus = sum(p.chantrea_especes_usd if p.chantrea_montant_khr else p.amount for p in recus)
        dollars_rendus = 0.0
        for commande in commandes:
            if commande.chantrea_taux:
                dollars_rendus += commande.chantrea_rendu_usd
            else:
                # Vente enregistrée sans la caisse en riels : la monnaie a été rendue en dollars.
                dollars_rendus -= sum(paiements.filtered(
                    lambda p: p.is_change and p.pos_order_id == commande).mapped("amount"))
        return {
            "recus": riels_recus,
            "rendus": riels_rendus,
            "net": riels_recus - riels_rendus,
            "dollars_session": self.currency_id.round(dollars_recus - dollars_rendus),
        }

    def get_closing_control_data(self):
        donnees = super().get_closing_control_data()
        details = donnees.get("default_cash_details")
        if details:
            riels = self._chantrea_riels_du_tiroir()
            valeur = self.currency_id.round(details["payment_amount"] - riels["dollars_session"])
            riels["valeur_usd"] = valeur
            riels["dollars_attendus"] = self.currency_id.round(details["amount"] - valeur)
            # Taux qui ramène les riels attendus à leur valeur ; sans riels, le taux de la caisse.
            riels["taux"] = (riels["net"] / valeur) if riels["net"] and valeur else self.config_id.chantrea_taux_caisse
            details["chantrea_riels"] = riels
        return donnees
