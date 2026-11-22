"""Correctif de sécurité de la route OCA « /my/sign/<id>/download » (sign_oca 19.0).

La route d'origine lit la demande de signature en sudo d'après le seul numéro
envoyé et renvoie un lien de téléchargement du document signé : n'importe quel
utilisateur connecté (un client) peut télécharger les documents signés de tous
les autres, en essayant les numéros un par un.

Ici : le document n'est servi qu'à un signataire de la demande (ou à un collègue
de sa société), ou à un utilisateur interne qui a le droit de lire la demande.
"""
from werkzeug.exceptions import NotFound

from odoo import http
from odoo.http import request

from odoo.addons.sign_oca.controllers.main import PortalSign


class ChantreaPortalSign(PortalSign):

    @http.route()
    def portal_download_signed(self, request_id, **kw):
        utilisateur = request.env.user
        demande = request.env["sign.oca.request"].sudo().browse(request_id).exists()
        if not demande:
            raise NotFound()
        if utilisateur._is_internal():
            autorise = request.env["sign.oca.request"].browse(request_id).has_access("read")
        else:
            societe = utilisateur.partner_id.commercial_partner_id
            autorise = bool(demande.signer_ids.filtered(
                lambda s: s.partner_id.commercial_partner_id == societe))
        if not autorise:
            raise NotFound()
        return super().portal_download_signed(request_id, **kw)
