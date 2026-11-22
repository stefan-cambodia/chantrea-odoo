"""Règles d'accès des clients qui complètent les modules OCA.

Vérifiées par l'ORM et par l'appel direct à l'API JSON d'Odoo, qu'un client
connecté peut utiliser sans passer par les pages de l'espace client.
"""
import base64

from odoo.exceptions import AccessError
from odoo.tests import HttpCase, tagged

MOT_DE_PASSE = "Regles-Test-2026!"


@tagged("post_install", "-at_install", "chantrea")
class TestReglesPortail(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        Partner = env["res.partner"]
        cls.societe_a = Partner.create({"name": "Société A (règles)", "is_company": True})
        cls.societe_b = Partner.create({"name": "Société B (règles)", "is_company": True})
        cls.contact_a = Partner.create({"name": "Chan A", "parent_id": cls.societe_a.id, "email": "chan@a.example"})
        cls.user_a = env["res.users"].with_context(no_reset_password=True).create({
            "name": "Chan A", "login": "chan-regles", "password": MOT_DE_PASSE,
            "partner_id": cls.contact_a.id, "group_ids": [(6, 0, env.ref("base.group_portal").ids)]})

        produit = env["product.product"].create({"name": "Forfait (règles)", "type": "service", "list_price": 50})

        def contrat(societe, nom, prix):
            return env["contract.contract"].create({
                "name": nom, "partner_id": societe.id,
                "contract_line_ids": [(0, 0, {"product_id": produit.id, "name": f"Ligne {nom}",
                                              "quantity": 1, "price_unit": prix})]})

        # Aucun abonnement explicite : le contrat A doit être visible par sa société.
        cls.contrat_a = contrat(cls.societe_a, "Contrat A (règles)", 100)
        cls.contrat_b = contrat(cls.societe_b, "Contrat B (règles)", 999)
        Modif = env["contract.modification"]
        cls.modif_a = Modif.create({"contract_id": cls.contrat_a.id, "date": "2026-11-01", "description": "Modif A"})
        cls.modif_b = Modif.create({"contract_id": cls.contrat_b.id, "date": "2026-11-01", "description": "Modif B"})

        def mouvement(societe):
            site = env["fsm.location"].create({"name": f"Site {societe.name}", "owner_id": societe.id})
            ordre = env["fsm.order"].create({"location_id": site.id})
            stockable = env["product.product"].create({"name": f"Câble {societe.name}", "type": "consu"})
            return env["stock.move"].create({
                "product_id": stockable.id, "product_uom_qty": 3, "fsm_order_id": ordre.id,
                "location_id": env.ref("stock.stock_location_stock").id,
                "location_dest_id": env.ref("stock.stock_location_customers").id})

        cls.mouvement_a = mouvement(cls.societe_a)
        cls.mouvement_b = mouvement(cls.societe_b)

    def visibles(self, modele):
        return self.env(user=self.user_a)[modele].search([]).sudo()

    def test_contrat_visible_par_la_societe_sans_abonnement(self):
        self.assertIn(self.contrat_a, self.visibles("contract.contract"))
        self.assertNotIn(self.contrat_b, self.visibles("contract.contract"))

    def test_lignes_de_contrat(self):
        lignes = self.visibles("contract.line")
        self.assertIn(self.contrat_a.contract_line_ids, lignes)
        self.assertFalse(lignes & self.contrat_b.contract_line_ids, "lignes du contrat d'un autre client visibles")

    def test_modifications_de_contrat(self):
        modifs = self.visibles("contract.modification")
        self.assertIn(self.modif_a, modifs)
        self.assertNotIn(self.modif_b, modifs)

    def test_mouvements_de_stock(self):
        mouvements = self.visibles("stock.move")
        self.assertIn(self.mouvement_a, mouvements)
        self.assertNotIn(self.mouvement_b, mouvements)
        for mouvement in (self.mouvement_a, self.mouvement_b):
            with self.assertRaises(AccessError, msg="un client ne doit modifier aucun mouvement de stock"):
                mouvement.with_user(self.user_a).write({"product_uom_qty": 1})

    def test_api_json_ne_livre_rien_d_un_autre_client(self):
        self.authenticate("chan-regles", MOT_DE_PASSE)
        for modele, champ, interdit in [
            ("contract.line", "price_unit", 999.0),
            ("contract.contract", "name", "Contrat B (règles)"),
            ("contract.modification", "description", "Modif B"),
        ]:
            resultat = self.make_jsonrpc_request(f"/web/dataset/call_kw/{modele}/search_read", {
                "model": modele, "method": "search_read", "args": [[], [champ]], "kwargs": {}})
            valeurs = [ligne[champ] for ligne in resultat]
            self.assertNotIn(interdit, valeurs, f"{modele} : donnée d'un autre client livrée par l'API")


@tagged("post_install", "-at_install", "chantrea")
class TestTelechargementSignature(HttpCase):
    """sign_oca : /my/sign/<id>/download ne doit servir un document signé qu'à ses signataires."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        Partner = env["res.partner"]
        portail = env.ref("base.group_portal")
        cls.contact_a = Partner.create({"name": "Sok A (signature)", "email": "sok@a.example",
                                        "parent_id": Partner.create({"name": "A (signature)", "is_company": True}).id})
        cls.contact_b = Partner.create({"name": "Bopha B (signature)", "email": "bopha@b.example",
                                        "parent_id": Partner.create({"name": "B (signature)", "is_company": True}).id})
        for contact, login in ((cls.contact_a, "sok-signature"), (cls.contact_b, "bopha-signature")):
            env["res.users"].with_context(no_reset_password=True).create({
                "name": contact.name, "login": login, "password": MOT_DE_PASSE, "partner_id": contact.id,
                "group_ids": [(6, 0, portail.ids)]})
        pdf = base64.b64encode(b"%PDF-1.4\n% document signe de B\n")
        cls.demande_b = env["sign.oca.request"].create({
            "name": "Contrat signé de B", "data": pdf,
            "signer_ids": [(0, 0, {"partner_id": cls.contact_b.id,
                                   "role_id": env["sign.oca.role"].search([], limit=1).id})]})

    def telecharger(self, login):
        self.authenticate(login, MOT_DE_PASSE)
        return self.url_open(f"/my/sign/{self.demande_b.id}/download", allow_redirects=False)

    def test_autre_client_refuse(self):
        reponse = self.telecharger("sok-signature")
        self.assertEqual(reponse.status_code, 404, "un client a obtenu le document signé d'un autre client")

    def test_signataire_autorise(self):
        reponse = self.telecharger("bopha-signature")
        self.assertIn(reponse.status_code, (302, 303))
        self.assertIn("/web/content/", reponse.headers.get("Location", ""))
