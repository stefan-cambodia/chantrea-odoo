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

## Comportements d'Odoo pris en compte (pas des défauts)

- La langue des pages client suit d'abord le cookie `frontend_lang`, posé dès la page de
  connexion : à la connexion, `chantrea_portail` l'aligne sur la langue du compte du client.
- Odoo sert la langue par défaut aux robots (dont `curl`) : pour tester une langue à la
  main, utiliser un navigateur ou l'adresse préfixée (`/km/my`, `/fr/my`).
