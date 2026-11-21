from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    chantrea_nom_km = fields.Char(related="company_id.chantrea_nom_km", readonly=False)
    chantrea_taux_source = fields.Selection(related="company_id.chantrea_taux_source", readonly=False)
    chantrea_taux_alerte_user_id = fields.Many2one(
        related="company_id.chantrea_taux_alerte_user_id", readonly=False)

    def action_chantrea_recuperer_taux(self):
        """Bouton « Récupérer le taux maintenant »."""
        self.ensure_one()
        resultat = self.env["res.currency.rate"]._chantrea_recuperer_taux(self.company_id)
        if resultat["problemes"]:
            message, genre = "\n".join(resultat["problemes"]), "warning"
        else:
            message, genre = self.env._(
                "%(count)s new rate(s) recorded. Rate in force: %(rate)s KHR (%(date)s).",
                count=len(resultat["crees"]),
                rate=resultat["taux_en_vigueur"] or "-",
                date=resultat["date_en_vigueur"] or "-",
            ), "success"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {"title": self.env._("USD/KHR exchange rate"), "message": message,
                       "type": genre, "sticky": genre == "warning"},
        }
