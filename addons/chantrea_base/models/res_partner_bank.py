"""KHQR (Bakong) : corrections du QR code d'Odoo 19 (l10n_kh) selon les règles du SDK
officiel de la Banque nationale du Cambodge (bakong-khqr) :

- montant : en riels, un nombre entier ; en dollars, deux décimales s'il y en a
  (« 12.50 », jamais « 12.5 » ni « 0.30000000000000004 ») ; 13 caractères au plus ;
- QR code sans montant : « statique » (11) et sans horodatage, et non « dynamique » (12),
  que les applications bancaires refusent sans montant ;
- numéro de facture (référence) : 25 caractères au plus.
"""
from odoo import models


class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"

    def _chantrea_montant_khqr(self, amount, currency):
        if currency.name == "KHR":
            return str(int(round(amount)))
        arrondi = round(amount, 2)
        return str(int(arrondi)) if arrondi == int(arrondi) else f"{arrondi:.2f}"

    def _get_qr_code_vals_list(self, qr_method, amount, currency, debtor_partner, free_communication, structured_communication):
        valeurs = super()._get_qr_code_vals_list(
            qr_method, amount, currency, debtor_partner, free_communication, structured_communication)
        if self.country_code != "KH":
            return valeurs
        sans_montant = not amount or currency.is_zero(amount)
        corrigees = []
        for tag, valeur in valeurs:
            if tag == 1:
                valeur = "11" if sans_montant else "12"
            elif tag == 54:
                valeur = None if sans_montant else self._chantrea_montant_khqr(amount, currency)
            elif tag == 99 and sans_montant:
                continue
            corrigees.append((tag, valeur))
        return corrigees

    def _get_additional_data_field(self, comment):
        if self.country_code == "KH":
            return self._serialize(1, (comment or "")[:25])
        return super()._get_additional_data_field(comment)
