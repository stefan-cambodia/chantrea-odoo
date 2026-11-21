import base64
import logging

from odoo.tools import file_open

_logger = logging.getLogger(__name__)

LANGUES = ("fr_FR", "en_US", "km_KH")


def configurer_societe(env):
    """Réglages de la société, appliqués à l'installation du module.

    Société en cours d'immatriculation : numéro d'enregistrement et numéro de
    TVA restent vides. Aucune donnée réelle n'est écrite ici.
    """
    company = env.ref("base.main_company")
    khr = env.ref("base.KHR")

    company.write({
        "name": "Chantrea Systems",
        "city": "Kampot",
        "country_id": env.ref("base.kh").id,
        "vat": False,
        "company_registry": False,
        # Couleurs de la charte du site (vert et or).
        "primary_color": "#1f6b3c",
        "secondary_color": "#d9a441",
    })
    # Logo « pingouin dans le croissant » du site chantrea (version claire).
    with file_open("chantrea_base/static/img/logo_chantrea.png", "rb") as logo:
        company.logo = base64.b64encode(logo.read())

    # Le riel reste actif, sans décimales (pas de sous-unité en pratique).
    khr.write({"active": True, "rounding": 1.0})

    apres_plan_comptable(env, company)


def apres_plan_comptable(env, company):
    """Réglages qui dépendent du plan comptable.

    Appelée à l'installation du module ET juste après le chargement du plan
    comptable cambodgien (voir models/account_chart_template.py) : selon l'ordre
    d'installation, Odoo charge le plan après nos hooks et impose alors la
    devise du pays (KHR). Tout n'est modifiable que tant qu'aucune écriture
    comptable n'existe.
    """
    usd, khr = env.ref("base.USD"), env.ref("base.KHR")
    ecritures = env["account.move.line"].search_count([("company_id", "=", company.id)], limit=1)

    # Devise principale USD.
    if company.currency_id != usd:
        if ecritures:
            _logger.error(
                "chantrea_base : la devise de la société est %s et des écritures existent ; "
                "passage en USD impossible.", company.currency_id.name)
        else:
            company.currency_id = usd
    khr.active = True

    # Listes de prix créées en KHR : passage en USD tant qu'aucune commande ne les utilise.
    for liste in env["product.pricelist"].with_context(active_test=False).search(
            [("currency_id", "=", khr.id), ("company_id", "in", [False, company.id])]):
        if not env["sale.order"].search_count([("pricelist_id", "=", liste.id)], limit=1):
            liste.currency_id = usd

    # Journal des ventes : code « INV » (préfixe des numéros de facture),
    # seulement s'il n'a encore servi à rien.
    journal = env["account.journal"].search(
        [("company_id", "=", company.id), ("type", "=", "sale")], limit=1)
    if journal and journal.code != "INV" and not env["account.move"].search_count(
            [("journal_id", "=", journal.id)], limit=1):
        journal.write({"code": "INV", "name": "Factures clients"})


def activer_langues(env):
    langs = env["res.lang"].with_context(active_test=False).search([("code", "in", LANGUES)])
    env["base.language.install"].create({
        "lang_ids": [(6, 0, langs.ids)],
        "overwrite": False,
    }).lang_install()


def post_init_hook(env):
    configurer_societe(env)
    activer_langues(env)
    # Interface interne en français pour l'administrateur.
    env.ref("base.user_admin").write({"lang": "fr_FR", "tz": "Asia/Phnom_Penh"})
