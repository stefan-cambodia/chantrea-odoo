"""Factures cambodgiennes : taux mémorisé, variantes TVA/commerciale, numérotation, impression."""
from odoo import fields
from odoo.exceptions import UserError
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install", "chantrea")
class TestFactureKh(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.usd = cls.env.ref("base.USD")
        cls.khr = cls.env.ref("base.KHR")
        cls.taxe = cls.env["account.tax"].create({
            "name": "TVA test 10 %",
            "amount": 10.0,
            "amount_type": "percent",
            "type_tax_use": "sale",
            "company_id": cls.company.id,
        })
        cls.client_tva = cls.env["res.partner"].create({"name": "Client assujetti (test)", "vat": "TEST-0001"})
        cls.client_sans_tva = cls.env["res.partner"].create({"name": "Client non assujetti (test)"})
        # Taux maîtrisés pour le test : on part d'une table vide.
        cls.Taux = cls.env["res.currency.rate"]
        cls.Taux.search([("currency_id", "=", cls.khr.id)]).unlink()
        cls.Taux.create({"currency_id": cls.khr.id, "name": "2026-11-20", "rate": 4063,
                         "company_id": cls.company.root_id.id, "chantrea_source": "gdt"})

    def facture(self, client, prix=450.0, date="2026-11-21", **valeurs):
        return self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": client.id,
            "invoice_date": date,
            "currency_id": self.usd.id,
            "invoice_line_ids": [(0, 0, {"name": "Maintenance", "quantity": 1,
                                         "price_unit": prix, "tax_ids": [(6, 0, self.taxe.ids)]})],
            **valeurs,
        })

    def rendu(self, rapport, ids):
        return self.env["ir.actions.report"]._render_qweb_html(rapport, ids)[0].decode()

    # --- Total en riels -------------------------------------------------------
    def test_total_riels_memorise_a_la_validation(self):
        f = self.facture(self.client_tva)
        self.assertFalse(f.chantrea_taux_khr, "aucun taux n'est fixé sur un brouillon")
        f.action_post()
        self.assertEqual(f.chantrea_taux_khr, 4063)
        self.assertEqual(f.chantrea_taux_date, fields.Date.to_date("2026-11-20"))
        self.assertEqual(f.chantrea_taux_source, "gdt")
        self.assertEqual(f.amount_total, 495.0)
        self.assertEqual(f.chantrea_total_khr, 2_011_185)
        self.assertEqual(f.chantrea_tva_khr, 182_835)
        self.assertEqual(f.chantrea_ht_khr, 1_828_350)
        self.assertEqual(f.chantrea_total_usd, 495.0)

    def test_taux_fige_apres_validation(self):
        f = self.facture(self.client_tva)
        f.action_post()
        # Un nouveau taux publié ensuite ne change pas une facture validée.
        self.Taux.create({"currency_id": self.khr.id, "name": "2026-11-21", "rate": 4100,
                          "company_id": self.company.root_id.id, "chantrea_source": "gdt"})
        f.invalidate_recordset()
        self.assertEqual(f.chantrea_taux_khr, 4063)
        self.assertEqual(f.chantrea_total_khr, 2_011_185)
        # Une nouvelle facture du même jour prend le nouveau taux.
        g = self.facture(self.client_tva)
        g.action_post()
        self.assertEqual(g.chantrea_taux_khr, 4100)
        self.assertEqual(g.chantrea_total_khr, 2_029_500)

    def test_sans_taux_la_validation_est_refusee(self):
        f = self.facture(self.client_tva, date="2026-01-05")  # avant tout taux connu
        with self.assertRaisesRegex(UserError, "2026-01-05"):
            f.action_post()

    def test_taux_saisi_a_la_main(self):
        f = self.facture(self.client_tva, chantrea_taux_khr=4000, chantrea_taux_date="2026-11-21")
        f.action_post()
        self.assertEqual(f.chantrea_taux_khr, 4000)
        self.assertEqual(f.chantrea_taux_source, "manuel")
        self.assertEqual(f.chantrea_total_khr, 1_980_000)

    def test_remise_en_brouillon_libere_le_taux(self):
        f = self.facture(self.client_tva)
        f.action_post()
        f.button_draft()
        self.assertFalse(f.chantrea_taux_khr)
        self.assertFalse(f.chantrea_total_khr)

    def test_avoir_reprend_le_taux_de_la_facture(self):
        f = self.facture(self.client_tva)
        f.action_post()
        # Un nouveau taux publié le jour de l'avoir ne doit pas être pris.
        self.Taux.create({"currency_id": self.khr.id, "name": "2026-11-21", "rate": 4200,
                          "company_id": self.company.root_id.id, "chantrea_source": "gdt"})
        assistant = self.env["account.move.reversal"].with_context(
            active_model="account.move", active_ids=f.ids).create({
                "date": "2026-11-21", "journal_id": f.journal_id.id, "reason": "test"})
        avoir = self.env["account.move"].browse(assistant.refund_moves()["res_id"])
        avoir.action_post()
        self.assertEqual(avoir.chantrea_taux_khr, 4063)
        self.assertEqual(avoir.chantrea_total_khr, 2_011_185)

    # --- Variantes ------------------------------------------------------------
    def test_type_propose_selon_le_client(self):
        self.assertEqual(self.facture(self.client_tva).chantrea_type_facture, "tva")
        self.assertEqual(self.facture(self.client_sans_tva).chantrea_type_facture, "commerciale")

    def test_facture_tva_exige_le_numero_du_client(self):
        f = self.facture(self.client_sans_tva, chantrea_type_facture="tva")
        with self.assertRaisesRegex(UserError, "VATTIN"):
            f.action_post()
        self.assertEqual(f.state, "draft")

    def test_facture_commerciale_sans_numero(self):
        f = self.facture(self.client_sans_tva)
        f.action_post()
        self.assertEqual(f.state, "posted")

    # --- Numérotation -----------------------------------------------------------
    def test_numerotation_unique_et_continue(self):
        factures = [
            self.facture(self.client_tva, date="2026-11-21"),
            self.facture(self.client_sans_tva, date="2026-11-21"),
            self.facture(self.client_tva, date="2026-12-31"),
            self.facture(self.client_sans_tva, date="2027-01-02"),  # pas de remise à zéro annuelle
        ]
        for f in factures:
            f.action_post()
        noms = [f.name for f in factures]
        for nom in noms:
            self.assertRegex(nom, r"^[A-Z]+/\d{6}$", "pas d'année dans le numéro")
        prefixes = {nom.split("/")[0] for nom in noms}
        self.assertEqual(len(prefixes), 1, "TVA et commerciale partagent la même série")
        numeros = [int(nom.split("/")[1]) for nom in noms]
        self.assertEqual(numeros, list(range(numeros[0], numeros[0] + 4)), noms)

    # --- Impression -------------------------------------------------------------
    def test_impression_facture_tva(self):
        f = self.facture(self.client_tva)
        f.action_post()
        html = self.rendu("account.account_invoices", f.ids)
        for attendu in ("វិក្កយបត្រអាករ", "TAX INVOICE", "TEST-0001", "2,011,185", "4,063", "20/11/2026",
                        "Sub-total in riels", f.name):
            self.assertTrue(attendu in html, f"absent du PDF : {attendu}")
        self.assertFalse("Provisional rate" in html, "taux définitif sur une facture validée")
        # Dates et montants aussi en chiffres khmers, au-dessus des chiffres habituels.
        for attendu in ("ថ្ងៃទី២១ ខែវិច្ឆិកា ឆ្នាំ២០២៦", "២,០១១,១៨៥", "៤៩៥.០០", "១ USD = ៤,០៦៣ KHR",
                        "ថ្ងៃទី២០ ខែវិច្ឆិកា ឆ្នាំ២០២៦"):
            self.assertTrue(attendu in html, f"absent du PDF : {attendu}")

    def test_impression_facture_commerciale(self):
        f = self.facture(self.client_sans_tva, prix=97.5)
        f.action_post()
        html = self.rendu("account.account_invoices", f.ids)
        for attendu in ("វិក្កយបត្រពាណិជ្ជកម្ម", "COMMERCIAL INVOICE", "435,757"):
            self.assertTrue(attendu in html, f"absent du PDF : {attendu}")
        self.assertFalse("Sub-total in riels" in html, "pas de détail HT/TVA en riels")

    def test_impression_devis(self):
        devis = self.env["sale.order"].create({
            "partner_id": self.client_tva.id,
            "date_order": "2026-11-21 05:00:00",
            "order_line": [(0, 0, {"name": "Wi-Fi", "product_uom_qty": 1, "price_unit": 450.0,
                                   "tax_ids": [(6, 0, self.taxe.ids)]})],
        })
        html = self.rendu("sale.action_report_saleorder", devis.ids)
        for attendu in ("សម្រង់តម្លៃ", "QUOTATION", "2,011,185", "Provisional rate",
                        "ថ្ងៃទី២១ ខែវិច្ឆិកា ឆ្នាំ២០២៦", "២,០១១,១៨៥"):
            self.assertTrue(attendu in html, f"absent du PDF : {attendu}")
