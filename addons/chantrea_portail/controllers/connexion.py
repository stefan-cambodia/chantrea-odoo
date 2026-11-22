"""Langue de l'espace client après connexion.

Odoo choisit la langue des pages client d'abord d'après le cookie
« frontend_lang », posé dès la page de connexion avec la langue par défaut.
Sans correction, un client réglé en khmer reste dans la langue de la page de
connexion. Ici, une connexion réussie aligne le cookie sur la langue du compte.
"""
from odoo import http
from odoo.http import request

from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class ChantreaConnexion(AuthSignupHome):

    @http.route()
    def web_login(self, *args, **kw):
        response = super().web_login(*args, **kw)
        uid = request.session.uid
        if request.httprequest.method == "POST" and uid:
            langue = request.env["res.users"].sudo().browse(uid).lang
            if langue and hasattr(response, "set_cookie"):
                response.set_cookie("frontend_lang", langue, max_age=365 * 24 * 3600, path="/")
        return response
