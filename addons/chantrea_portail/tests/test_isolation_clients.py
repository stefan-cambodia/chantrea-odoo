"""Un client ne voit jamais les données d'un autre client dans l'espace client.

Deux niveaux :
- droits d'accès (ORM) : ce que l'utilisateur portail peut lire ou chercher ;
- pages réelles de l'espace client (HTTP), y compris en forçant l'adresse
  d'un document qui n'est pas à lui, et la fermeture de ticket corrigée.
"""
import re

from odoo.exceptions import AccessError
from odoo.tests import HttpCase, tagged

MOTS_DE_PASSE = "Isolation-Test-2026!"


@tagged("post_install", "-at_install", "chantrea")
class TestIsolationClients(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        Partner = env["res.partner"]
        cls.societe_a = Partner.create({"name": "Société A (test)", "is_company": True})
        cls.societe_b = Partner.create({"name": "Société B (test)", "is_company": True})
        cls.contact_a = Partner.create({"name": "Alice A", "parent_id": cls.societe_a.id, "email": "alice@a.example"})
        cls.collegue_a = Partner.create({"name": "Arthur A", "parent_id": cls.societe_a.id, "email": "arthur@a.example"})
        cls.contact_b = Partner.create({"name": "Bruno B", "parent_id": cls.societe_b.id, "email": "bruno@b.example"})

        portail = env.ref("base.group_portal")

        def utilisateur(contact, login):
            return env["res.users"].with_context(no_reset_password=True).create({
                "name": contact.name, "login": login, "password": MOTS_DE_PASSE,
                "partner_id": contact.id, "group_ids": [(6, 0, portail.ids)],
            })

        cls.user_a = utilisateur(cls.contact_a, "alice-test")
        cls.user_collegue_a = utilisateur(cls.collegue_a, "arthur-test")
        cls.user_b = utilisateur(cls.contact_b, "bruno-test")

        # --- Documents de chaque client -----------------------------------------
        Ticket = env["helpdesk.ticket"]
        cls.ticket_a = Ticket.create({"name": "Imprimante A en panne", "description": "<p>A</p>",
                                      "partner_id": cls.contact_a.id})
        cls.ticket_b = Ticket.create({"name": "Wi-Fi B coupé", "description": "<p>B</p>",
                                      "partner_id": cls.contact_b.id})

        khr = env.ref("base.KHR")
        env["res.currency.rate"].create({"currency_id": khr.id, "name": "2026-01-01", "rate": 4050,
                                         "company_id": env.company.root_id.id})

        def facture(client):
            move = env["account.move"].create({
                "move_type": "out_invoice", "partner_id": client.id, "invoice_date": "2026-11-21",
                "currency_id": env.ref("base.USD").id,
                "invoice_line_ids": [(0, 0, {"name": "Maintenance", "quantity": 1, "price_unit": 100.0,
                                             "tax_ids": [(5, 0, 0)]})],
            })
            move.action_post()
            return move

        cls.facture_a = facture(cls.societe_a)
        cls.facture_b = facture(cls.societe_b)

        def devis(client):
            commande = env["sale.order"].create({
                "partner_id": client.id,
                "order_line": [(0, 0, {"name": "Wi-Fi", "product_uom_qty": 1, "price_unit": 60.0})],
            })
            commande.action_quotation_sent()
            return commande

        cls.devis_a = devis(cls.societe_a)
        cls.devis_b = devis(cls.societe_b)

        Contrat = env["contract.contract"]
        cls.contrat_a = Contrat.create({"name": "Maintenance A", "partner_id": cls.societe_a.id})
        cls.contrat_a.message_subscribe(partner_ids=cls.contact_a.ids)
        cls.contrat_b = Contrat.create({"name": "Maintenance B", "partner_id": cls.societe_b.id})
        cls.contrat_b.message_subscribe(partner_ids=cls.contact_b.ids)

    # ------------------------------------------------------------------
    # Droits d'accès
    # ------------------------------------------------------------------
    def verifier_isolation(self, modele, a_moi, a_lautre):
        env_a = self.env(user=self.user_a)
        visibles = env_a[modele].search([])
        self.assertIn(a_moi, visibles.sudo(), f"{modele} : le client doit voir son document")
        self.assertNotIn(a_lautre, visibles.sudo(), f"{modele} : le client voit le document d'un autre client")
        with self.assertRaises(AccessError, msg=f"{modele} : lecture directe du document d'un autre client"):
            env_a[modele].browse(a_lautre.id).read(["display_name"])

    def test_tickets(self):
        self.verifier_isolation("helpdesk.ticket", self.ticket_a, self.ticket_b)

    def test_factures(self):
        self.verifier_isolation("account.move", self.facture_a, self.facture_b)

    def test_devis(self):
        self.verifier_isolation("sale.order", self.devis_a, self.devis_b)

    def test_contrats(self):
        self.verifier_isolation("contract.contract", self.contrat_a, self.contrat_b)

    def test_collegue_voit_les_tickets_de_sa_societe(self):
        # Comportement voulu en B2B : les contacts d'une même société partagent leurs tickets.
        visibles = self.env(user=self.user_collegue_a)["helpdesk.ticket"].search([])
        self.assertIn(self.ticket_a, visibles.sudo())
        self.assertNotIn(self.ticket_b, visibles.sudo())

    def test_portail_ne_modifie_pas_les_tickets(self):
        with self.assertRaises(AccessError):
            self.ticket_a.with_user(self.user_a).write({"name": "modifié"})

    # ------------------------------------------------------------------
    # Pages de l'espace client
    # ------------------------------------------------------------------
    def page(self, url):
        reponse = self.url_open(url)
        return reponse, reponse.text

    def test_pages_listes(self):
        self.authenticate("alice-test", MOTS_DE_PASSE)
        for url, a_moi, a_lautre in [
            ("/my/tickets", self.ticket_a.number, self.ticket_b.number),
            ("/my/invoices", self.facture_a.name, self.facture_b.name),
            ("/my/quotes", self.devis_a.name, self.devis_b.name),
        ]:
            _reponse, texte = self.page(url)
            self.assertIn(a_moi, texte, f"{url} : document du client absent")
            self.assertNotIn(a_lautre, texte, f"{url} : document d'un autre client affiché")

    def test_adresse_forcee_vers_le_document_d_un_autre(self):
        self.authenticate("alice-test", MOTS_DE_PASSE)
        for url, secret in [
            (f"/my/ticket/{self.ticket_b.id}", "Wi-Fi B coupé"),
            (f"/my/invoices/{self.facture_b.id}", self.facture_b.name),
            (f"/my/orders/{self.devis_b.id}", self.devis_b.name),
            (f"/my/contracts/{self.contrat_b.id}", "Maintenance B"),
        ]:
            reponse, texte = self.page(url)
            self.assertNotIn(secret, texte, f"{url} : contenu d'un autre client affiché")
            self.assertTrue(reponse.status_code in (403, 404) or not reponse.url.endswith(url),
                            f"{url} : l'accès aurait dû être refusé ou redirigé")

    def jeton_csrf(self):
        _reponse, texte = self.page(f"/my/ticket/{self.ticket_a.id}")
        jeton = re.search(r'name="csrf_token" value="([^"]+)"', texte)
        self.assertTrue(jeton, "le formulaire de fermeture doit porter un jeton CSRF")
        return jeton.group(1)

    def test_fermeture_du_ticket_d_un_autre_refusee(self):
        etape_finie = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        etape_b = self.ticket_b.stage_id
        self.authenticate("alice-test", MOTS_DE_PASSE)
        reponse = self.url_open("/ticket/close", data={
            "csrf_token": self.jeton_csrf(), "ticket_id": self.ticket_b.id, "stage_id": etape_finie.id})
        self.assertEqual(reponse.status_code, 404)
        self.ticket_b.invalidate_recordset()
        self.assertEqual(self.ticket_b.stage_id, etape_b, "le ticket d'un autre client a été modifié")

    def test_fermeture_par_lien_get_refusee(self):
        etape_finie = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        self.authenticate("alice-test", MOTS_DE_PASSE)
        reponse = self.url_open(f"/ticket/close?ticket_id={self.ticket_a.id}&stage_id={etape_finie.id}")
        self.assertEqual(reponse.status_code, 405)
        self.ticket_a.invalidate_recordset()
        self.assertNotEqual(self.ticket_a.stage_id, etape_finie)

    def test_fermeture_de_son_propre_ticket(self):
        etape_finie = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        self.authenticate("alice-test", MOTS_DE_PASSE)
        reponse = self.url_open("/ticket/close", data={
            "csrf_token": self.jeton_csrf(), "ticket_id": self.ticket_a.id, "stage_id": etape_finie.id})
        self.assertEqual(reponse.status_code, 200)
        self.ticket_a.invalidate_recordset()
        self.assertEqual(self.ticket_a.stage_id, etape_finie)

    def test_ticket_ouvert_depuis_l_espace_client(self):
        self.authenticate("alice-test", MOTS_DE_PASSE)
        page = self.url_open("/new/ticket").text
        jeton = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
        categorie = self.env.ref("chantrea_portail.categorie_reseau")
        reponse = self.url_open("/submitted/ticket", data={
            "csrf_token": jeton, "category": categorie.id, "subject": "Plus d'Internet (test)",
            "description": "La box clignote."})
        self.assertEqual(reponse.status_code, 200)
        ticket = self.env["helpdesk.ticket"].search([("name", "=", "Plus d'Internet (test)")])
        self.assertEqual(len(ticket), 1)
        self.assertEqual(ticket.partner_id, self.contact_a)
        self.assertEqual(ticket.category_id, categorie)
        self.assertEqual(ticket.team_id, self.env.ref("chantrea_portail.equipe_assistance"))
        # Accusé de réception envoyé au client, signé par la société (pas par le client).
        # (dans une requête web, le courriel part aussitôt puis est supprimé : on vérifie
        # le message publié dans le ticket et la notification adressée au client)
        accuse = ticket.message_ids.filtered(lambda m: ticket.number in (m.subject or ""))
        self.assertEqual(len(accuse), 1)
        self.assertEqual(accuse.author_id, self.env.company.partner_id)
        self.assertNotIn("alice@a.example", accuse.email_from or "")
        notification = accuse.notification_ids.filtered(lambda n: n.res_partner_id == self.contact_a)
        self.assertEqual(notification.notification_type, "email")
        # Le nouveau ticket est visible par sa société, pas par l'autre client.
        self.assertIn(ticket, self.env(user=self.user_collegue_a)["helpdesk.ticket"].search([]).sudo())
        self.assertNotIn(ticket, self.env(user=self.user_b)["helpdesk.ticket"].search([]).sudo())

    def test_categorie_controlee_par_le_serveur(self):
        self.authenticate("alice-test", MOTS_DE_PASSE)
        page = self.url_open("/new/ticket").text
        jeton = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
        masquee = self.env["helpdesk.ticket.category"].create({"name": "Interne (test)", "show_in_portal": False})
        for categorie in ("", str(masquee.id), "abc"):
            reponse = self.url_open("/submitted/ticket", data={
                "csrf_token": jeton, "category": categorie, "subject": f"Sans catégorie valide {categorie!r}",
                "description": "x"}, allow_redirects=False)
            self.assertEqual(reponse.status_code, 303)
            self.assertTrue(reponse.headers["Location"].endswith("/new/ticket"))
        self.assertFalse(self.env["helpdesk.ticket"].search([("name", "like", "Sans catégorie valide")]))
