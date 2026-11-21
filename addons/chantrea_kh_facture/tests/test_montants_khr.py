"""Calcul du total en riels (règles d'arrondi), sans base de données de factures."""
from odoo.tests import TransactionCase, tagged

from ..models import montants_khr


@tagged("post_install", "-at_install", "chantrea")
class TestMontantsKhr(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.usd = cls.env.ref("base.USD")
        cls.khr = cls.env.ref("base.KHR")

    def calculer(self, devise, ht, tva, total, taux):
        return montants_khr.calculer(devise, ht, tva, total, taux, self.usd, self.khr)

    def test_facture_usd_avec_tva(self):
        m = self.calculer(self.usd, 450.0, 45.0, 495.0, 4063)
        self.assertEqual(m["total_khr"], 2_011_185)   # 495 × 4063
        self.assertEqual(m["tva_khr"], 182_835)       # 45 × 4063
        self.assertEqual(m["ht_khr"], 1_828_350)
        self.assertEqual(m["total_usd"], 495.0)

    def test_ht_plus_tva_egale_total(self):
        # Montants « difficiles » : la somme des arrondis doit rester égale au total.
        m = self.calculer(self.usd, 97.50, 9.75, 107.25, 4063)
        self.assertEqual(m["total_khr"], 435_757)     # 435 756,75 → 435 757
        self.assertEqual(m["ht_khr"] + m["tva_khr"], m["total_khr"])

    def test_arrondi_au_riel_le_plus_proche(self):
        self.assertEqual(self.calculer(self.usd, 33.33, 0, 33.33, 4063)["total_khr"], 135_420)  # 135 419,79
        self.assertEqual(self.calculer(self.usd, 10.01, 0, 10.01, 4050)["total_khr"], 40_541)   # 40 540,5 → vers le haut
        self.assertEqual(self.calculer(self.usd, 10.01, 0, 10.01, 4049)["total_khr"], 40_530)   # 40 530,49

    def test_document_en_riels(self):
        m = self.calculer(self.khr, 369_364, 36_936, 406_300, 4063)
        self.assertEqual(m["total_khr"], 406_300)
        self.assertEqual(m["total_usd"], 100.0)

    def test_sans_taux_rien_n_est_calcule(self):
        self.assertIsNone(self.calculer(self.usd, 100, 10, 110, 0))
        self.assertIsNone(self.calculer(self.env.ref("base.EUR"), 100, 10, 110, 4063))
