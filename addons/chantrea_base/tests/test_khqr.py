"""KHQR (Bakong) : QR codes conformes aux règles du SDK de la Banque nationale du Cambodge."""
import time

from odoo.tests import TransactionCase, tagged

# Longueurs maximales du SDK bakong-khqr (constant/index.js, INVALID_LENGTH).
MAXI = {"29": 99, "54": 13, "59": 25, "60": 15}


def crc16(donnees):
    crc = 0xFFFF
    for octet in donnees.encode():
        crc ^= octet << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
    return crc & 0xFFFF


def decoder(chaine):
    """Découpe un QR code EMV en {tag: valeur} et vérifie la somme de contrôle."""
    tags, i = {}, 0
    while i < len(chaine):
        tag, longueur = chaine[i:i + 2], int(chaine[i + 2:i + 4])
        tags[tag] = chaine[i + 4:i + 4 + longueur]
        i += 4 + longueur
    assert chaine[-8:-4] == "6304", "la somme de contrôle doit être le dernier champ"
    assert int(tags["63"], 16) == crc16(chaine[:-4]), "somme de contrôle fausse"
    return tags


@tagged("post_install", "-at_install", "chantrea")
class TestKhqr(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.usd, cls.khr = cls.env.ref("base.USD"), cls.env.ref("base.KHR")
        partenaire = cls.env["res.partner"].create({
            "name": "Chantrea Systems", "city": "Kampot", "country_id": cls.env.ref("base.kh").id})
        cls.compte = cls.env["res.partner.bank"].create({
            "acc_number": "KHQR-TEST-1", "partner_id": partenaire.id, "proxy_type": "bakong_id_solo",
            "proxy_value": "chantrea_test@aclb", "include_reference": True})

    def qr(self, montant, devise, reference="Shop/0001 101"):
        return decoder(self.compte._get_qr_vals("emv_qr", montant, devise, False, reference, ""))

    def test_qr_en_dollars(self):
        t = self.qr(12.5, self.usd)
        self.assertEqual(t["00"], "01")
        self.assertEqual(t["01"], "12", "QR code dynamique : il a un montant")
        self.assertEqual(t["29"], "0018chantrea_test@aclb")
        self.assertEqual(t["53"], "840")
        self.assertEqual(t["54"], "12.50", "deux décimales en dollars, comme le SDK")
        self.assertEqual(t["58"], "KH")
        self.assertEqual(t["59"], "Chantrea Systems")
        self.assertEqual(t["60"], "Kampot")
        self.assertEqual(t["62"], "0113Shop/0001 101")
        for tag, maxi in MAXI.items():
            self.assertLessEqual(len(t[tag]), maxi, tag)

    def test_qr_en_riels_montant_entier(self):
        t = self.qr(50800, self.khr)
        self.assertEqual(t["53"], "116")
        self.assertEqual(t["54"], "50800")
        self.assertEqual(self.qr(12.0, self.usd)["54"], "12")

    def test_montant_calcule_en_virgule_flottante(self):
        self.assertEqual(self.qr(0.1 + 0.2, self.usd)["54"], "0.30")

    def test_horodatage_du_qr_dynamique(self):
        t = self.qr(12.5, self.usd)
        creation, expiration = t["99"][4:17], t["99"][21:34]
        self.assertTrue(t["99"].startswith("0013") and t["99"][17:21] == "0113")
        maintenant = time.time() * 1000
        self.assertLess(abs(int(creation) - maintenant), 60_000)
        self.assertGreater(int(expiration), maintenant)

    def test_qr_sans_montant_statique(self):
        t = self.qr(0.0, self.usd)
        self.assertEqual(t["01"], "11", "sans montant, le QR code est statique")
        self.assertNotIn("54", t)
        self.assertNotIn("99", t, "pas d'horodatage sur un QR code statique")

    def test_reference_limitee_a_25_caracteres(self):
        t = self.qr(5, self.usd, reference="Commande 0123456789 0123456789 0123456789")
        self.assertEqual(t["62"], "0125Commande 0123456789 01234")
