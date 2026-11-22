from unittest.mock import patch

from odoo.tests import TransactionCase, tagged
from odoo.tools import config


@tagged("post_install", "-at_install", "chantrea")
class TestConfiguration(TransactionCase):

    @patch.dict(config.options, {"email_from": "erp@exemple.test"})
    def test_expediteur_du_domaine_d_alias(self):
        """Créer le domaine d'alias (réception des courriels) ne doit pas changer
        l'adresse d'expédition : elle reste EMAIL_FROM, la seule autorisée."""
        domaine = self.env["mail.alias.domain"].create({"name": "exemple.test"})
        self.assertEqual(domaine.default_from_email, "erp@exemple.test")

    @patch.dict(config.options, {"email_from": False})
    def test_expediteur_du_domaine_d_alias_sans_reglage(self):
        domaine = self.env["mail.alias.domain"].create({"name": "exemple.test"})
        self.assertEqual(domaine.default_from_email, "notifications@exemple.test")

    def test_societe(self):
        company = self.env.ref("base.main_company")
        self.assertEqual(company.country_id, self.env.ref("base.kh"))
        self.assertEqual(company.currency_id, self.env.ref("base.USD"), "USD doit être la devise principale")
        # Société en cours d'immatriculation : aucune donnée légale.
        self.assertFalse(company.vat)
        self.assertFalse(company.company_registry)

    def test_riel_actif_sans_decimales(self):
        khr = self.env.ref("base.KHR")
        self.assertTrue(khr.active)
        self.assertEqual(khr.rounding, 1.0)

    def test_langues_actives(self):
        actives = self.env["res.lang"].search([]).mapped("code")
        for code in ("fr_FR", "en_US", "km_KH"):
            self.assertIn(code, actives)

    def test_dates_jour_mois_annee(self):
        for code in ("fr_FR", "en_US", "km_KH"):
            self.assertEqual(self.env["res.lang"]._lang_get(code).date_format, "%d/%m/%Y", code)

    def test_double_authentification(self):
        policy = self.env["ir.config_parameter"].sudo().get_param("auth_totp.policy")
        self.assertEqual(policy, "employee_required")

    def test_portail_sur_invitation(self):
        scope = self.env["ir.config_parameter"].sudo().get_param("auth_signup.invitation_scope")
        self.assertEqual(scope, "b2b")

    def test_groupes(self):
        direction = self.env.ref("chantrea_base.groupe_direction")
        technicien = self.env.ref("chantrea_base.groupe_technicien")
        self.assertIn(technicien, direction.all_implied_ids)
        self.assertIn(self.env.ref("account.group_account_manager"), direction.all_implied_ids)
        self.assertNotIn(self.env.ref("account.group_account_invoice"), technicien.all_implied_ids,
                         "un technicien ne doit pas facturer")
