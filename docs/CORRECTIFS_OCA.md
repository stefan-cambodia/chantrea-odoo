# Défauts trouvés dans les modules OCA et corrigés ici

Le code OCA n'est jamais modifié (sous-modules en lecture seule) : chaque défaut est
corrigé par héritage dans un module maison, avec un test automatique.
Ces défauts pourraient être signalés à l'OCA ; ce n'est pas fait (à décider).

| Module OCA (commit épinglé) | Défaut | Conséquence | Correctif | Test |
|---|---|---|---|---|
| helpdesk_mgmt (`77d935eb`) | La route `/ticket/close` lit le ticket en sudo d'après le seul `ticket_id` envoyé par le navigateur, sans vérifier qu'il appartient au client connecté. | Un client connecté peut fermer le ticket d'un autre client. | `chantrea_portail/controllers/helpdesk.py` : ticket lu avec les droits du client, sinon 404. | `test_fermeture_du_ticket_d_un_autre_refusee` |
| helpdesk_mgmt (`77d935eb`) | La même route accepte une requête GET (formulaire en `method="GET"`), donc sans protection CSRF. | Un simple lien piégé ferme un ticket à l'insu du client. | Route en POST uniquement, formulaire en POST avec jeton CSRF (`views/helpdesk_portail.xml`). | `test_fermeture_par_lien_get_refusee` |
| helpdesk_mgmt (`77d935eb`) | Sur la page d'un ticket, un attribut `id` sur `<t t-call="portal.portal_record_sidebar">` empêche Odoo 19 de transmettre `title` et `entries`. | Le client ne voit ni le numéro du ticket ni les boutons de fermeture. | Attribut retiré par héritage de la vue. | `test_fermeture_de_son_propre_ticket` (le jeton n'existe que si les boutons s'affichent) |
| helpdesk_mgmt (`77d935eb`) | La catégorie « obligatoire » n'est vérifiée que dans le navigateur ; le serveur accepte aussi une catégorie masquée. | Tickets sans catégorie, ou dans une catégorie interne. | Contrôle côté serveur dans `submit_ticket`. | `test_categorie_controlee_par_le_serveur` |
| helpdesk_mgmt (`77d935eb`) | Le modèle de courriel d'une étape n'est envoyé qu'au changement d'étape, pas à la création. | Pas d'accusé de réception. | Accusé de réception propre à Chantrea, envoyé à la création (`models/helpdesk_ticket.py`). | `test_accuse_de_reception_dans_la_langue_du_client` |
| contract (`d553a35d`) | `contract.line` est lisible par le Portail sans aucune règle propre au Portail. | Un client connecté lit, par l'API JSON d'Odoo, les lignes (produits, prix, nom du contrat) des contrats de **tous** les clients. | Règle Portail limitée aux contrats du client (`chantrea_portail/security/regles_portail.xml`). | `test_lignes_de_contrat`, `test_api_json_ne_livre_rien_d_un_autre_client` |
| contract (`d553a35d`) | `contract.modification` : même défaut, aucune règle. | Un client lit les modifications des contrats des autres clients. | Même règle. | `test_modifications_de_contrat` |
| fieldservice_stock (`99a7b92e`) | Le Portail reçoit la lecture **et l'écriture** sur `stock.move`, sans règle Portail. | Un client connecté peut lire et modifier tous les mouvements de stock (quantités). | Lecture limitée aux mouvements des interventions du client ; aucune écriture. | `test_mouvements_de_stock` |
| contract (`d553a35d`) | Un contrat n'est visible dans l'espace client que si le contact y est abonné. | Les collègues du client ne voient pas les contrats de leur société. | Règle Portail ajoutée : contrats de la société du client. | `test_contrat_visible_par_la_societe_sans_abonnement` |
| sign_oca (`6080baa8`) | La route `/my/sign/<id>/download` lit la demande en sudo d'après le seul numéro et renvoie un lien vers le document signé, sans vérifier qui le demande. | Un client connecté télécharge les documents signés de tous les autres en essayant les numéros. | Document servi seulement à un signataire (ou sa société) ou à un interne autorisé (`chantrea_portail/controllers/signature.py`). | `test_autre_client_refuse` |
| fieldservice_sign (`99a7b92e`) | Les boutons « Signer » n'apparaissent que si l'étape en cours demande une signature ; seule l'étape « Terminé » le fait, alors que « signature obligatoire » l'exige AVANT de terminer. | Impossible de faire signer puis de terminer une intervention. | Signature possible dès l'étape « Nouveau » (`chantrea_parc/data/interventions.xml`). | `test_terminer_exige_la_signature` |
| fieldservice (`99a7b92e`) | Les instructions au technicien (`todo`) sont lisibles par le client via l'API. | Fuite d'instructions internes. | Champ réservé aux utilisateurs internes. | `test_instructions_illisibles_par_le_client` |
| fieldservice_portal (`99a7b92e`) | Son script `fsm_order_portal.esm.js` importe `@portal/js/portal`, qui n'existe plus dans Odoo 19. | Une erreur JavaScript sur **chaque** page de l'espace client. | Script retiré du lot de scripts de l'espace client (`chantrea_portail/__manifest__.py`). | `test_script_oca_incompatible_retire` |

## Défauts d'Odoo 19 sans le module « website »

Le module `website` n'est pas installé (il n'est pas demandé). Sans lui, deux réglages
qu'il apporte manquent à l'espace client ; ils sont rétablis par héritage.

| Défaut | Conséquence | Correctif | Test |
|---|---|---|---|
| La balise `<html>` des pages client n'a pas d'attribut `lang` : le navigateur demande les traductions JavaScript sans préciser de langue. | Fenêtre de signature d'un devis, messages d'erreur, boutons affichés par JavaScript : en anglais dans **toutes** les langues, français compris. | Attribut `lang` ajouté (`chantrea_portail/views/mise_en_page.xml`). | `test_traductions_javascript_demandees_dans_la_langue_de_la_page` |
| Les traductions JavaScript du module `mail` ne sont envoyées à l'espace client que par `website_mail`. | La messagerie d'un ticket, d'un devis ou d'une facture (« Write a message… », « Send ») reste en anglais. | `mail`, `auth_totp_portal`, `auth_passkey_portal` et `account_payment` ajoutés aux modules traduits côté client (`chantrea_portail/models/ir_http.py`). | même test |

## Comportements d'Odoo pris en compte (pas des défauts)

- La langue des pages client suit d'abord le cookie `frontend_lang`, posé dès la page de
  connexion : à la connexion, `chantrea_portail` l'aligne sur la langue du compte du client.
- Odoo sert la langue par défaut aux robots (dont `curl`) : pour tester une langue à la
  main, utiliser un navigateur ou l'adresse préfixée (`/km/my`, `/fr/my`).
