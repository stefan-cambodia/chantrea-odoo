import logging
from datetime import datetime, timedelta

import pytz
from markupsafe import Markup, escape

from odoo import api, fields, models

from . import taux_officiel

_logger = logging.getLogger(__name__)

SOURCES_TAUX = [
    ("gdt", "GDT"),
    ("nbc", "NBC"),
    ("manuel", "Manual entry"),
]
FUSEAU = "Asia/Phnom_Penh"
JOURS_RATTRAPAGE = 31


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    chantrea_source = fields.Selection(SOURCES_TAUX, string="Source", default="manuel")
    chantrea_releve_le = fields.Datetime("Retrieved on", readonly=True)

    # ------------------------------------------------------------------
    # Recherche
    # ------------------------------------------------------------------
    @api.model
    def _chantrea_taux_a_la_date(self, jour, company=None):
        """Dernier taux KHR publié au plus tard à `jour` (enregistrement, ou vide)."""
        company = company or self.env.company
        return self.search([
            ("currency_id", "=", self.env.ref("base.KHR").id),
            ("name", "<=", jour),
            ("company_id", "in", [False, company.root_id.id]),
        ], order="name desc", limit=1)

    def _chantrea_valeur(self, company=None):
        """Nombre de riels pour 1 USD (la société est en USD)."""
        self.ensure_one()
        return self.with_company(company or self.env.company).company_rate

    # ------------------------------------------------------------------
    # Tâche planifiée
    # ------------------------------------------------------------------
    @api.model
    def _chantrea_cron_taux_du_jour(self):
        usd = self.env.ref("base.USD")
        for company in self.env["res.company"].search([("currency_id", "=", usd.id), ("parent_id", "=", False)]):
            self.with_company(company)._chantrea_recuperer_taux(company)

    @api.model
    def _chantrea_aujourdhui(self):
        return datetime.now(pytz.timezone(FUSEAU)).date()

    @api.model
    def _chantrea_recuperer_taux(self, company):
        """Récupère les taux publiés, enregistre ceux qui manquent, alerte si besoin.

        Jamais de taux inventé : en cas d'échec, rien n'est enregistré et le
        dernier taux réellement publié reste celui qui s'applique (Odoo prend
        toujours le dernier taux connu à la date de la facture).
        """
        _ = self.env._
        khr = self.env.ref("base.KHR")
        source = company.chantrea_taux_source or "gdt"
        nom_source = dict(company._fields["chantrea_taux_source"]._description_selection(self.env))[source]
        aujourd_hui = self._chantrea_aujourdhui()
        problemes, crees = [], self.browse()

        try:
            publies = taux_officiel.telecharger(source)
        except taux_officiel.ErreurTaux as erreur:
            publies = {}
            problemes.append(_("Could not read the rate from %(origine)s: %(error)s",
                               origine=nom_source, error=str(erreur)))

        for jour in sorted(publies):
            valeur = publies[jour]
            if jour > aujourd_hui:
                problemes.append(_("%(origine)s shows a rate (%(rate)s) dated %(date)s, which is in the future: ignored.",
                                   origine=nom_source, rate=valeur, date=jour))
                continue
            if jour < aujourd_hui - timedelta(days=JOURS_RATTRAPAGE):
                continue
            existant = self._chantrea_taux_a_la_date(jour, company)
            if existant and existant.name == jour:
                continue  # déjà enregistré (ou saisi à la main) : on n'écrase jamais
            precedent = existant._chantrea_valeur(company) if existant else None
            erreur = taux_officiel.verifier(valeur, precedent)
            if erreur:
                problemes.append(_("Rate of %(date)s rejected: %(error)s", date=jour, error=erreur))
                continue
            crees |= self.create({
                "currency_id": khr.id,
                "name": jour,
                "rate": valeur,
                "company_id": company.root_id.id,
                "chantrea_source": source,
                "chantrea_releve_le": fields.Datetime.now(),
            })

        en_vigueur = self._chantrea_taux_a_la_date(aujourd_hui, company)
        # Pas de publication le week-end : on n'alerte que les jours ouvrés.
        if aujourd_hui.weekday() < 5 and en_vigueur.name != aujourd_hui:
            if en_vigueur:
                problemes.append(_(
                    "No rate for today (%(today)s). The last published rate stays in force: "
                    "%(rate)s KHR for 1 USD, dated %(date)s.",
                    today=aujourd_hui, rate=en_vigueur._chantrea_valeur(company), date=en_vigueur.name))
            else:
                problemes.append(_(
                    "No USD/KHR rate is recorded at all: customer invoices cannot be confirmed "
                    "until a rate is entered manually."))

        if problemes:
            self._chantrea_alerter(company, problemes)
        _logger.info("Taux USD/KHR (%s) : %d enregistré(s), %d problème(s)", source, len(crees), len(problemes))
        return {
            "crees": crees,
            "problemes": problemes,
            "taux_en_vigueur": en_vigueur._chantrea_valeur(company) if en_vigueur else None,
            "date_en_vigueur": en_vigueur.name if en_vigueur else None,
        }

    @api.model
    def _chantrea_alerter(self, company, problemes):
        destinataire = company.chantrea_taux_alerte_user_id or self.env.ref("base.user_admin")
        env = self.with_context(lang=destinataire.lang).env
        _logger.warning("Alerte taux USD/KHR : %s", " | ".join(problemes))
        if not destinataire.email:
            _logger.error("Alerte taux USD/KHR : %s n'a pas d'adresse e-mail.", destinataire.login)
            return
        corps = Markup("<p>%s</p><ul>%s</ul><p>%s</p>") % (
            env._("The daily USD/KHR exchange rate task needs your attention:"),
            Markup("").join(Markup("<li>%s</li>") % escape(p) for p in problemes),
            env._("To enter a rate manually: Invoicing › Configuration › USD/KHR rates."),
        )
        env["mail.mail"].sudo().create({
            "subject": env._("[Odoo] USD/KHR exchange rate: action needed"),
            "email_to": destinataire.email,
            "body_html": corps,
            "auto_delete": False,
        })
        env.ref("mail.ir_cron_mail_scheduler_action")._trigger()
