"""Lecture du taux officiel et tâche planifiée (sans accès Internet : pages enregistrées)."""
from datetime import date
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged
from odoo.tools import file_open

from ..models import taux_officiel


def page(nom):
    with file_open(f"chantrea_kh_facture/tests/data/{nom}") as fichier:
        return fichier.read()


@tagged("post_install", "-at_install", "chantrea")
class TestAnalysePages(TransactionCase):

    def test_page_gdt(self):
        taux = taux_officiel.analyser_gdt(page("gdt_extrait.html"))
        self.assertEqual(len(taux), 14)
        self.assertEqual(taux[date(2026, 11, 20)], 4063)
        self.assertEqual(taux[date(2026, 11, 2)], 4080)
        self.assertNotIn(date(2026, 11, 21), taux, "pas de publication le samedi")

    def test_page_nbc(self):
        self.assertEqual(taux_officiel.analyser_nbc(page("nbc_extrait.html")), {date(2026, 11, 26): 4059})

    def test_page_inconnue(self):
        self.assertEqual(taux_officiel.analyser_gdt("<html>maintenance</html>"), {})
        self.assertEqual(taux_officiel.analyser_nbc("<html>maintenance</html>"), {})

    def test_garde_fous(self):
        self.assertIsNone(taux_officiel.verifier(4063, 4066))
        self.assertTrue(taux_officiel.verifier(406.3))           # virgule mal placée
        self.assertTrue(taux_officiel.verifier(40630))
        self.assertTrue(taux_officiel.verifier(4500, 4063))      # saut de plus de 5 %


@tagged("post_install", "-at_install", "chantrea")
class TestTacheTaux(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.khr = cls.env.ref("base.KHR")
        cls.Taux = cls.env["res.currency.rate"]
        cls.Taux.search([("currency_id", "=", cls.khr.id)]).unlink()
        cls.Taux.create({"currency_id": cls.khr.id, "name": "2026-11-19", "rate": 4066,
                         "company_id": cls.company.root_id.id, "chantrea_source": "gdt"})
        cls.admin = cls.env.ref("base.user_admin")
        cls.admin.email = "admin@example.com"
        cls.company.chantrea_taux_source = "gdt"
        cls.company.chantrea_taux_alerte_user_id = cls.admin

    def lancer(self, aujourd_hui, publies=None, erreur=None):
        def faux_telechargement(source, timeout=30):
            if erreur:
                raise taux_officiel.ErreurTaux(erreur)
            return publies
        classe = type(self.Taux)
        with patch.object(taux_officiel, "telecharger", faux_telechargement), \
                patch.object(classe, "_chantrea_aujourdhui", lambda self: aujourd_hui):
            return self.Taux._chantrea_recuperer_taux(self.company)

    def alertes(self):
        return self.env["mail.mail"].search([("subject", "ilike", "USD/KHR"), ("email_to", "=", "admin@example.com")])

    def taux_khr(self, jour):
        return self.Taux.search([("currency_id", "=", self.khr.id), ("name", "=", jour)])

    def test_jour_ouvre_taux_publie(self):
        resultat = self.lancer(date(2026, 11, 20), {date(2026, 11, 19): 4066, date(2026, 11, 20): 4063})
        self.assertEqual(self.taux_khr("2026-11-20").rate, 4063)
        self.assertEqual(self.taux_khr("2026-11-20").chantrea_source, "gdt")
        self.assertEqual(len(resultat["crees"]), 1, "le 19 existait déjà : pas de doublon")
        self.assertFalse(resultat["problemes"])
        self.assertFalse(self.alertes())

    def test_echec_aucun_taux_invente_et_alerte(self):
        resultat = self.lancer(date(2026, 11, 20), erreur="délai dépassé")
        self.assertFalse(self.taux_khr("2026-11-20"), "aucun taux ne doit être inventé")
        self.assertEqual(resultat["taux_en_vigueur"], 4066, "le dernier taux publié reste en vigueur")
        alerte = self.alertes()
        self.assertEqual(len(alerte), 1)
        self.assertIn("délai dépassé", alerte.body_html)
        self.assertIn("4066", alerte.body_html)

    def test_week_end_sans_publication_pas_d_alerte(self):
        resultat = self.lancer(date(2026, 11, 21), {date(2026, 11, 19): 4066})  # samedi
        self.assertFalse(resultat["problemes"])
        self.assertFalse(self.alertes())

    def test_date_future_rejetee(self):
        resultat = self.lancer(date(2026, 11, 20), {date(2026, 11, 20): 4063, date(2026, 11, 26): 4059})
        self.assertFalse(self.taux_khr("2026-11-26"))
        self.assertEqual(self.taux_khr("2026-11-20").rate, 4063)
        self.assertTrue(any("2026-11-26" in p for p in resultat["problemes"]))
        self.assertTrue(self.alertes())

    def test_valeur_invraisemblable_rejetee(self):
        resultat = self.lancer(date(2026, 11, 20), {date(2026, 11, 20): 406.3})
        self.assertFalse(self.taux_khr("2026-11-20"))
        self.assertTrue(resultat["problemes"])
        self.assertTrue(self.alertes())

    def test_saisie_manuelle_jamais_ecrasee(self):
        self.Taux.create({"currency_id": self.khr.id, "name": "2026-11-20", "rate": 4070,
                          "company_id": self.company.root_id.id, "chantrea_source": "manuel"})
        self.lancer(date(2026, 11, 20), {date(2026, 11, 20): 4063})
        self.assertEqual(self.taux_khr("2026-11-20").rate, 4070)
        self.assertEqual(self.taux_khr("2026-11-20").chantrea_source, "manuel")
