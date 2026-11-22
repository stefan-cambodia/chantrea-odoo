"""Langue de l'espace client : page publique en anglais, puis langue du compte après connexion."""
import re

from odoo.tests import HttpCase, tagged

MOT_DE_PASSE = "Langue-Test-2026!"


@tagged("post_install", "-at_install", "chantrea")
class TestLangueClient(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        contact = cls.env["res.partner"].create({"name": "Sokha (test)", "email": "sokha@test.example",
                                                 "lang": "km_KH"})
        cls.env["res.users"].with_context(no_reset_password=True).create({
            "name": contact.name, "login": "sokha-test", "password": MOT_DE_PASSE,
            "partner_id": contact.id, "group_ids": [(6, 0, cls.env.ref("base.group_portal").ids)],
        })

    def test_page_de_connexion_en_anglais(self):
        page = self.url_open("/web/login").text
        self.assertIn('"bundle_params": {"lang": "en_US"}', page)
        self.assertIn("Log in", page)

    def test_page_de_connexion_dans_la_langue_de_l_adresse(self):
        """Sans le module « website », Odoo la servait toujours en anglais."""
        khmer = self.url_open("/km/web/login").text
        self.assertRegex(khmer, r'<html[^>]*\blang="km-KH"')
        self.assertIn("ចូលគណនី", khmer)
        francais = self.url_open("/fr/web/login").text
        self.assertRegex(francais, r'<html[^>]*\blang="fr-FR"')
        self.assertIn("Se connecter", francais)

    def test_mot_de_passe_errone_reste_dans_la_langue_du_client(self):
        page = self.url_open("/km/web/login").text
        self.assertEqual(self.opener.cookies.get("frontend_lang"), "km_KH")
        jeton = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
        # Le formulaire d'Odoo envoie toujours vers /web/login, sans la langue dans l'adresse.
        reponse = self.url_open("/web/login", data={"login": "sokha-test", "password": "pas-le-bon", "csrf_token": jeton})
        self.assertRegex(reponse.text, r'<html[^>]*\blang="km-KH"')
        self.assertIn("ឈ្មោះចូល ឬពាក្យសម្ងាត់មិនត្រឹមត្រូវ", reponse.text)
        self.assertNotIn("Wrong login/password", reponse.text)

    def test_client_khmer_arrive_en_khmer(self):
        page = self.url_open("/web/login").text
        jeton = re.search(r'name="csrf_token" value="([^"]+)"', page).group(1)
        reponse = self.url_open("/web/login", data={
            "login": "sokha-test", "password": MOT_DE_PASSE, "csrf_token": jeton, "redirect": "/my"})
        self.assertEqual(self.opener.cookies.get("frontend_lang"), "km_KH")
        self.assertIn("/km/my", reponse.url)
        self.assertIn('"bundle_params": {"lang": "km_KH"}', reponse.text)

    def test_accuse_de_reception_dans_la_langue_du_client(self):
        equipe = self.env.ref("chantrea_portail.equipe_assistance")
        for langue, attendu, corps in [
            ("km_KH", "ត្រូវបានទទួលហើយ", "មើលសំណើរបស់ខ្ញុំ"),
            ("fr_FR", "a bien été reçue", "Voir ma demande"),
            ("en_US", "has been received", "View my request"),
        ]:
            contact = self.env["res.partner"].create({"name": f"Client {langue}", "email": f"{langue}@test.example",
                                                      "lang": langue})
            ticket = self.env["helpdesk.ticket"].create({"name": "Panne", "description": "<p>x</p>",
                                                         "partner_id": contact.id, "team_id": equipe.id})
            accuse = ticket.message_ids.filtered(lambda m: ticket.number in (m.subject or ""))
            self.assertEqual(len(accuse), 1, f"{langue} : un accusé de réception attendu")
            self.assertIn(attendu, accuse.subject)
            self.assertIn(corps, accuse.body)
            self.assertEqual(accuse.notification_ids.res_partner_id, contact)
            self.assertEqual(accuse.author_id, self.env.company.partner_id)
