# Modules installés

Vérifié le 22/11/2026 avec `scripts/verifier_modules.sh` : tous à l'état *installed*.

## Images Docker (épinglées par empreinte)

| Image | Empreinte |
|---|---|
| odoo:19.0 (build 19.0-20261112) | `sha256:03a47921f9eef2c225ded1167fe7828465d2b3177883f30d173bb1c3c792949b` |
| postgres:17 | `sha256:223efeb196329b55b3b9a13db144956411dbc18e727e59f681c3e0aede6475cf` |
| caddy:2 | `sha256:4851e54a46b206517c574821bb5cc67f170d2156041e9fbc4c9193b45e84a75b` |
| axllent/mailpit (local seulement) | `sha256:23a2ef85bc50853ab3093645d1d64679afd8887e89da5e48a88940c172591a4e` |

## Dépôts OCA (sous-modules git, branche 19.0)

| Dépôt | Commit épinglé | Date du commit |
|---|---|---|
| OCA/helpdesk | `77d935ebda4a51e9eb3e00d8805f975725a09919` | 17/11/2026 |
| OCA/contract | `d553a35d86a4408f357f37039b987fcc9e3b2b2e` | 21/11/2026 |
| OCA/field-service | `99a7b92e1343d5aef033f3a0da3e438eb548f0a9` | 17/11/2026 |
| OCA/timesheet | `df7c987cdd9e3ba5360c60ca7cec93e5c93d4b47` | 18/11/2026 |
| OCA/sign | `6080baa8c9c94920c0658ba9867c27f5e1037316` | 11/11/2026 |

## Modules demandés

| Module | Origine | Licence | Version |
|---|---|---|---|
| contacts | Odoo | LGPL-3 | 19.0.1.0 |
| crm | Odoo | LGPL-3 | 19.0.1.9 |
| sale_management (Ventes) | Odoo | LGPL-3 | 19.0.1.0 |
| account (Facturation) | Odoo | LGPL-3 | 19.0.1.5 |
| l10n_kh | Odoo | LGPL-3 | 19.0.1.0 |
| project | Odoo | LGPL-3 | 19.0.1.4 |
| hr_timesheet (Feuilles de temps) | Odoo | LGPL-3 | 19.0.1.0 |
| purchase | Odoo | LGPL-3 | 19.0.1.2 |
| stock (Inventaire) | Odoo | LGPL-3 | 19.0.1.1 |
| portal | Odoo | LGPL-3 | 19.0.1.0 |
| helpdesk_mgmt | OCA/helpdesk | AGPL-3 | 19.0.1.4.0 |
| helpdesk_mgmt_timesheet | OCA/helpdesk | AGPL-3 | 19.0.1.0.0 |
| helpdesk_mgmt_sale | OCA/helpdesk | AGPL-3 | 19.0.1.0.0 |
| helpdesk_mgmt_fieldservice | OCA/helpdesk | AGPL-3 | 19.0.1.0.0 |
| contract | OCA/contract | AGPL-3 | 19.0.1.7.0 |
| contract_sale | OCA/contract | AGPL-3 | 19.0.1.0.0 |
| fieldservice | OCA/field-service | AGPL-3 | 19.0.1.3.0 |
| fieldservice_portal | OCA/field-service | AGPL-3 | 19.0.1.0.0 |
| fieldservice_sign | OCA/field-service | AGPL-3 | 19.0.1.0.0 |
| fieldservice_account | OCA/field-service | AGPL-3 | 19.0.1.0.0 |
| fieldservice_stock | OCA/field-service | AGPL-3 | 19.0.1.0.0 |

## Dépendances OCA installées automatiquement

| Module | Origine | Licence | Requis par |
|---|---|---|---|
| base_territory | OCA/field-service | AGPL-3 | fieldservice |
| helpdesk_mgmt_project | OCA/helpdesk | AGPL-3 | helpdesk_mgmt_timesheet |
| hr_timesheet_time_control | OCA/timesheet | AGPL-3 | helpdesk_mgmt_timesheet |
| sign_oca | OCA/sign | AGPL-3 | fieldservice_sign |
| helpdesk_mgmt_sale_project | OCA/helpdesk | AGPL-3 | installation automatique (helpdesk_mgmt_sale + helpdesk_mgmt_project) |
| helpdesk_product | OCA/helpdesk | AGPL-3 | helpdesk_mgmt_sale |

## Modules maison

| Module | Licence | Étape | État |
|---|---|---|---|
| chantrea_base | LGPL-3 | 2 | installé, testé |
| chantrea_kh_facture | LGPL-3 | 2 | installé, testé |
| chantrea_parc | AGPL-3 (dépend de fieldservice) | 5 et 6 | parc et interventions signées installés, testés |
| chantrea_portail | AGPL-3 (dépend de modules OCA) | 3, 4 et 7 | assistance, règles d'accès client, contrats installés et testés ; page d'accueil à l'étape 7 |
