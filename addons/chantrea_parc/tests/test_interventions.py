"""Interventions sur site : signature du client, lien ticket/équipements, rapport, espace client."""
import base64

from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import HttpCase, tagged

MOT_DE_PASSE = "Intervention-Test-2026!"
INSTRUCTION_INTERNE = "Instruction interne : le client paie toujours en retard"
# Petite image PNG (1×1 pixel) en guise de signature.
SIGNATURE = (b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=")


@tagged("post_install", "-at_install", "chantrea")
class TestInterventions(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        Partner = env["res.partner"]
        cls.societe_a = Partner.create({"name": "Société A (interv.)", "is_company": True})
        cls.societe_b = Partner.create({"name": "Société B (interv.)", "is_company": True})
        cls.contact_a = Partner.create({"name": "Rithy A", "parent_id": cls.societe_a.id,
                                        "email": "rithy@a.example"})
        cls.user_a = env["res.users"].with_context(no_reset_password=True).create({
            "name": "Rithy A", "login": "rithy-interv", "password": MOT_DE_PASSE, "partner_id": cls.contact_a.id,
            "group_ids": [(6, 0, env.ref("base.group_portal").ids)]})
        cls.site_a = env["fsm.location"].create({"name": "Site A (interv.)", "owner_id": cls.societe_a.id})
        cls.site_b = env["fsm.location"].create({"name": "Site B (interv.)", "owner_id": cls.societe_b.id})
        cls.equipement = env["fsm.equipment"].create({
            "name": "Switch du 1er étage", "chantrea_client_id": cls.societe_a.id, "location_id": cls.site_a.id,
            "chantrea_categorie": "switch", "chantrea_numero_serie": "SW-INTERV-01"})
        cls.ticket = env["helpdesk.ticket"].create({
            "name": "Réseau coupé au 1er", "description": "<p>x</p>", "partner_id": cls.contact_a.id,
            "chantrea_equipement_ids": [(6, 0, cls.equipement.ids)]})
        action = cls.ticket.action_create_order()
        cls.intervention_a = env["fsm.order"].with_context(**action["context"]).create({
            "location_id": cls.site_a.id, "description": "<p>Remplacer le switch</p>",
            "todo": f"<p>{INSTRUCTION_INTERNE}</p>", "resolution": "<p>Switch remplacé, réseau rétabli</p>"})
        cls.intervention_b = env["fsm.order"].create({"location_id": cls.site_b.id,
                                                      "description": "<p>Intervention B secrète</p>"})

    def signer(self, intervention, nom="Rithy A"):
        self.env["fsm.order.sign.wizard"].create({
            "order_id": intervention.id, "signed_by": nom, "signature": SIGNATURE}).action_sign()

    # --- Configuration et signature -------------------------------------------------
    def test_configuration_signature(self):
        company = self.env.company
        self.assertTrue(company.fsm_signature_capture)
        self.assertTrue(company.fsm_require_signature_to_complete)
        self.assertFalse(company.fsm_document_signing)
        self.assertTrue(self.env.ref("fieldservice.fsm_stage_new").require_signature,
                        "le bouton « Signer » doit être disponible dès l'étape Nouveau")

    def test_terminer_exige_la_signature(self):
        with self.assertRaisesRegex(UserError, "signature"):
            self.intervention_a.action_complete()
        self.signer(self.intervention_a)
        self.assertEqual(self.intervention_a.signed_by, "Rithy A")
        self.assertTrue(self.intervention_a.signed_on)
        self.intervention_a.action_complete()
        self.assertEqual(self.intervention_a.stage_id, self.env.ref("fieldservice.fsm_stage_completed"))

    # --- Liens ------------------------------------------------------------------------
    def test_intervention_creee_depuis_le_ticket(self):
        self.assertEqual(self.intervention_a.ticket_id, self.ticket)
        self.assertEqual(self.intervention_a.equipment_ids, self.equipement)
        self.assertEqual(self.equipement.chantrea_intervention_count, 1)

    def test_aucun_secret_dans_une_intervention(self):
        for champ in ("description", "todo", "resolution"):
            with self.assertRaises(ValidationError, msg=champ):
                self.intervention_b.write({champ: "<p>Routeur 192.168.1.1, login: admin</p>"})

    # --- Rapport ------------------------------------------------------------------------
    def test_rapport_bilingue_signe_sans_instructions_internes(self):
        self.signer(self.intervention_a, "Rithy (réception)")
        html = self.env["ir.actions.report"]._render_qweb_html(
            "fieldservice.action_report_fsm_order", self.intervention_a.ids)[0].decode()
        for attendu in ("របាយការណ៍សេវាកម្មនៅទីតាំង", "ON-SITE SERVICE REPORT", "Rithy (réception)",
                        "SW-INTERV-01", "Switch remplacé", self.ticket.number, "data:image/png;base64"):
            self.assertTrue(attendu in html, f"absent du rapport : {attendu}")
        self.assertFalse(INSTRUCTION_INTERNE in html, "instructions internes imprimées")
        # Heure de signature imprimée à l'heure de Phnom Penh (UTC+7).
        locale = self.intervention_a._chantrea_heure_locale(self.intervention_a.signed_on)
        self.assertIn(locale, html)
        from datetime import timedelta
        self.assertEqual(locale, (self.intervention_a.signed_on + timedelta(hours=7)).strftime("%d/%m/%Y %H:%M"))

    # --- Espace client ------------------------------------------------------------------
    def test_instructions_illisibles_par_le_client(self):
        with self.assertRaises(AccessError):
            self.intervention_a.with_user(self.user_a).read(["todo"])

    def test_pages_espace_client(self):
        self.signer(self.intervention_a)
        self.authenticate("rithy-interv", MOT_DE_PASSE)
        liste = self.url_open("/my/fsm_orders").text
        self.assertIn(self.intervention_a.name, liste)
        self.assertNotIn(self.intervention_b.name, liste)
        page = self.url_open(f"/my/fsm_order/{self.intervention_a.id}").text
        for attendu in ("Switch remplacé", "Rithy A", "SW-INTERV-01", f"/my/fsm_order/{self.intervention_a.id}/rapport"):
            self.assertIn(attendu, page)
        self.assertNotIn(INSTRUCTION_INTERNE, page)
        rapport = self.url_open(f"/my/fsm_order/{self.intervention_a.id}/rapport")
        self.assertEqual(rapport.status_code, 200)
        self.assertNotIn("/my", rapport.url.split("/rapport")[-1])

    def test_rapport_d_un_autre_client_refuse(self):
        self.authenticate("rithy-interv", MOT_DE_PASSE)
        reponse = self.url_open(f"/my/fsm_order/{self.intervention_b.id}/rapport")
        self.assertTrue(reponse.url.rstrip("/").endswith("/my"), reponse.url)
        self.assertNotIn("Intervention B secrète", reponse.text)
        page = self.url_open(f"/my/fsm_order/{self.intervention_b.id}")
        self.assertNotIn("Intervention B secrète", page.text)

    def test_signature_png_valide(self):
        self.assertTrue(base64.b64decode(SIGNATURE).startswith(b"\x89PNG"))
