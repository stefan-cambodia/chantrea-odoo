"""Caisse en dollars qui accepte les riels : taux, commandes, clôture, KHQR en riels."""
import uuid

from odoo import fields
from odoo.exceptions import ValidationError
from psycopg2 import IntegrityError

from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger

from odoo.addons.chantrea_caisse.models.pos_config import arrondir_riels


@tagged("post_install", "-at_install", "chantrea")
class TestCaisse(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env.user.group_ids |= cls.env.ref("point_of_sale.group_pos_manager")
        cls.company = cls.env.company
        cls.usd, cls.khr = cls.env.ref("base.USD"), cls.env.ref("base.KHR")
        # Taux maîtrisés : on part d'une table vide.
        cls.env["res.currency.rate"].search([("currency_id", "=", cls.khr.id)]).unlink()
        cls.env["res.currency.rate"].create({
            "currency_id": cls.khr.id, "name": fields.Date.today(), "rate": 4063,
            "company_id": cls.company.root_id.id, "chantrea_source": "gdt"})
        cls.config = cls.env["pos.config"].create({"name": "Caisse de test"})
        cls.config._create_journal_and_payment_methods(cash_journal_vals={"name": "Caisse test", "code": "CTST"})
        cls.especes = cls.config.payment_method_ids.filtered("is_cash_count")
        cls.produit = cls.env["product.product"].create({
            "name": "Câble HDMI (test)", "list_price": 12.5, "available_in_pos": True, "taxes_id": [(5, 0, 0)]})

    def commande(self, session, total, paiements, rendu=0.0, **valeurs):
        """Commande telle que la caisse l'envoie (montants déjà calculés par la caisse).
        Odoo 19 compte la monnaie rendue en négatif (amount_return)."""
        return {
            "uuid": str(uuid.uuid4()),
            "name": "Commande test",
            "session_id": session.id,
            "user_id": self.env.uid,
            "pricelist_id": self.config.pricelist_id.id,
            "date_order": fields.Datetime.to_string(fields.Datetime.now()),
            "state": "paid",
            "amount_total": total, "amount_tax": 0.0,
            "amount_paid": sum(p["amount"] for p in paiements), "amount_return": rendu,
            "lines": [(0, 0, {"product_id": self.produit.id, "qty": total / 12.5, "price_unit": 12.5,
                              "price_subtotal": total, "price_subtotal_incl": total, "tax_ids": []})],
            "payment_ids": [(0, 0, {"payment_method_id": self.especes.id, "name": fields.Datetime.now(), **p})
                            for p in paiements],
            **valeurs,
        }

    # --- Taux de la caisse ---------------------------------------------------------------
    def test_taux_officiel_du_jour(self):
        self.assertEqual(self.config.chantrea_taux_mode, "officiel")
        self.assertEqual(self.config.chantrea_taux_caisse, 4063)

    def test_taux_fixe(self):
        self.config.write({"chantrea_taux_mode": "fixe", "chantrea_taux_fixe": 4000})
        self.assertEqual(self.config.chantrea_taux_caisse, 4000)

    def test_sans_taux_officiel_rien_n_est_invente(self):
        self.env["res.currency.rate"].search([("currency_id", "=", self.khr.id)]).unlink()
        self.config.invalidate_recordset(["chantrea_taux_caisse"])
        self.assertEqual(self.config.chantrea_taux_caisse, 0)

    @mute_logger("odoo.sql_db")
    def test_taux_fixe_nul_refuse(self):
        with self.assertRaises(IntegrityError), self.cr.savepoint():
            self.config.write({"chantrea_taux_mode": "fixe", "chantrea_taux_fixe": 0})
            self.config.flush_recordset()

    def test_arrondi_comme_la_caisse(self):
        """Même règle que static/src/js/riels.js (testé avec Node)."""
        self.assertEqual(arrondir_riels(50787.5, 100, "haut"), 50800)
        self.assertEqual(arrondir_riels(3049, 100), 3000)
        self.assertEqual(arrondir_riels(3050, 100), 3100)
        self.assertEqual(arrondir_riels(0.1 * 3 * 1000, 100, "haut"), 300)

    # --- Chargement dans la caisse ---------------------------------------------------------
    def test_riel_et_taux_charges_dans_la_caisse(self):
        self.config.open_ui()
        session = self.config.current_session_id
        donnees = session.load_data([])
        devises = {d["name"] for d in donnees["res.currency"]}
        self.assertIn("KHR", devises)
        self.assertIn("USD", devises)
        self.assertEqual(donnees["pos.config"][0]["chantrea_taux_caisse"], 4063)
        self.assertIn("chantrea_khqr_riels", donnees["pos.payment.method"][0])
        self.assertIn("qr_code_method", donnees["pos.payment.method"][0])

    # --- Commandes et clôture --------------------------------------------------------------
    def test_riels_du_tiroir_a_la_cloture(self):
        self.config.open_ui()
        session = self.config.current_session_id
        session.set_opening_control(0, None)
        commandes = [
            # 12,50 $ payés 10 $ + 10 200 ៛ (≈ 2,51 $) ; rendu 0,01 $ : rien en riels.
            self.commande(session, 12.5, [{"amount": 12.51, "chantrea_especes_usd": 10, "chantrea_montant_khr": 10200}],
                          rendu=-0.01, chantrea_taux=4063, chantrea_rendu_khr=0),
            # 25 $ payés avec un billet de 50 $ : rendu 25 $, rien en riels.
            self.commande(session, 25.0, [{"amount": 50.0, "chantrea_especes_usd": 50}],
                          rendu=-25.0, chantrea_taux=4063, chantrea_rendu_usd=25),
            # 12,50 $ payés 20 $ : rendu 7,50 $ = 7 $ + 2 000 ៛.
            self.commande(session, 12.5, [{"amount": 20.0, "chantrea_especes_usd": 20}],
                          rendu=-7.5, chantrea_taux=4063, chantrea_rendu_usd=7, chantrea_rendu_khr=2000),
        ]
        self.env["pos.order"].sync_from_ui(commandes)
        ordres = session.order_ids
        self.assertEqual(len(ordres), 3)
        self.assertEqual(sorted(ordres.mapped("chantrea_rendu_khr")), [0, 0, 2000])
        recu = ordres.payment_ids.filtered("chantrea_montant_khr")
        self.assertEqual(recu.chantrea_montant_khr, 10200)
        self.assertEqual(recu.chantrea_especes_usd, 10)

        donnees = session.get_closing_control_data()
        riels = donnees["default_cash_details"]["chantrea_riels"]
        self.assertEqual(riels["recus"], 10200)
        self.assertEqual(riels["rendus"], 2000)
        self.assertEqual(riels["net"], 8200)
        attendu = donnees["default_cash_details"]["amount"]
        self.assertAlmostEqual(attendu, 50.0, places=2)  # 82,51 reçus − 32,51 rendus
        # Billets en dollars : 10 + 50 + 20 reçus, 25 + 7 rendus.
        self.assertAlmostEqual(riels["dollars_attendus"], 48.0, places=2)
        self.assertAlmostEqual(riels["valeur_usd"], 2.0, places=2)
        self.assertAlmostEqual(riels["taux"], 4100, places=0)
        # Compter exactement les billets attendus ne crée aucun écart.
        self.assertAlmostEqual(riels["dollars_attendus"] + riels["net"] / riels["taux"], attendu, places=2)

    def test_cloture_sans_riels(self):
        self.config.open_ui()
        session = self.config.current_session_id
        session.set_opening_control(0, None)
        self.env["pos.order"].sync_from_ui([self.commande(session, 12.5, [{"amount": 12.5}], chantrea_taux=4063)])
        riels = session.get_closing_control_data()["default_cash_details"]["chantrea_riels"]
        self.assertEqual(riels["net"], 0)
        self.assertEqual(riels["taux"], 4063)

    # --- KHQR en riels ---------------------------------------------------------------------
    def test_khqr_en_riels(self):
        partenaire = self.company.partner_id
        compte = self.env["res.partner.bank"].create({
            "acc_number": "KHQR-CAISSE-1", "partner_id": partenaire.id, "proxy_type": "bakong_id_solo",
            "proxy_value": "chantrea_test@aclb"})
        journal = self.env["account.journal"].create({
            "name": "KHQR test", "type": "bank", "code": "KHQT", "bank_account_id": compte.id})
        methode = self.env["pos.payment.method"].create({
            "name": "KHQR riels", "journal_id": journal.id, "payment_method_type": "qr_code",
            "qr_code_method": "emv_qr", "chantrea_khqr_riels": True})
        image = methode.get_qr_code(50800, "Commande 1", "", self.khr.id, False)
        self.assertTrue(image.startswith("data:image/png;base64,"))
        texte = compte._get_qr_vals("emv_qr", 50800, self.khr, False, "Commande 1", "")
        self.assertIn("5303116", texte)
        self.assertIn("540550800", texte)

    def test_khqr_en_riels_reserve_aux_qr_codes(self):
        with self.assertRaises(ValidationError):
            self.especes.chantrea_khqr_riels = True
