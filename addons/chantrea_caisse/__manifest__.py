{
    "name": "Chantrea Systems – Caisse en dollars et en riels",
    "summary": "Point de vente en USD qui accepte les riels, rendu de monnaie en $ et ៛, KHQR",
    "version": "19.0.1.0.0",
    "category": "Sales/Point of Sale",
    "author": "Chantrea Systems",
    "license": "LGPL-3",
    "depends": ["chantrea_base", "chantrea_kh_facture", "point_of_sale", "l10n_kh"],
    "data": [
        "views/pos_config_views.xml",
        "views/pos_payment_method_views.xml",
        "views/pos_order_views.xml",
    ],
    "assets": {
        "point_of_sale._assets_pos": [
            "chantrea_caisse/static/src/js/**/*",
            "chantrea_caisse/static/src/xml/**/*",
            "chantrea_caisse/static/src/scss/**/*",
        ],
    },
    "installable": True,
}
