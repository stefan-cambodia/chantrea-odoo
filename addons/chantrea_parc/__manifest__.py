{
    "name": "Chantrea Systems – Parc matériel",
    "summary": "Parc matériel des clients : fiches, garanties, liens tickets et interventions, vue client",
    "version": "19.0.1.0.0",
    "category": "Services/Field Service",
    "author": "Chantrea Systems",
    # AGPL-3 : ce module étend des modules OCA sous AGPL-3 (fieldservice).
    "license": "AGPL-3",
    "depends": [
        "chantrea_base",
        "fieldservice",
        "helpdesk_mgmt_fieldservice",
        "contract",
        "portal",
        "mail",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/regles.xml",
        "data/garantie.xml",
        "views/fsm_equipment_views.xml",
        "views/helpdesk_ticket_views.xml",
        "views/portail_templates.xml",
    ],
    "installable": True,
}
