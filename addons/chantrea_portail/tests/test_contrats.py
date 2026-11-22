"""Contrats de maintenance : facture mensuelle en brouillon, activité de validation, espace client."""
from odoo import fields
from odoo.tests import HttpCase, tagged

MOT_DE_PASSE = "Contrat-Test-2026!"


@tagged("post_install", "-at_install", "chantrea")
class TestContratsMaintenance(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        cls.societe = env["res.partner"].create({"name": "Hôtel (contrat test)", "is_company": True,
                                                 "lang": "en_US"})
        cls.contact = env["res.partner"].create({"name": "Vanna", "parent_id": cls.societe.id,
                                                 "email": "vanna@contrat.example"})
        cls.autre = env["res.partner"].create({"name": "Autre client (contrat test)", "is_company": True})
        env["res.users"].with_context(no_reset_password=True).create({
            "name": "Vanna", "login": "vanna-contrat", "password": MOT_DE_PASSE, "partner_id": cls.contact.id,
            "group_ids": [(6, 0, env.ref("base.group_portal").ids)]})
        cls.responsable = env.ref("base.user_admin")
        cls.modele = env.ref("chantrea_portail.modele_contrat_maintenance_mensuelle")
        cls.contrat = cls.creer_contrat(cls.societe, 120.0)
        cls.contrat_autre = cls.creer_contrat(cls.autre, 300.0)
        env["res.currency.rate"].create({"currency_id": env.ref("base.KHR").id, "name": "2026-10-30",
                                         "rate": 4070, "company_id": env.company.root_id.id})

    @classmethod
    def creer_contrat(cls, client, prix):
        contrat = cls.env["contract.contract"].new({
            "name": f"Maintenance {client.name}", "partner_id": client.id,
            "contract_template_id": cls.modele.id, "user_id": cls.responsable.id,
        })
        contrat._onchange_contract_template_id()
        contrat = cls.env["contract.contract"].create(contrat._convert_to_write(contrat._cache))
        contrat.contract_line_ids.write({"price_unit": prix, "date_start": "2026-11-01",
                                         "recurring_next_date": "2026-11-01"})
        return contrat

    def factures(self, contrat):
        return contrat._get_related_invoices()

    def test_modele_mensuel_paye_d_avance(self):
        ligne = self.contrat.contract_line_ids
        self.assertEqual(len(ligne), 1)
        self.assertEqual(ligne.recurring_rule_type, "monthly")
        self.assertEqual(ligne.recurring_invoicing_type, "pre-paid")
        self.assertEqual(ligne.product_id, self.env.ref("chantrea_portail.produit_maintenance_mensuelle"))

    def test_facture_mensuelle_en_brouillon_avec_activite(self):
        self.env["contract.contract"].cron_recurring_create_invoice(date_ref=fields.Date.to_date("2026-11-01"))
        facture = self.factures(self.contrat)
        self.assertEqual(len(facture), 1)
        self.assertEqual(facture.state, "draft", "la facture mensuelle doit rester en brouillon")
        self.assertEqual(facture.partner_id, self.societe)
        self.assertEqual(facture.invoice_date, fields.Date.to_date("2026-11-01"))
        self.assertEqual(facture.invoice_date_due, facture.invoice_date)
        self.assertIn("01/11/2026", facture.invoice_line_ids.name)
        self.assertEqual(facture.amount_untaxed, 120.0)
        self.assertIn("កញ្ចប់ថែទាំព័ត៌មានវិទ្យាប្រចាំខែ", facture.invoice_line_ids.name)
        self.assertNotIn("#START#", facture.invoice_line_ids.name)
        activite = facture.activity_ids
        self.assertEqual(len(activite), 1)
        self.assertEqual(activite.user_id, self.responsable)
        self.assertEqual(activite.date_deadline, fields.Date.to_date("2026-11-01"))
        self.assertFalse(facture.chantrea_taux_khr, "le taux est fixé à la validation, pas avant")
        # Le mois suivant est prévu ; relancer la tâche le même jour ne crée pas de doublon.
        self.assertEqual(self.contrat.recurring_next_date, fields.Date.to_date("2026-12-01"))
        self.env["contract.contract"].cron_recurring_create_invoice(date_ref=fields.Date.to_date("2026-11-01"))
        self.assertEqual(len(self.factures(self.contrat)), 1)
        self.env["contract.contract"].cron_recurring_create_invoice(date_ref=fields.Date.to_date("2026-12-01"))
        self.assertEqual(len(self.factures(self.contrat)), 2)

    def test_validation_fixe_le_taux_et_clot_l_activite(self):
        self.env["contract.contract"].cron_recurring_create_invoice(date_ref=fields.Date.to_date("2026-11-01"))
        facture = self.factures(self.contrat)
        self.assertEqual(facture.activity_ids.activity_type_id,
                         self.env.ref("chantrea_portail.activite_valider_facture"))
        facture.action_post()
        self.assertFalse(facture.activity_ids, "l'activité « À valider » doit être faite à la validation")
        self.assertEqual(facture.chantrea_taux_khr, 4070)
        self.assertEqual(facture.chantrea_total_khr, round(facture.amount_total * 4070))

    def test_contrat_dans_l_espace_client(self):
        self.authenticate("vanna-contrat", MOT_DE_PASSE)
        liste = self.url_open("/my/contracts").text
        self.assertIn(self.contrat.name, liste)
        self.assertNotIn(self.contrat_autre.name, liste)
        page = self.url_open(f"/my/contracts/{self.contrat.id}")
        self.assertEqual(page.status_code, 200)
        self.assertIn("Monthly IT maintenance plan", page.text)
        autre = self.url_open(f"/my/contracts/{self.contrat_autre.id}")
        self.assertNotIn(self.contrat_autre.name, autre.text)
