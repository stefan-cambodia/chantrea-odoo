"""Langue de la page de connexion et de l'espace client.

1. Page de connexion. Sans le module « website », Odoo sert /web/login hors de l'espace
   client : la page est toujours en anglais, même à l'adresse /km/web/login, et un mot de
   passe erroné ramène aussi à l'anglais. On donne à cette route les mêmes réglages que
   le module « website » (website=True, auth="public") : elle suit alors la langue de
   l'adresse (/km/…, /fr/…) ou celle du cookie « frontend_lang ».

2. Après connexion. Odoo choisit la langue des pages client d'abord d'après ce cookie,
   posé dès la page de connexion. Sans correction, un client réglé en khmer resterait
   dans la langue de la page de connexion : une connexion réussie aligne le cookie sur
   la langue du compte.
"""
from odoo import http
from odoo.http import request

from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class ChantreaConnexion(AuthSignupHome):

    @http.route(website=True, auth="public", sitemap=False)
    def web_login(self, *args, **kw):
        response = super().web_login(*args, **kw)
        uid = request.session.uid
        if request.httprequest.method == "POST" and uid:
            langue = request.env["res.users"].sudo().browse(uid).lang
            if langue and hasattr(response, "set_cookie"):
                response.set_cookie("frontend_lang", langue, max_age=365 * 24 * 3600, path="/")
        return response
