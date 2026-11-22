"""Deux blocs standard d'Odoo masqués dans l'espace client (views/blocs_masques.xml)."""
from odoo.tests import HttpCase, tagged

MOT_DE_PASSE = "Blocs-Test-2026!"


@tagged("post_install", "-at_install", "chantrea")
class TestBlocsMasques(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        cls.societe = env["res.partner"].create({"name": "Société (blocs)", "is_company": True})
        cls.contact = env["res.partner"].create({"name": "Kosal (blocs)", "parent_id": cls.societe.id,
                                                 "email": "kosal@blocs.example"})
        env["res.users"].with_context(no_reset_password=True).create({
            "name": cls.contact.name, "login": "kosal-blocs", "password": MOT_DE_PASSE,
            "partner_id": cls.contact.id, "group_ids": [(6, 0, env.ref("base.group_portal").ids)]})
        cls.devis = env["sale.order"].create({
            "partner_id": cls.societe.id,
            "order_line": [(0, 0, {"name": "Borne Wi-Fi", "product_uom_qty": 1, "price_unit": 60.0})],
        })
        cls.devis.action_quotation_sent()

    def test_mon_compte_sans_format_electronique(self):
        # Sans notre vue, Odoo afficherait la liste : il y a bien des formats installés.
        formats = self.env["res.partner"]._fields["invoice_edi_format"]._description_selection(self.env)
        self.assertTrue(formats, "aucun format électronique installé : ce test ne prouverait rien")
        self.authenticate("kosal-blocs", MOT_DE_PASSE)
        reponse = self.url_open("/my/account")
        self.assertEqual(reponse.status_code, 200)
        page = reponse.text
        self.assertIn('name="name"', page, "le formulaire du compte doit rester affiché")
        for absent in ('name="invoice_edi_format"', 'name="invoice_sending_method"', "FacturX", "Peppol"):
            self.assertNotIn(absent, page)

    def test_devis_sans_encart_logiciel(self):
        self.assertTrue(self.devis._get_edi_builders(), "sans notre vue, Odoo afficherait le bouton sur ce devis")
        self.authenticate("kosal-blocs", MOT_DE_PASSE)
        reponse = self.url_open(f"/my/orders/{self.devis.id}")
        self.assertEqual(reponse.status_code, 200)
        page = reponse.text
        self.assertIn(self.devis.name, page)
        self.assertIn('id="modalaccept"', page, "la fenêtre de signature doit rester")
        for absent in ("portal_connect_software_modal_btn", "sale_portal_connect_software_modal",
                       "odoo.com/app/sales", "download_edi"):
            self.assertNotIn(absent, page)
