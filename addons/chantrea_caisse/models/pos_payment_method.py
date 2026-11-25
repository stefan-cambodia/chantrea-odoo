import base64
import hashlib
import logging
import re

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.image import image_data_uri

_logger = logging.getLogger(__name__)

# API Bakong de la Banque nationale du Cambodge (https://api-bakong.nbc.gov.kh/document) :
# une transaction se retrouve par l'empreinte MD5 du texte du QR code payé.
BAKONG_URL_DEFAUT = "https://api-bakong.nbc.gov.kh"
PARAM_JETON = "chantrea_caisse.bakong_token"
PARAM_URL = "chantrea_caisse.bakong_url"


class PosPaymentMethod(models.Model):
    _inherit = "pos.payment.method"

    chantrea_khqr_riels = fields.Boolean(
        string="QR code in riels",
        help="The KHQR code asks for the amount in riels, converted at the till rate "
             "and rounded up to the riel rounding. Otherwise it asks for dollars.")

    @api.model
    def _load_pos_data_fields(self, config):
        return super()._load_pos_data_fields(config) + ["qr_code_method", "chantrea_khqr_riels"]

    @api.constrains("chantrea_khqr_riels", "payment_method_type", "qr_code_method")
    def _check_chantrea_khqr_riels(self):
        for methode in self.filtered("chantrea_khqr_riels"):
            if methode.payment_method_type != "qr_code" or methode.qr_code_method != "emv_qr":
                raise ValidationError(_(
                    "Only a QR code payment method (EMV / KHQR) can ask for riels: %s.", methode.name))

    # --- QR code KHQR et vérification du paiement auprès de Bakong ---------------------------
    @api.model
    def _chantrea_bakong(self):
        """Jeton et adresse de l'API Bakong ; pas de jeton, pas de vérification automatique."""
        parametres = self.env["ir.config_parameter"].sudo()
        jeton = (parametres.get_param(PARAM_JETON) or "").strip()
        url = (parametres.get_param(PARAM_URL) or "").strip() or BAKONG_URL_DEFAUT
        return jeton, url.rstrip("/")

    def chantrea_qr_khqr(self, amount, reference, currency_id, partner_id=False):
        """QR code KHQR de la caisse, avec l'empreinte MD5 de son texte.

        Le texte n'est calculé qu'une fois : il contient l'heure de création (étiquette 99),
        l'image et l'empreinte doivent donc venir du même calcul."""
        self.ensure_one()
        if self.payment_method_type != "qr_code" or self.qr_code_method != "emv_qr":
            raise UserError(_("This payment method is not configured to generate QR codes."))
        banque = self.journal_id.bank_account_id.with_context(is_online_qr=True)
        devise = self.env["res.currency"].browse(currency_id)
        partenaire = self.env["res.partner"].browse(partner_id or [])
        vals = banque._build_qr_code_vals(
            float(amount), reference, "", devise, partenaire, self.qr_code_method, silent_errors=False)
        if not vals:
            raise UserError(_("No KHQR code can be generated for the bank account of %s.", self.name))
        parametres = banque._get_qr_code_generation_params(**vals)
        image = self.env["ir.actions.report"].barcode(**parametres)
        jeton, _url = self._chantrea_bakong()
        return {
            "qr": image_data_uri(base64.b64encode(image)),
            "md5": hashlib.md5(parametres["value"].encode()).hexdigest(),
            "verification": bool(jeton),
        }

    def chantrea_verifier_khqr(self, md5, amount, currency_id):
        """Demande à Bakong si le QR code d'empreinte « md5 » a été payé.

        Réponse : {"etat": …} avec etat = « paye » (et « hash », la référence Bakong),
        « attente », « ecart » (un paiement qui ne correspond pas), « erreur » ou « inactif »
        (pas de jeton : la caissière confirme elle-même)."""
        self.ensure_one()
        jeton, url = self._chantrea_bakong()
        if not jeton:
            return {"etat": "inactif"}
        if not isinstance(md5, str) or not re.fullmatch(r"[0-9a-f]{32}", md5):
            return {"etat": "erreur", "message": _("Invalid QR code fingerprint.")}
        try:
            reponse = requests.post(
                f"{url}/v1/check_transaction_by_md5", json={"md5": md5},
                headers={"Authorization": f"Bearer {jeton}"}, timeout=10)
        except requests.RequestException as erreur:
            _logger.warning("Bakong injoignable : %s", erreur)
            return {"etat": "erreur", "message": _(
                "The Bakong service cannot be reached: check the payment in the banking app.")}
        if reponse.status_code in (401, 403):
            _logger.warning("Bakong refuse le jeton (HTTP %s)", reponse.status_code)
            return {"etat": "erreur", "message": _(
                "Bakong refuses the token (expired?): renew it in the Point of Sale settings.")}
        try:
            donnees = reponse.json()
        except ValueError:
            donnees = None
        if reponse.status_code != 200 or not isinstance(donnees, dict):
            _logger.warning("Réponse Bakong inattendue (HTTP %s) : %.300s", reponse.status_code, reponse.text)
            return {"etat": "erreur", "message": _(
                "Unexpected answer from Bakong: check the payment in the banking app.")}
        transaction = donnees.get("data")
        if donnees.get("responseCode") != 0 or not isinstance(transaction, dict):
            # responseCode 1, errorCode 1 : pas (encore) de transaction pour ce QR code.
            return {"etat": "attente"}
        return self._chantrea_controler_transaction(transaction, amount, currency_id)

    def _chantrea_controler_transaction(self, transaction, amount, currency_id):
        """Le paiement trouvé doit aller au compte de la caisse, dans la devise et pour le montant du QR code."""
        devise = self.env["res.currency"].browse(currency_id)
        compte = (self.journal_id.bank_account_id.proxy_value or "").lower()
        try:
            montant = float(transaction.get("amount"))
        except (TypeError, ValueError):
            montant = None
        conforme = (
            montant is not None
            and (transaction.get("currency") or "").upper() == devise.name
            and devise.compare_amounts(montant, float(amount)) >= 0
            and (transaction.get("toAccountId") or "").lower() == compte
        )
        if not conforme:
            _logger.warning("Paiement Bakong non conforme pour %s : %s", self.name, transaction)
            return {"etat": "ecart", "message": _(
                "A payment was found but does not match this QR code (%(amount)s %(currency)s to %(account)s).",
                amount=transaction.get("amount"), currency=transaction.get("currency"),
                account=transaction.get("toAccountId"))}
        return {"etat": "paye", "hash": transaction.get("hash") or "", "payeur": transaction.get("fromAccountId") or ""}
