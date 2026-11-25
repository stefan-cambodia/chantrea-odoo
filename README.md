# chantrea-odoo

Application de gestion et espace client de **Chantrea Systems** (services informatiques, Kampot, Cambodge).
Odoo 19.0 Community, auto-hébergé avec Docker. Interface interne en français ; espace client en khmer, anglais et français.

- Liste des modules, licences et versions épinglées : [docs/MODULES.md](docs/MODULES.md)
- Installation sur un serveur, sauvegardes et restauration : [docs/DEPLOIEMENT.md](docs/DEPLOIEMENT.md)

## Organisation du dépôt

| Dossier | Contenu |
|---|---|
| `docker/` | Image Odoo (polices khmères), génération de `odoo.conf`, Caddyfile |
| `oca/` | Dépôts OCA en sous-modules git, épinglés à un commit — **jamais modifiés** |
| `addons/` | Modules maison `chantrea_*` |
| `scripts/` | Installation (locale ou serveur), mise à jour, vérification, sauvegarde et restauration |
| `deploiement/` | Tâches planifiées du serveur (sauvegarde chaque nuit, essai de restauration chaque semaine) |
| `docs/` | Documentation |

## Installer en local

Prérequis : Docker avec Docker Compose, git.

```bash
git clone --recurse-submodules git@github.com:stefan-cambodia/chantrea-odoo.git
cd chantrea-odoo
cp .env.example .env
# Remplir dans .env : POSTGRES_PASSWORD, ODOO_ADMIN_PASSWD, ADMIN_LOCAL_PASSWORD
#   (générer avec : openssl rand -base64 32)
scripts/init_local.sh
```

Le script construit l'image, crée la base `chantrea` en français, règle la société
(Cambodge, USD, riel actif), installe tous les modules (dont les modules maison),
récupère le taux officiel USD/KHR et affiche l'état des modules.
Il refuse de tourner si la base existe déjà.

Données de démonstration (poste local uniquement, refusé si `DOMAINE` n'est pas `localhost`) :

```bash
scripts/donnees_demo.sh     # clients, produits, 2 factures et 1 devis « DÉMO » + PDF dans demo-pdf/
```

- Odoo : <https://localhost:8443> (identifiant `admin`, mot de passe `ADMIN_LOCAL_PASSWORD`).
  Le certificat local est émis par Caddy : le navigateur affiche un avertissement la première fois.
- Double authentification obligatoire pour les utilisateurs internes : à la connexion,
  le code est envoyé par courriel. En local, il arrive dans **Mailpit** : <http://localhost:8025>.

Commandes utiles :

```bash
docker compose ps                 # état des services
docker compose logs -f odoo       # journal d'Odoo
docker compose stop / start       # arrêter / relancer
scripts/verifier_modules.sh       # état et licence des modules
```

## Ajouter un module

1. **Module maison** : créer `addons/chantrea_xxx/` (avec `__manifest__.py`), puis :
   `scripts/mettre_a_jour.sh base` (rafraîchit la liste des modules) et l'installer :
   `docker compose run --rm odoo odoo -d chantrea -i chantrea_xxx --stop-after-init`.
2. **Module OCA d'un dépôt déjà présent** : l'ajouter à `scripts/modules.txt` et l'installer de la même façon.
3. **Nouveau dépôt OCA** : `git submodule add -b 19.0 https://github.com/OCA/<depot>.git oca/<depot>`,
   ajouter `oca/<depot>` à `addons_path` dans `docker/entrypoint-chantrea.sh`, noter le commit dans `docs/MODULES.md`.

On ne modifie jamais le code d'Odoo ni celui des modules OCA : on en hérite dans un module maison.

## Mettre à jour

```bash
# Avancer un dépôt OCA à un nouveau commit (contrôlé) :
git -C oca/helpdesk fetch && git -C oca/helpdesk checkout <commit>
git add oca/helpdesk && git commit -m "OCA helpdesk : passage au commit <commit>"

# Appliquer dans la base (tous les modules, ou une liste) :
scripts/mettre_a_jour.sh
scripts/mettre_a_jour.sh chantrea_parc,chantrea_portail
```

Sur le serveur, faire une sauvegarde avant toute mise à jour : `scripts/sauvegarde.sh`.

## Tests automatiques

```bash
scripts/tests.sh            # base de test neuve « chantrea_test » (installation complète, ~6 min)
scripts/tests.sh --rapide   # réutilise la base de test (mise à jour des modules maison seulement)
```

Les tests tournent dans une base séparée, jamais dans la base de travail.

## Factures cambodgiennes et taux USD/KHR

- Devis et factures sont imprimés en khmer, l'anglais juste en dessous, avec le total en USD
  **et** en KHR. Les dates et les montants sont aussi écrits en chiffres khmers, au-dessus des
  chiffres habituels (« ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦ », « $ ៤៩៥.០០ », mêmes séparateurs que la ligne
  anglaise) ; de même pour les heures du rapport d'intervention. Les tableaux de lignes gardent
  les chiffres habituels. Fonctions : `chantrea_base/outils_km.py`, nommées `km` dans les rapports. Le taux, sa date et sa source sont imprimés et mémorisés sur la facture
  au moment de la validation ; ils ne changent plus ensuite.
- Deux variantes, une seule numérotation (`INV/000001`, sans remise à zéro annuelle ;
  avoirs : `RINV/000001`) : **facture de TVA** (numéro de TVA du client obligatoire) et
  **facture commerciale**. Le type est proposé selon le client et modifiable sur le brouillon.
- Taux officiel : une tâche planifiée le récupère chaque jour à 10 h (Phnom Penh) sur le site
  du GDT (ou de la Banque nationale, selon le réglage Facturation › Configuration › Paramètres).
  En cas d'échec, rien n'est inventé : le dernier taux publié reste en vigueur et une alerte
  est envoyée par courriel. Pas d'alerte le week-end (pas de publication).
- Saisie manuelle : Facturation › Configuration › Taux USD/KHR, ou sur la facture brouillon
  (onglet Cambodge). Sans aucun taux, une facture ne peut pas être validée.

## Assistance et espace client

- **Accueil de l'espace client** (`/my`, module `chantrea_portail`) : un tableau de bord aux
  couleurs de Chantrea Systems avec six cartes — demandes d'assistance ouvertes, interventions
  en cours, matériel (et garanties qui se terminent dans les 60 jours), contrats en cours, devis
  à examiner, factures à payer (et montant dû) — et un bouton « Demander de l'aide ».
  Chaque chiffre est calculé avec les droits du client connecté : il ne compte que les
  données de sa société. En dessous : commandes, adresses, connexion et sécurité.
  Les rubriques internes ou fournisseurs d'Odoo (projets, tâches, feuilles de temps, achats,
  signature à distance) ne sont pas proposées aux clients (`controllers/accueil.py`).
- Deux blocs standard d'Odoo sont masqués pour les clients (`views/blocs_masques.xml`) : le choix
  du mode d'envoi et du format électronique des factures sur « Mon compte » (FacturX, Peppol…,
  sans objet au Cambodge), et l'encart « Connect with your software! » de la page d'un devis.
- Les clients ouvrent et suivent leurs tickets dans l'espace client (`/my/tickets`, bouton
  « Nouveau ») ; la catégorie est obligatoire. Les tickets vont à l'équipe
  « Assistance Chantrea Systems », dont le temps passé est suivi dans le projet « Assistance ».
- Accusé de réception envoyé au client à la création du ticket, dans sa langue (khmer,
  anglais ou français), signé par la société.
- Tous les courriels d'Odoo partent de l'adresse `EMAIL_FROM` de `.env`, avec le nom de leur
  auteur ; les réponses reviennent à l'auteur. `scripts/essai_courriel.sh adresse` envoie deux
  courriels d'essai et contrôle cet expéditeur.
- Un ticket peut aussi être ouvert par courriel (facultatif, réglages dans
  [docs/DEPLOIEMENT.md](docs/DEPLOIEMENT.md), étape 6) : contact connu rattaché à son ticket,
  canal « Courriel », réponses rangées dans le ticket (`tests/test_tickets_par_courriel.py`).
  Une adresse inconnue est refusée et reçoit une réponse en khmer, anglais et français
  (`data/refus_inconnus.xml`) ; le réglage se change sur l'équipe, « Accepter les courriels de ».
- Accès d'un client : fiche du contact › Action › « Accorder l'accès au portail ».
  Un client voit les tickets, devis et factures de **sa** société, jamais ceux d'un autre client
  (tests `chantrea_portail/tests/`). La page de connexion est en anglais à la première visite ;
  elle existe en khmer et en français (`/km/web/login`, `/fr/web/login`) et un client déjà venu
  la retrouve dans sa langue. Après connexion, tout est dans la langue du compte du client.
- En local, `scripts/donnees_demo.sh` crée deux accès clients de démonstration
  (`dara@demo.example` en khmer, `sophea@demo.example` en anglais) ; mot de passe :
  `DEMO_CLIENT_PASSWORD` dans `.env`.
- Défauts trouvés dans les modules OCA (et dans Odoo 19 sans le module « website ») et corrigés par
  héritage : [docs/CORRECTIFS_OCA.md](docs/CORRECTIFS_OCA.md).

## Contrats de maintenance

- Créer un contrat : Facturation › Clients › Contrats › Nouveau, choisir le modèle
  « Monthly IT maintenance » (mensuel, facturé en début de période), puis fixer le prix
  de la ligne et la date de début. Le libellé de ligne est bilingue anglais / khmer ;
  `#START#` et `#END#` deviennent les dates de la période.
- Chaque jour, la tâche planifiée du module OCA crée les factures arrivées à échéance,
  **en brouillon**, avec une activité « Valider la facture mensuelle » pour le responsable
  du contrat. Valider la facture fixe le taux USD/KHR et marque l'activité comme faite.
- Échéance = date de facture, sauf conditions de paiement définies sur le contrat.
- Le client voit les contrats de sa société dans son espace (`/my/contracts`).

## Parc matériel des clients

- Interventions › Équipements (fiche « Field Service Equipment » complétée par `chantrea_parc`) :
  client, site, catégorie (serveur, switch, pare-feu, Wi-Fi, onduleur, stockage, poste, licence),
  marque, modèle, numéro de série, fournisseur, date d'achat, fin de garantie, contrat lié,
  responsable, notes internes. Boutons : tickets et interventions de l'équipement.
- **Aucun mot de passe, adresse IP ni identifiant d'accès dans Odoo** : un avertissement le
  rappelle sur la fiche, et Odoo refuse d'enregistrer une fiche qui semble en contenir
  (pour un numéro de version, écrire `v1.0.2.15`).
- Alertes internes 60 et 30 jours avant la fin de garantie : activité pour le responsable
  de la fiche (tâche planifiée chaque jour à 7 h).
- Le client voit le matériel de sa société dans son espace (`/my/equipments`), en lecture
  seule, sans les notes internes ni le fournisseur (illisibles aussi par l'API).
- Un ticket peut être relié aux équipements concernés (champ « Équipement » du ticket).

## Interventions sur site

- Depuis un ticket : bouton de création d'une intervention (elle reprend le site et les
  équipements du ticket). Interventions › Ordres de service sinon.
- Le technicien fait **signer le client sur place** (bouton « Signer », tablette ou téléphone) ;
  une intervention ne peut pas être terminée sans signature. La signature de documents à
  distance (`sign_oca`) est désactivée.
- Rapport d'intervention PDF bilingue khmer/anglais : demande, travaux réalisés, équipements,
  signature et heure (fuseau du site, Phnom Penh par défaut). Jamais les instructions internes.
- Le client suit ses interventions dans son espace (`/my/fsm_orders`) et télécharge le rapport.
- Les textes d'une intervention refusent aussi adresses IP, mots de passe et identifiants.

## Caisse en dollars et en riels, paiement KHQR

Module `chantrea_caisse` (Point de vente d'Odoo). La caisse vend en dollars et accepte les riels.

- **Taux de la caisse** : par défaut le taux officiel du jour, le même que sur les factures ;
  ou un taux fixe affiché en boutique (par exemple 4 000). Point de vente › Configuration ›
  Paramètres › « Riels à la caisse ». Sans taux disponible, la caisse le dit et n'accepte pas de riels.
- L'écran de paiement donne le total aussi en riels (arrondi aux 100 ៛ supérieurs), puis le reste
  à payer en riels.
- Bouton **« Espèces en dollars et en riels »** : la caissière saisit les billets reçus dans les
  deux monnaies (touches +1 $… +100 000 ៛). Monnaie à rendre : les dollars entiers en billets,
  les centimes en riels arrondis aux 100 ៛ (les pièces de dollar ne circulent pas) ; ou tout en
  riels, ou tout en dollars.
- Ticket : total en riels, taux, espèces reçues ($ + ៛), monnaie rendue ; ces lignes sont en khmer
  et en anglais quelle que soit la langue de la caissière.
- Comptabilité : un seul tiroir, compté en dollars par Odoo. Les riels reçus et rendus sont
  enregistrés sur chaque vente. À la clôture : riels reçus − rendus, dollars attendus, et deux
  cases « $ » et « ៛ » qui remplissent le comptage (compter exactement les billets attendus ne
  crée aucun écart). Le fond de caisse est compté avec les dollars.
- **KHQR** (Bakong, Banque nationale du Cambodge) : mode de paiement « Application bancaire (code QR) »
  sur un journal de banque dont le compte porte votre identifiant Bakong. Case « QR code en riels » :
  le QR demande des riels au taux de la caisse, sinon des dollars. Le client scanne avec
  l'application de sa banque ; la caissière confirme quand le paiement apparaît. La référence
  du QR est le numéro du ticket. Le même compte sert au QR code des factures.
  Réglage pas à pas : [docs/DEPLOIEMENT.md](docs/DEPLOIEMENT.md), étape 6 bis.
- Odoo 19 produit des QR codes KHQR que le SDK de la Banque nationale refuse dans certains cas ;
  corrigé dans `chantrea_base/models/res_partner_bank.py` (voir
  [docs/CORRECTIFS_OCA.md](docs/CORRECTIFS_OCA.md)).
- Calculs en riels de la caisse : `static/src/js/riels.js`, testés avec Node par `scripts/tests.sh`.
- Démonstration (poste local) : `scripts/donnees_demo.sh` crée « Boutique Kampot (DÉMO) », trois
  articles et deux modes KHQR avec un identifiant Bakong **fictif** (aucun paiement réel possible).

## Langues et traductions

L'interface interne est en français. L'espace client existe en khmer, en anglais et en
français : chaque client le voit dans la langue de sa fiche (champ « Langue » du contact).

| Où | Contenu |
|---|---|
| `addons/chantrea_*/i18n/fr.po`, `km.po` | Textes des modules maison (écrits en anglais dans le code) |
| `addons/chantrea_portail/i18n_clients/km.po` | Textes d'**Odoo et de l'OCA** vus par les clients, en khmer (Odoo 19 n'en traduit que 1 à 17 %, l'OCA aucun) |
| `addons/chantrea_portail/i18n_clients/km_pays.po` | Noms de pays en khmer, repris du référentiel Unicode CLDR |
| `addons/chantrea_portail/i18n_clients/fr.po` | Les quelques textes que l'OCA et Odoo n'ont pas traduits en français |

- Les fichiers `i18n_clients` sont chargés à chaque installation ou mise à jour de
  `chantrea_portail` : pages, champs, pays et courriels sont importés dans la base
  (`models/traductions_clients.py`) ; les textes écrits dans le code Python ou JavaScript
  d'Odoo et de l'OCA (tris et filtres des listes, fenêtre de signature, messagerie d'un
  ticket…) sont complétés au démarrage (`traductions_code.py`). Ni Odoo ni l'OCA ne sont modifiés.
- **Corriger une traduction** : modifier le `msgstr` dans le fichier, puis
  `scripts/mettre_a_jour.sh chantrea_portail` (ou le module concerné).
  Les fichiers `i18n_clients` font foi : pour les textes qu'ils contiennent, une traduction
  modifiée à la main dans Odoo est remplacée à la mise à jour suivante.
- **Ajouter un texte d'Odoo ou de l'OCA resté en anglais** : ajouter une entrée dans
  `i18n_clients/km.po` en recopiant le `msgid` et les lignes `#.` / `#:` du fichier
  `i18n/<module>.pot` du module d'origine, puis mettre à jour `chantrea_portail`.
- Restent en anglais pour un client khmer : les données saisies par l'équipe (noms de
  produits, descriptions, étapes ajoutées à la main), les pages de paiement en ligne (aucun
  prestataire de paiement n'est configuré) et les fonctions d'Odoo que les clients
  n'utilisent pas (clés d'API, discussion instantanée).

### Relecture du khmer

Tous les textes khmers visibles par les clients sont listés dans
[docs/RELECTURE_KM.md](docs/RELECTURE_KM.md), à faire relire par un locuteur natif, en trois
parties : documents imprimés et pages Chantrea, modules Chantrea, textes d'Odoo et de l'OCA.
Après correction, noter le texte comme relu dans `docs/relecture-km-statut.json` puis :

```bash
python3 scripts/relecture_km.py
```

## Sauvegarder / restaurer

Mode d'emploi complet, réglages et planification : [docs/DEPLOIEMENT.md](docs/DEPLOIEMENT.md), étapes 7 et 8.

```bash
scripts/sauvegarde.sh                           # base + fichiers → archive chiffrée → copie SFTP → ménage (30 jours)
scripts/restauration.sh --essai --depuis-sftp   # essai : restaure à côté, vérifie, supprime. Ne touche à rien.
scripts/restauration.sh --remplacer --depuis-sftp   # revenir à la dernière sauvegarde (confirmation demandée)
scripts/restauration.sh --help
```

- Une archive contient la base PostgreSQL, les fichiers d'Odoo (pièces jointes, PDF) et un manifeste.
  Elle est chiffrée (AES-256) avec `SAUVEGARDE_PHRASE` de `.env` : **gardez cette phrase hors du
  serveur**, sans elle aucune sauvegarde n'est lisible. `.env` n'est pas dans les archives.
- Après chaque sauvegarde, l'archive est relue et la copie distante vérifiée. Les archives de plus
  de `SAUVEGARDE_JOURS` jours (30) sont supprimées, sur la machine et sur le second stockage.
- Une restauration se fait toujours **à côté** de la base en service, puis est vérifiée (mêmes
  chiffres qu'au moment de la sauvegarde, chaque pièce jointe présente et intacte). La base en
  service n'est remplacée qu'ensuite, et l'ancienne est gardée sous un autre nom.
- Une sauvegarde venue d'un autre domaine (celle du serveur, ouverte sur votre poste) est
  neutralisée : pas d'envoi de courriels ni de tâches planifiées.
- En cas d'échec d'une sauvegarde ou d'un essai de restauration : courriel à `ALERTE_EMAIL`.

Essai complet sur le poste local, sans toucher à la base de travail ni à vos réglages
(serveur SFTP provisoire, environ une minute et demie) :

```bash
scripts/essai_sauvegarde.sh
```
