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
| helpdesk_mgmt (`77d935eb`) | Le canal « Courriel » d'un ticket reçu par courriel est déduit du contexte `fetchmail_cron_running`, qu'Odoo 19 ne transmet plus à la création du ticket. | Le canal reste vide : on ne distingue plus les tickets reçus par courriel. | Canal fixé dans `message_new`, appelé seulement pour un courriel reçu (`models/helpdesk_ticket.py`). | `test_courriel_d_un_client_connu` |

## Défauts d'Odoo 19 sans le module « website »

Le module `website` n'est pas installé (il n'est pas demandé). Sans lui, trois réglages
qu'il apporte manquent à l'espace client ; ils sont rétablis par héritage.

| Défaut | Conséquence | Correctif | Test |
|---|---|---|---|
| La balise `<html>` des pages client n'a pas d'attribut `lang` : le navigateur demande les traductions JavaScript sans préciser de langue. | Fenêtre de signature d'un devis, messages d'erreur, boutons affichés par JavaScript : en anglais dans **toutes** les langues, français compris. | Attribut `lang` ajouté (`chantrea_portail/views/mise_en_page.xml`). | `test_traductions_javascript_demandees_dans_la_langue_de_la_page` |
| La page de connexion `/web/login` n'est pas servie comme une page de l'espace client. | Elle est toujours en anglais, même à l'adresse `/km/web/login` ou pour un client déjà venu ; un mot de passe erroné ramène aussi à l'anglais. | Mêmes réglages de route que le module `website` (`website=True`, `auth="public"`) dans `chantrea_portail/controllers/connexion.py`. | `test_page_de_connexion_dans_la_langue_de_l_adresse`, `test_mot_de_passe_errone_reste_dans_la_langue_du_client` |
| Les traductions JavaScript du module `mail` ne sont envoyées à l'espace client que par `website_mail`. | La messagerie d'un ticket, d'un devis ou d'une facture (« Write a message… », « Send ») reste en anglais. | `mail`, `auth_totp_portal`, `auth_passkey_portal` et `account_payment` ajoutés aux modules traduits côté client (`chantrea_portail/models/ir_http.py`). | même test |

## Défauts du QR code KHQR d'Odoo 19 (`l10n_kh`)

Comparés aux règles du SDK officiel de la Banque nationale du Cambodge (`bakong-khqr`,
version 1.0.20 : longueurs maximales, format du montant, champs obligatoires).
Corrigés par héritage dans `chantrea_base/models/res_partner_bank.py`, pour les comptes cambodgiens seulement.

| Défaut | Conséquence | Correctif | Test |
|---|---|---|---|
| Le montant est écrit tel que Python l'affiche : `12.5`, ou `0.30000000000000004` pour un montant calculé. | Un montant de plus de 13 caractères ou à plus de 2 décimales est refusé par les applications bancaires. | Riels : nombre entier ; dollars : deux décimales s'il y en a (`12.50`). | `test_qr_en_dollars`, `test_montant_calcule_en_virgule_flottante` |
| Un QR code sans montant (QR de secours de la caisse) est marqué « dynamique » (12). | Le SDK refuse un QR dynamique sans montant. | « Statique » (11), sans horodatage. | `test_qr_sans_montant_statique` |
| La référence (numéro de facture) n'est pas limitée. | Au-delà de 25 caractères, le QR est refusé. | Coupée à 25 caractères. | `test_reference_limitee_a_25_caracteres` |
| À la caisse, la référence est le nom de la commande, qui vaut « / » tant qu'elle n'est pas enregistrée. | Référence inutilisable sur le relevé bancaire. | Numéro du ticket (`chantrea_caisse/static/src/js/caisse.js`). | vérifié dans un navigateur (QR décodé) |

## Comportements d'Odoo pris en compte (pas des défauts)

- Sans réglage, Odoo met en expéditeur d'un courriel l'adresse personnelle de son auteur
  (invitation d'un client, réponse à un ticket, envoi d'un devis) : un service d'envoi refuse en
  général ces courriels. `docker/entrypoint-chantrea.sh` règle `from_filter` sur `EMAIL_FROM` :
  tout part de cette adresse, le nom de l'auteur est conservé et les réponses lui reviennent.
- Créer un domaine d'alias (réception des courriels) change l'expéditeur en `notifications@…` :
  `chantrea_base` propose `EMAIL_FROM` à la place (`test_expediteur_du_domaine_d_alias`).
- Quand on impose l'auteur d'un message publié avec un modèle de courriel, Odoo ne reprend plus
  l'expéditeur du modèle : l'accusé de réception d'un ticket le donne lui-même, avec le nom de la
  société (`test_expediteur_de_l_accuse_de_reception`).

- La langue des pages client suit d'abord le cookie `frontend_lang`, posé dès la page de
  connexion : à la connexion, `chantrea_portail` l'aligne sur la langue du compte du client.
- Le plan comptable crée ses taxes après l'installation des modules : `chantrea_portail` remet ses
  traductions à ce moment-là (`test_plan_comptable_traduit_apres_son_chargement`).
- Odoo sert la langue par défaut aux robots (dont `curl`) : pour tester une langue à la
  main, utiliser un navigateur ou l'adresse préfixée (`/km/my`, `/fr/my`).
