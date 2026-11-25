"""Chiffres et dates en khmer (outils_km)."""
import datetime

from odoo.tests import TransactionCase, tagged

from odoo.addons.chantrea_base import outils_km
from odoo.addons.chantrea_base.outils_km import OutilsKm


@tagged("post_install", "-at_install", "chantrea")
class TestOutilsKm(TransactionCase):

    def test_chiffres(self):
        self.assertEqual(outils_km.chiffres("0123456789"), "០១២៣៤៥៦៧៨៩")
        self.assertEqual(outils_km.chiffres("INV/000042 - $ 1,234.50"), "INV/០០០០៤២ - $ ១,២៣៤.៥០")
        self.assertEqual(outils_km.chiffres(None), "")
        self.assertEqual(outils_km.chiffres(False), "")

    def test_date(self):
        self.assertEqual(outils_km.date(datetime.date(2026, 11, 26)), "ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦")
        self.assertEqual(outils_km.date(datetime.date(2027, 1, 5)), "ថ្ងៃទី០៥ ខែមករា ឆ្នាំ២០២៧")
        self.assertEqual(outils_km.date(False), "")

    def test_mois_comme_le_cldr(self):
        """Mêmes noms de mois que le référentiel Unicode (Babel), pour les 12 mois."""
        from babel.dates import format_date
        for mois in range(1, 13):
            jour = datetime.date(2026, mois, 1)
            self.assertEqual(outils_km.MOIS[mois - 1], format_date(jour, "MMMM", locale="km"))

    def test_date_heure_a_phnom_penh(self):
        # 23 h 30 UTC le 25 = 6 h 30 le 26 à Phnom Penh (UTC+7) : le jour change aussi.
        utc = datetime.datetime(2026, 11, 25, 23, 30)
        self.assertEqual(outils_km.date_heure(utc), "ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦ ម៉ោង ០៦:៣០")
        self.assertEqual(OutilsKm(self.env).date(utc), "ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦")

    def test_montants_au_format_de_la_ligne_anglaise(self):
        """Mêmes séparateurs que la ligne anglaise, quelle que soit la langue de l'utilisateur."""
        km = OutilsKm(self.env(context={"lang": "fr_FR"}))
        usd, khr = self.env.ref("base.USD"), self.env.ref("base.KHR")
        self.assertEqual(km.montant(1234.5, usd).replace("\xa0", " "), "$ ១,២៣៤.៥០")
        self.assertIn("២,០១១,១៨៥", km.montant(2011185, khr))
        self.assertEqual(km.nombre(4063), "៤,០៦៣")
        self.assertEqual(km.nombre(4063.25, 2), "៤,០៦៣.២៥")

    def test_cellule_de_tableau_comme_la_ligne_anglaise(self):
        """km.champ reprend le rendu anglais de t-field (décimales, symbole), chiffres khmers."""
        km = OutilsKm(self.env(context={"lang": "fr_FR"}))
        usd = self.env.ref("base.USD")
        self.env["res.lang"]._activate_lang("fr_FR")
        societe = self.env.company
        self.assertEqual(societe.currency_id, usd)
        partenaire = self.env["res.partner"].create({"name": "Client km.champ"})
        ligne = self.env["account.move"].create({
            "move_type": "out_invoice", "partner_id": partenaire.id,
            "invoice_line_ids": [(0, 0, {"name": "Maintenance", "quantity": 1234.5, "price_unit": 25, "tax_ids": []})],
        }).invoice_line_ids
        self.assertEqual(km.champ(ligne, "quantity"), "១,២៣៤.៥០")
        self.assertEqual(km.champ(ligne, "price_unit"), "២៥.០០")
        self.assertEqual(km.champ(ligne, "price_subtotal").replace("\xa0", " "), "$ ៣០,៨៦២.៥០")
