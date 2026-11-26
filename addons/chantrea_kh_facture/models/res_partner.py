from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _chantrea_adresse_ligne(self):
        """Adresse sur une ligne, pour les documents imprimés (khmer + anglais).

        Le pays est en anglais quelle que soit la langue de la personne qui imprime :
        le t-lang des modèles ne s'applique pas aux enregistrements qu'on leur passe.
        """
        self.ensure_one()
        pays = self.country_id.with_context(lang="en_US").name
        morceaux = [self.street, self.street2, self.city, self.state_id.name, pays]
        return ", ".join(m for m in morceaux if m)
