"""Parc matériel : fiche, contenu interdit, alertes de garantie, liens, espace client."""
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import HttpCase, tagged

from ..models.fsm_equipment import contenu_interdit

MOT_DE_PASSE = "Parc-Test-2026!"
NOTE_SECRETE = "Remarque interne : client difficile, ne pas facturer le déplacement"


@tagged("post_install", "-at_install", "chantrea")
class TestParc(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        Partner = env["res.partner"]
        cls.societe_a = Partner.create({"name": "Société A (parc)", "is_company": True})
        cls.societe_b = Partner.create({"name": "Société B (parc)", "is_company": True})
        cls.contact_a = Partner.create({"name": "Pich A", "parent_id": cls.societe_a.id, "email": "pich@a.example"})
        cls.fournisseur = Partner.create({"name": "Grossiste secret (parc)", "is_company": True})
        cls.user_a = env["res.users"].with_context(no_reset_password=True).create({
            "name": "Pich A", "login": "pich-parc", "password": MOT_DE_PASSE, "partner_id": cls.contact_a.id,
            "group_ids": [(6, 0, env.ref("base.group_portal").ids)]})
        cls.site_a = env["fsm.location"].create({"name": "Siège A (parc)", "owner_id": cls.societe_a.id})
        cls.equipement_a = cls.creer(cls.societe_a, "Pare-feu de l'accueil", site=cls.site_a)
        cls.equipement_b = cls.creer(cls.societe_b, "Serveur B confidentiel")

    @classmethod
    def creer(cls, client, nom, site=None, **valeurs):
        return cls.env["fsm.equipment"].create({
            "name": nom, "chantrea_client_id": client.id, "location_id": site.id if site else False,
            "chantrea_categorie": "pare_feu", "chantrea_marque": "Fortinet", "chantrea_modele": "FortiGate 40F",
            "chantrea_numero_serie": f"SN-{nom[:6]}", "chantrea_fournisseur_id": cls.fournisseur.id,
            "chantrea_date_achat": "2025-01-15", "chantrea_fin_garantie": "2028-01-15",
            "notes": f"<p>{NOTE_SECRETE}</p>", **valeurs})

    # --- Aucun mot de passe, adresse IP ni identifiant ----------------------------
    def test_detection_du_contenu_interdit(self):
        for texte in ("IP 192.168.1.10", "passerelle 10.0.0.1", "<p>Admin password: Abc123</p>",
                      "mot de passe : soleil", "login=admin", "fe80::1", "2001:db8::8a2e:370:7334",
                      "Clé Wi-Fi: 12345678", "ពាក្យសម្ងាត់: 1234"):
            self.assertTrue(contenu_interdit(texte), texte)
        for texte in ("Firmware v1.0.2.15", "MAC aa:bb:cc:dd:ee:ff", "Changer le mot de passe tous les 90 jours",
                      "Utilisateur principal : la réception", "Écran 24 pouces", "bypass: non", "Prix 1.5"):
            self.assertFalse(contenu_interdit(texte), texte)

    def test_enregistrement_refuse(self):
        with self.assertRaises(ValidationError):
            self.equipement_a.write({"notes": "<p>Accès : admin / password: Kampot2026</p>"})
        with self.assertRaises(ValidationError):
            self.equipement_a.write({"chantrea_modele": "Switch 192.168.0.2"})
        self.equipement_a.write({"chantrea_modele": "FortiGate 40F, firmware v7.2.8"})

    # --- Alertes de garantie --------------------------------------------------------
    def test_alertes_60_et_30_jours(self):
        aujourd_hui = fields.Date.context_today(self.env["fsm.equipment"])
        dans_60 = self.creer(self.societe_a, "Onduleur 60", chantrea_fin_garantie=aujourd_hui + timedelta(days=60))
        dans_45 = self.creer(self.societe_a, "Switch 45", chantrea_fin_garantie=aujourd_hui + timedelta(days=45))
        dans_20 = self.creer(self.societe_a, "NAS 20", chantrea_fin_garantie=aujourd_hui + timedelta(days=20))
        loin = self.creer(self.societe_a, "Serveur 200", chantrea_fin_garantie=aujourd_hui + timedelta(days=200))
        expire = self.creer(self.societe_a, "Poste expiré", chantrea_fin_garantie=aujourd_hui - timedelta(days=5))
        type_alerte = self.env.ref("chantrea_parc.activite_fin_garantie")

        def alertes(equipement):
            return equipement.activity_ids.filtered(lambda a: a.activity_type_id == type_alerte)

        Equipement = self.env["fsm.equipment"]
        Equipement._chantrea_cron_alertes_garantie()
        self.assertEqual(len(alertes(dans_60)), 1)
        self.assertIn("60", alertes(dans_60).summary)
        self.assertEqual(len(alertes(dans_45)), 1)
        self.assertEqual(len(alertes(dans_20)), 1, "sous les 30 jours d'emblée : une seule alerte")
        self.assertFalse(alertes(loin))
        self.assertFalse(alertes(expire))
        self.assertEqual(dans_60.chantrea_etat_garantie, "bientot")
        self.assertEqual(loin.chantrea_etat_garantie, "valide")
        self.assertEqual(expire.chantrea_etat_garantie, "expiree")

        # Relancer ne crée pas de doublon.
        Equipement._chantrea_cron_alertes_garantie()
        self.assertEqual(len(alertes(dans_60)), 1)
        # À 30 jours, la seconde alerte part.
        dans_60.with_context(tracking_disable=True)
        Equipement.browse(dans_60.id)._write({"chantrea_fin_garantie": aujourd_hui + timedelta(days=30)})
        Equipement._chantrea_cron_alertes_garantie()
        self.assertEqual(len(alertes(dans_60)), 2)
        # Une nouvelle date de fin de garantie relance les alertes.
        loin.chantrea_fin_garantie = aujourd_hui + timedelta(days=50)
        Equipement._chantrea_cron_alertes_garantie()
        self.assertEqual(len(alertes(loin)), 1)

    # --- Liens tickets et interventions ---------------------------------------------
    def test_liens_tickets_et_interventions(self):
        ticket = self.env["helpdesk.ticket"].create({
            "name": "Pare-feu qui redémarre", "description": "<p>x</p>", "partner_id": self.contact_a.id,
            "chantrea_equipement_ids": [(6, 0, self.equipement_a.ids)]})
        self.env["fsm.order"].create({"location_id": self.site_a.id, "equipment_ids": [(6, 0, self.equipement_a.ids)]})
        self.assertEqual(self.equipement_a.chantrea_ticket_ids, ticket)
        self.assertEqual(self.equipement_a.chantrea_ticket_count, 1)
        self.assertEqual(self.equipement_a.chantrea_intervention_count, 1)

    def test_technicien_cree_une_fiche(self):
        technicien = self.env["res.users"].create({
            "name": "Tech (parc)", "login": "tech-parc",
            "group_ids": [(6, 0, self.env.ref("chantrea_base.groupe_technicien").ids)]})
        fiche = self.env["fsm.equipment"].with_user(technicien).create({
            "name": "Borne Wi-Fi", "chantrea_client_id": self.societe_a.id, "chantrea_categorie": "wifi"})
        self.assertTrue(fiche)
        with self.assertRaises(AccessError):
            fiche.with_user(technicien).unlink()

    # --- Espace client ----------------------------------------------------------------
    def test_droits_du_client(self):
        Equipement = self.env["fsm.equipment"].with_user(self.user_a)
        visibles = Equipement.search([])
        self.assertIn(self.equipement_a, visibles.sudo())
        self.assertNotIn(self.equipement_b, visibles.sudo())
        with self.assertRaises(AccessError):
            Equipement.browse(self.equipement_a.id).read(["notes"])
        with self.assertRaises(AccessError):
            Equipement.browse(self.equipement_a.id).read(["chantrea_fournisseur_id"])
        with self.assertRaises(AccessError):
            Equipement.browse(self.equipement_a.id).write({"chantrea_modele": "modifié"})
        with self.assertRaises(AccessError):
            Equipement.browse(self.equipement_b.id).read(["name"])

    def test_pages_espace_client(self):
        self.authenticate("pich-parc", MOT_DE_PASSE)
        liste = self.url_open("/my/equipments").text
        self.assertIn("Pare-feu de l&#39;accueil", liste.replace("'", "&#39;"))
        self.assertNotIn("Serveur B confidentiel", liste)
        fiche = self.url_open(f"/my/equipment/{self.equipement_a.id}")
        self.assertEqual(fiche.status_code, 200)
        for attendu in ("FortiGate 40F", "SN-Pare-f", "Siège A (parc)", "15/01/2028"):
            self.assertIn(attendu, fiche.text)
        for interdit in (NOTE_SECRETE, "Grossiste secret"):
            self.assertNotIn(interdit, fiche.text, "information interne affichée au client")
        autre = self.url_open(f"/my/equipment/{self.equipement_b.id}")
        self.assertNotIn("Serveur B confidentiel", autre.text)

    def test_api_json_sans_notes_internes(self):
        self.authenticate("pich-parc", MOT_DE_PASSE)
        lecture = self.make_jsonrpc_request("/web/dataset/call_kw/fsm.equipment/search_read", {
            "model": "fsm.equipment", "method": "search_read", "args": [[], ["name", "chantrea_numero_serie"]],
            "kwargs": {}})
        self.assertEqual([ligne["name"] for ligne in lecture], [self.equipement_a.name])
        with self.assertRaises(Exception):
            self.make_jsonrpc_request("/web/dataset/call_kw/fsm.equipment/read", {
                "model": "fsm.equipment", "method": "read", "args": [self.equipement_a.ids, ["notes"]],
                "kwargs": {}})
