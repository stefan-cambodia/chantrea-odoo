"""Traductions des textes Odoo/OCA vus par les clients (i18n_clients/*.po).

- les fichiers eux-mêmes : chaque traduction garde les variables et les balises
  du texte d'origine (une variable oubliée casserait la page ou le courriel) ;
- les textes de la base (pages, pays, étapes) sont bien importés ;
- les textes du code Python et JavaScript sont bien complétés ;
- une vraie page de l'espace client sort en khmer.
"""
import re
from collections import Counter

import polib
from lxml import etree

from odoo.tests import HttpCase, TransactionCase, tagged
from odoo.tools.translate import code_translations

from ..traductions_code import fichiers_clients

MOT_DE_PASSE = "Traductions-Test-2026!"
VARIABLE = re.compile(r"%\([^)]+\)[sdf]|%[sdf]|\{\{.*?\}\}", re.S)
BALISE = re.compile(r"<[^>]+>")
INFOBULLE = re.compile(r'\b(title|aria-label|alt|placeholder|data-tooltip|label|value_label)="[^"]*"')
KHMER = re.compile(r"[ក-៿]")


@tagged("post_install", "-at_install", "chantrea")
class TestFichiersDeTraduction(TransactionCase):

    @staticmethod
    def balises(texte):
        return Counter(INFOBULLE.sub(r'\1=""', balise) for balise in BALISE.findall(texte))

    def test_fichiers_presents(self):
        self.assertEqual([f.name for f in fichiers_clients("km_KH")], ["km.po", "km_pays.po"])
        self.assertEqual([f.name for f in fichiers_clients("fr_FR")], ["fr.po"])
        self.assertEqual(fichiers_clients("en_US"), [])

    def test_variables_et_balises_conservees(self):
        nombre = 0
        for langue in ("km_KH", "fr_FR"):
            for fichier in fichiers_clients(langue):
                for entree in polib.pofile(str(fichier)):
                    nombre += 1
                    ou = f"{fichier.name} : {entree.msgid[:60]!r}"
                    self.assertTrue(entree.msgstr, f"{ou} : traduction vide")
                    self.assertTrue(entree.comment.startswith("module: "), f"{ou} : commentaire « module: » absent")
                    self.assertTrue(entree.occurrences, f"{ou} : aucune référence")
                    self.assertEqual(Counter(VARIABLE.findall(entree.msgid)), Counter(VARIABLE.findall(entree.msgstr)),
                                     f"{ou} : variables différentes")
                    if any(reference.startswith("model") for reference, _ligne in entree.occurrences):
                        # Mêmes balises ; seul le texte des infobulles (title, aria-label…) est traduit.
                        self.assertEqual(self.balises(entree.msgid), self.balises(entree.msgstr),
                                         f"{ou} : balises différentes")
                        if BALISE.search(entree.msgstr):
                            etree.fromstring(f"<racine>{entree.msgstr}</racine>".replace("&nbsp;", " "))
                    if langue == "km_KH" and not any("mail.template" in r for r, _l in entree.occurrences):
                        self.assertTrue(KHMER.search(entree.msgstr), f"{ou} : pas de khmer dans la traduction")
        self.assertGreater(nombre, 800)

    def test_textes_de_la_base_importes(self):
        en_khmer = self.env(context={"lang": "km_KH"})
        self.assertEqual(en_khmer.ref("base.kh").name, "កម្ពុជា")
        self.assertEqual(en_khmer.ref("base.fr").name, "បារាំង")
        self.assertIn("អាសយដ្ឋាន", en_khmer.ref("portal.portal_my_home").arch_db)
        self.assertIn("ស្វែងរក", en_khmer.ref("portal.portal_searchbar").arch_db)
        self.assertIn("សម្រង់តម្លៃ", en_khmer.ref("sale.sale_order_portal_template").arch_db)
        self.assertEqual(en_khmer.ref("fieldservice.fsm_stage_completed").name, "បានបញ្ចប់")
        # Français : seuls les textes absents des modules OCA sont complétés.
        en_francais = self.env(context={"lang": "fr_FR"})
        self.assertEqual(en_francais.ref("fieldservice.fsm_stage_completed").name, "Terminé")
        self.assertIn("Vos contrats", en_francais.ref("contract.portal_my_home_contract").arch_db)
        self.assertIn("Adresses", en_francais.ref("portal.portal_my_home").arch_db, "traduction d'Odoo conservée")

    def test_traductions_remises_quand_odoo_recharge_un_module(self):
        """Mise à jour d'un module OCA, langue réactivée : nos traductions sont remises aussitôt."""
        etape = self.env.ref("fieldservice.fsm_stage_completed")
        etape.with_context(lang="km_KH").name = "Completed"
        etape.with_context(lang="fr_FR").name = "Completed"
        pays = self.env.ref("base.kh")
        pays.with_context(lang="km_KH").name = "Cambodia"
        self.env["ir.module.module"]._load_module_terms(["fieldservice"], ["km_KH", "fr_FR"], overwrite=True)
        self.env.invalidate_all()
        self.assertEqual(etape.with_context(lang="km_KH").name, "បានបញ្ចប់")
        self.assertEqual(etape.with_context(lang="fr_FR").name, "Terminé")
        self.assertEqual(pays.with_context(lang="km_KH").name, "Cambodia", "module base non rechargé : inchangé")
        self.env["ir.module.module"]._load_module_terms(["base"], ["km_KH"])
        self.env.invalidate_all()
        self.assertEqual(pays.with_context(lang="km_KH").name, "កម្ពុជា")

    def test_traduction_corrigee_remplace_l_ancienne(self):
        """Après relecture, le fichier corrigé remplace l'ancienne traduction, même sur un
        enregistrement qu'Odoo protège des mises à jour (étape, modèle de courriel)."""
        etape = self.env.ref("helpdesk_mgmt.helpdesk_ticket_stage_done")
        modele = self.env.ref("account.email_template_edi_invoice")
        self.assertTrue(self.env["ir.model.data"].search([
            ("module", "=", "account"), ("name", "=", "email_template_edi_invoice")]).noupdate)
        bonne_traduction = modele.with_context(lang="km_KH").body_html
        self.assertIn("វិក្កយបត្រ", bonne_traduction)
        etape.with_context(lang="km_KH").name = "ancienne traduction"
        modele.with_context(lang="km_KH").body_html = bonne_traduction.replace("វិក្កយបត្រ", "ancienne traduction")
        self.env["chantrea.traductions.clients"]._charger()
        self.env.invalidate_all()
        self.assertEqual(etape.with_context(lang="km_KH").name, "រួចរាល់")
        corps = modele.with_context(lang="km_KH").body_html
        self.assertNotIn("ancienne traduction", corps)
        self.assertEqual(corps.count("វិក្កយបត្រ"), bonne_traduction.count("វិក្កយបត្រ"))

    def test_textes_du_code_completes(self):
        python = code_translations.get_python_translations
        self.assertEqual(python("helpdesk_mgmt", "km_KH").get("Newest"), "ថ្មីបំផុត")
        self.assertEqual(python("fieldservice_portal", "km_KH").get("Search in All"), "ស្វែងរកក្នុងទាំងអស់")
        self.assertEqual(python("portal", "km_KH").get("Some required fields are empty."),
                         "ព័ត៌មានចាំបាច់ខ្លះមិនទាន់បានបំពេញ។")
        self.assertEqual(python("contract", "fr_FR").get("All"), "Tous")
        self.assertNotIn("Newest", python("helpdesk_mgmt", "en_US"))

        def javascript(module, langue):
            return {m["id"]: m["string"] for m in code_translations.get_web_translations(module, langue)["messages"]}

        self.assertEqual(javascript("web", "km_KH").get("Draw"), "គូរ")
        self.assertEqual(javascript("portal", "km_KH").get("Due today"), "ផុតកំណត់ថ្ងៃនេះ")
        self.assertEqual(javascript("mail", "km_KH").get("The conversation is empty."), "មិនទាន់មានសារនៅឡើយទេ។")
        # Les traductions d'Odoo restent en place (ici le français du module web).
        self.assertEqual(javascript("web", "fr_FR").get("Draw"), "Dessiner")
        self.assertGreater(len(javascript("web", "fr_FR")), 500)


@tagged("post_install", "-at_install", "chantrea")
class TestPagesEnKhmer(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        contact = cls.env["res.partner"].create({"name": "Vanna (traductions)", "email": "vanna@test.example",
                                                 "lang": "km_KH"})
        cls.env["res.users"].with_context(no_reset_password=True).create({
            "name": contact.name, "login": "vanna-traductions", "password": MOT_DE_PASSE,
            "partner_id": contact.id, "group_ids": [(6, 0, cls.env.ref("base.group_portal").ids)]})
        cls.env["helpdesk.ticket"].create({"name": "Souris (traductions)", "description": "<p>x</p>",
                                           "partner_id": contact.id})

    def test_liste_des_tickets_en_khmer(self):
        self.authenticate("vanna-traductions", MOT_DE_PASSE)
        page = self.url_open("/km/my/tickets").text
        self.assertIn("Souris (traductions)", page)
        for texte in ("ថ្មីបំផុត", "ស្វែងរកក្នុងទាំងអស់", "ដំណាក់កាល", "តម្រៀបតាម"):
            self.assertIn(texte, page, "tris et recherche de la liste (textes du code Python) en khmer")
        for texte in ("Newest", "Search in All", "Sort By"):
            self.assertNotIn(texte, page)

    def test_traductions_javascript_demandees_dans_la_langue_de_la_page(self):
        """Odoo 19 sans « website » : sans l'attribut lang, aucune traduction JavaScript n'est chargée."""
        self.authenticate("vanna-traductions", MOT_DE_PASSE)
        self.assertRegex(self.url_open("/km/my").text, r'<html[^>]*\blang="km-KH"')
        self.assertRegex(self.url_open("/fr/my").text, r'<html[^>]*\blang="fr-FR"')
        francais = self.url_open("/website/translations?lang=fr_FR").json()
        self.assertEqual(francais["lang"], "fr_FR")
        messages = {m["id"]: m["string"] for m in francais["modules"]["web"]["messages"]}
        self.assertEqual(messages.get("Draw"), "Dessiner")
        khmer = self.url_open("/website/translations?lang=km_KH").json()
        messages = {m["id"]: m["string"] for module in khmer["modules"].values() for m in module["messages"]}
        self.assertEqual(messages.get("Draw"), "គូរ")
        self.assertEqual(messages.get("Write a message…"), "សរសេរសារ…")
