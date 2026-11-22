{
    "name": "Chantrea Systems – Espace client",
    "summary": "Assistance (tickets) et espace client de Chantrea Systems",
    "version": "19.0.1.0.0",
    "category": "Website",
    "author": "Chantrea Systems",
    # AGPL-3 : ce module dépend de modules OCA sous AGPL-3.
    "license": "AGPL-3",
    "depends": [
        "chantrea_base",
        "chantrea_kh_facture",
        "chantrea_parc",
        "portal",
        "helpdesk_mgmt",
        "helpdesk_mgmt_timesheet",
        "sale_management",
        "account",
        "contract",
        "fieldservice_portal",
        "fieldservice_stock",
        "sign_oca",
    ],
    "data": [
        "security/chantrea_groupes.xml",
        "security/regles_portail.xml",
        "data/assistance.xml",
        "data/mail_template.xml",
        "data/contrats.xml",
        "views/helpdesk_portail.xml",
        "views/mise_en_page.xml",
        "views/accueil.xml",
    ],
    "assets": {
        "web._assets_frontend_helpers": [
            ("prepend", "chantrea_portail/static/src/scss/variables_portail.scss"),
        ],
        "web.assets_frontend": [
            "chantrea_portail/static/src/scss/espace_client.scss",
            # Script OCA incompatible avec Odoo 19 (il importe « @portal/js/portal »,
            # qui n'existe plus) : erreur dans le navigateur sur chaque page de
            # l'espace client. Voir docs/CORRECTIFS_OCA.md.
            ("remove", "fieldservice_portal/static/src/js/fsm_order_portal.esm.js"),
        ],
        "portal.assets_chatter_style": [
            "chantrea_portail/static/src/scss/messagerie.scss",
        ],
    },
    "installable": True,
}
