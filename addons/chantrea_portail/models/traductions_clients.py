"""Traductions des textes d'Odoo et de l'OCA vus par les clients.

Odoo 19 et les modules OCA n'ont presque pas de traduction khmère (1 à 17 %), et
il manque quelques textes français dans les modules OCA. Nos traductions sont
dans i18n_clients/<langue>*.po, sans toucher aux fichiers d'Odoo ni de l'OCA :

- les textes stockés en base (pages de l'espace client, champs, pays, courriels)
  sont importés ici : en entier à chaque installation ou mise à jour de ce module
  (data/traductions.xml), et pour un module donné chaque fois qu'Odoo recharge
  les traductions de ce module (installation, mise à jour, activation d'une langue) ;
- les textes écrits dans le code Python ou JavaScript sont lus dans les mêmes
  fichiers par traductions_code.py.
"""
import logging

from odoo import api, models
from odoo.tools.translate import TranslationImporter

from ..traductions_code import fichiers_clients, references_par_module

_logger = logging.getLogger(__name__)


class ChantreaTraductionsClients(models.AbstractModel):
    _name = "chantrea.traductions.clients"
    _description = "Chantrea: translations of customer-facing Odoo/OCA texts"

    @api.model
    def _charger(self, modules=None, langues=None):
        """Importe i18n_clients/*.po ; `modules` et `langues` limitent l'import."""
        actives = set(self.env["res.lang"].search([]).mapped("code"))
        for langue in sorted(actives if langues is None else actives & set(langues)):
            for fichier in fichiers_clients(langue):
                xmlids = None
                if modules is not None:
                    index = references_par_module(fichier)
                    xmlids = set().union(*(index.get(module, ()) for module in modules))
                    if not xmlids:
                        continue
                importeur = TranslationImporter(self.env.cr, verbose=False)
                importeur.load_file(str(fichier), langue, xmlids=xmlids)
                # Nos fichiers font foi, y compris pour les enregistrements qu'Odoo protège
                # des mises à jour (modèles de courriel, étapes) : sans « force_overwrite »,
                # une traduction corrigée après relecture ne remplacerait pas l'ancienne.
                importeur.save(overwrite=True, force_overwrite=True)
                _logger.info("Traductions clients chargées : %s (%s%s)", fichier.name, langue,
                             "" if modules is None else ", " + ", ".join(modules))
        return True


class IrModuleModule(models.Model):
    _inherit = "ir.module.module"

    def _load_module_terms(self, modules, langs, overwrite=False):
        """Après les traductions d'un module, remet les nôtres pour ce module.

        Sans cela, un module installé ou mis à jour APRÈS chantrea_portail, ou une
        langue réactivée, laisserait ses pages client sans traduction khmère.
        """
        resultat = super()._load_module_terms(modules, langs, overwrite=overwrite)
        self.env["chantrea.traductions.clients"]._charger(modules=list(modules), langues=langs)
        return resultat


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    def _load(self, *args, **kwargs):
        """Le plan comptable crée ses taxes et groupes de taxes APRÈS l'installation des
        modules : nos traductions (« VAT 10% » sur un devis) sont remises à ce moment-là.
        """
        resultat = super()._load(*args, **kwargs)
        self.env["chantrea.traductions.clients"]._charger(modules=["account"])
        return resultat
