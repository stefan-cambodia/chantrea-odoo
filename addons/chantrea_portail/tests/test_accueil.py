"""Accueil de l'espace client : tableau de bord propre à chaque client, rubriques, langues."""
import re
from datetime import timedelta

from odoo import fields
from odoo.tests import HttpCase, tagged

MOT_DE_PASSE = "Accueil-Test-2026!"


@tagged("post_install", "-at_install", "chantrea")
class TestAccueil(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        Partner = env["res.partner"]
        cls.societe_a = Partner.create({"name": "Société A (accueil)", "is_company": True})
        cls.societe_b = Partner.create({"name": "Société B (accueil)", "is_company": True})
        cls.contact_a = Partner.create({"name": "Achariya A", "parent_id": cls.societe_a.id,
                                        "email": "achariya@a.example", "lang": "km_KH"})
        cls.contact_b = Partner.create({"name": "Bernard B", "parent_id": cls.societe_b.id,
                                        "email": "bernard@b.example", "lang": "fr_FR"})
        portail = env.ref("base.group_portal")
        for contact, login in ((cls.contact_a, "achariya-accueil"), (cls.contact_b, "bernard-accueil")):
            env["res.users"].with_context(no_reset_password=True).create({
                "name": contact.name, "login": login, "password": MOT_DE_PASSE,
                "partner_id": contact.id, "group_ids": [(6, 0, portail.ids)]})

        # Société A : 2 tickets ouverts et 1 fermé, 2 équipements (dont 1 garantie proche),
        # 1 contrat, 1 devis envoyé, 2 factures à payer. Société B : 1 ticket, 1 équipement.
        Ticket = env["helpdesk.ticket"]
        for nom in ("Imprimante", "Wi-Fi"):
            Ticket.create({"name": f"{nom} (accueil A)", "description": "<p>A</p>", "partner_id": cls.contact_a.id})
        ferme = Ticket.create({"name": "Ancien ticket (accueil A)", "description": "<p>A</p>",
                               "partner_id": cls.contact_a.id})
        ferme.stage_id = env["helpdesk.ticket.stage"].search([("closed", "=", True)], limit=1)
        Ticket.create({"name": "Écran (accueil B)", "description": "<p>B</p>", "partner_id": cls.contact_b.id})

        aujourd_hui = fields.Date.context_today(env["fsm.equipment"])
        Equipement = env["fsm.equipment"]
        Equipement.create({"name": "Serveur A (accueil)", "chantrea_client_id": cls.societe_a.id,
                           "chantrea_categorie": "serveur", "chantrea_fin_garantie": aujourd_hui + timedelta(days=400)})
        Equipement.create({"name": "Onduleur A (accueil)", "chantrea_client_id": cls.societe_a.id,
                           "chantrea_categorie": "onduleur", "chantrea_fin_garantie": aujourd_hui + timedelta(days=40)})
        Equipement.create({"name": "Poste B (accueil)", "chantrea_client_id": cls.societe_b.id,
                           "chantrea_categorie": "poste", "chantrea_fin_garantie": aujourd_hui + timedelta(days=400)})

        env["contract.contract"].create({"name": "Maintenance A (accueil)", "partner_id": cls.societe_a.id})
        env["sale.order"].create({
            "partner_id": cls.societe_a.id,
            "order_line": [(0, 0, {"name": "Borne Wi-Fi", "product_uom_qty": 1, "price_unit": 60.0})],
        }).action_quotation_sent()

        env["res.currency.rate"].create({"currency_id": env.ref("base.KHR").id, "name": "2026-01-01", "rate": 4050,
                                         "company_id": env.company.root_id.id})
        for montant in (100.0, 250.0):
            env["account.move"].create({
                "move_type": "out_invoice", "partner_id": cls.societe_a.id, "invoice_date": "2026-11-21",
                "currency_id": env.ref("base.USD").id,
                "invoice_line_ids": [(0, 0, {"name": "Maintenance", "quantity": 1, "price_unit": montant,
                                             "tax_ids": [(5, 0, 0)]})],
            }).action_post()

    def accueil(self, login, prefixe=""):
        self.authenticate(login, MOT_DE_PASSE)
        reponse = self.url_open(f"{prefixe}/my")
        self.assertEqual(reponse.status_code, 200)
        return reponse.text

    @staticmethod
    def nombres(page):
        """{carte: nombre} lu dans le tableau de bord de la page."""
        return {carte: int(nombre) for carte, nombre in re.findall(
            r'data-chantrea-carte="(\w+)".*?class="o_chantrea_nombre">\s*(\d+)\s*<', page, flags=re.S)}

    def test_chaque_client_voit_ses_propres_chiffres(self):
        page_a = self.accueil("achariya-accueil")
        self.assertEqual(self.nombres(page_a), {"tickets": 2, "interventions": 0, "equipements": 2, "contrats": 1,
                                                "devis": 1, "factures": 2})
        self.assertIn("350.00", page_a, "montant restant dû des deux factures de la société A")
        self.assertNotIn("(accueil B)", page_a)

        page_b = self.accueil("bernard-accueil")
        self.assertEqual(self.nombres(page_b), {"tickets": 1, "interventions": 0, "equipements": 1, "contrats": 0,
                                                "devis": 0, "factures": 0})
        self.assertNotIn("350.00", page_b, "le client B ne doit pas voir le montant dû par A")

    def test_garantie_proche_signalee(self):
        self.assertIn("o_chantrea_alerte", self.accueil("achariya-accueil"))
        self.assertNotIn("o_chantrea_alerte", self.accueil("bernard-accueil"))

    def test_rubriques_internes_absentes(self):
        page = self.accueil("achariya-accueil")
        for adresse in ("/my/projects", "/my/tasks", "/my/timesheets", "/my/rfq", "/my/purchase", "/my/sign_requests"):
            self.assertNotIn(f'href="{adresse}', page, f"{adresse} ne doit pas être proposé à un client")
        for adresse in ("/my/tickets", "/my/fsm_orders", "/my/equipments", "/my/contracts", "/my/quotes",
                        "/my/invoices", "/my/orders", "/my/addresses", "/my/security", "/new/ticket"):
            self.assertIn(f'href="{adresse}', page, f"{adresse} doit rester accessible depuis l'accueil")
        for adresse in ("/my/tickets", "/my/invoices", "/my/contracts"):
            self.assertEqual(len(re.findall(f'href="{adresse}', page)), 1, f"{adresse} : un seul lien, celui du tableau de bord")

    def test_accueil_en_khmer(self):
        page = self.accueil("achariya-accueil", "/km")
        self.assertRegex(page, r'<html[^>]*\blang="km-KH"')
        for texte in ("សួស្តី", "ស្នើសុំជំនួយ", "សំណើជំនួយកំពុងបើក", "វិក្កយបត្រត្រូវបង់", "គណនីរបស់លោកអ្នក"):
            self.assertIn(texte, page)
        self.assertNotIn("Open requests", page)

    def test_accueil_en_francais(self):
        page = self.accueil("bernard-accueil", "/fr")
        self.assertRegex(page, r'<html[^>]*\blang="fr-FR"')
        for texte in ("Bonjour", "Demander de l'aide", "Demandes en cours", "Factures à payer", "Rien à payer"):
            self.assertIn(texte, page.replace("&#39;", "'"))

    def test_accueil_en_anglais(self):
        page = self.accueil("bernard-accueil", "/en")
        self.assertRegex(page, r'<html[^>]*\blang="en-US"')
        self.assertIn("Open requests", page)

    def test_script_oca_incompatible_retire(self):
        chemins = [chemin[0] for chemin in self.env["ir.asset"]._get_asset_paths("web.assets_frontend", {})]
        self.assertTrue(any("chantrea_portail/static/src/scss/espace_client.scss" in c for c in chemins))
        self.assertFalse([c for c in chemins if "fsm_order_portal" in c],
                         "le script OCA qui importe « @portal/js/portal » ne doit plus être chargé")
