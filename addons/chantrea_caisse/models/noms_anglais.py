"""Noms anglais chargés dans la caisse, pour le ticket khmer/anglais.

La caisse charge les noms dans la langue de la caissière (français) ; le ticket du client
écrit les données en anglais, comme les documents imprimés (rendus en en_US).
"""
from odoo import api, fields, models


def _calculer_nom_anglais(enregistrements, champ="name"):
    for enregistrement, anglais in zip(enregistrements, enregistrements.with_context(lang="en_US")):
        enregistrement.chantrea_nom_en = anglais[champ] or ""


class ProductTemplate(models.Model):
    _inherit = "product.template"

    chantrea_nom_en = fields.Char(string="English name", compute="_compute_chantrea_nom_en")

    @api.depends("name")
    def _compute_chantrea_nom_en(self):
        _calculer_nom_anglais(self)

    @api.model
    def _load_pos_data_fields(self, config_id):
        return super()._load_pos_data_fields(config_id) + ["chantrea_nom_en"]


class UomUom(models.Model):
    _inherit = "uom.uom"

    chantrea_nom_en = fields.Char(string="English name", compute="_compute_chantrea_nom_en")

    @api.depends("name")
    def _compute_chantrea_nom_en(self):
        _calculer_nom_anglais(self)

    @api.model
    def _load_pos_data_fields(self, config):
        return super()._load_pos_data_fields(config) + ["chantrea_nom_en"]


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    chantrea_nom_en = fields.Char(string="English name", compute="_compute_chantrea_nom_en")

    @api.depends("name")
    def _compute_chantrea_nom_en(self):
        _calculer_nom_anglais(self)

    @api.model
    def _load_pos_data_fields(self, config):
        return super()._load_pos_data_fields(config) + ["chantrea_nom_en"]


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    chantrea_nom_en = fields.Char(string="English name", compute="_compute_chantrea_nom_en")

    @api.depends("name")
    def _compute_chantrea_nom_en(self):
        _calculer_nom_anglais(self)
