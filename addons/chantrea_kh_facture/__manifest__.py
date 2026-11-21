{
    "name": "Chantrea Systems – Factures cambodgiennes",
    "summary": "Devis et factures khmer/anglais, total USD et KHR, taux officiel GDT/BNC",
    "version": "19.0.1.0.0",
    "category": "Accounting/Localizations",
    "author": "Chantrea Systems",
    "license": "LGPL-3",
    "depends": ["chantrea_base", "account", "sale_management", "mail"],
    "external_dependencies": {"python": ["requests"]},
    "data": [
        "data/ir_cron.xml",
        "views/res_currency_rate_views.xml",
        "views/res_config_settings_views.xml",
        "views/account_move_views.xml",
        "report/format_papier.xml",
        "report/libelles.xml",
        "report/facture_kh.xml",
        "report/devis_kh.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "chantrea_kh_facture/static/src/scss/documents_kh.scss",
        ],
    },
    "installable": True,
}
