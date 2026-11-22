# chantrea-odoo

Application de gestion et espace client de **Chantrea Systems** (services informatiques, Kampot, Cambodge).
Odoo 19.0 Community, auto-hébergé avec Docker. Interface interne en français ; espace client en khmer, anglais et français.

- Liste des modules, licences et versions épinglées : [docs/MODULES.md](docs/MODULES.md)
- Installation sur un serveur : `docs/DEPLOIEMENT.md` (étape 8)

## Organisation du dépôt

| Dossier | Contenu |
|---|---|
| `docker/` | Image Odoo (polices khmères), génération de `odoo.conf`, Caddyfile |
| `oca/` | Dépôts OCA en sous-modules git, épinglés à un commit — **jamais modifiés** |
| `addons/` | Modules maison `chantrea_*` |
| `scripts/` | Installation locale, mise à jour, vérification (sauvegarde/restauration à l'étape 8) |
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

Faire une sauvegarde avant toute mise à jour sur le serveur.

## Tests automatiques

```bash
scripts/tests.sh            # base de test neuve « chantrea_test » (installation complète, ~5 min)
scripts/tests.sh --rapide   # réutilise la base de test (mise à jour des modules maison seulement)
```

Les tests tournent dans une base séparée, jamais dans la base de travail.

## Factures cambodgiennes et taux USD/KHR

- Devis et factures sont imprimés en khmer, l'anglais juste en dessous, avec le total en USD
  **et** en KHR. Le taux, sa date et sa source sont imprimés et mémorisés sur la facture
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

- Les clients ouvrent et suivent leurs tickets dans l'espace client (`/my/tickets`, bouton
  « Nouveau ») ; la catégorie est obligatoire. Les tickets vont à l'équipe
  « Assistance Chantrea Systems », dont le temps passé est suivi dans le projet « Assistance ».
- Accusé de réception envoyé au client à la création du ticket, dans sa langue (khmer,
  anglais ou français), signé par la société.
- Accès d'un client : fiche du contact › Action › « Accorder l'accès au portail ».
  Un client voit les tickets, devis et factures de **sa** société, jamais ceux d'un autre client
  (tests `chantrea_portail/tests/`). Pages publiques (connexion) en anglais ; après connexion,
  la langue du compte du client.
- En local, `scripts/donnees_demo.sh` crée deux accès clients de démonstration
  (`dara@demo.example` en khmer, `sophea@demo.example` en anglais) ; mot de passe :
  `DEMO_CLIENT_PASSWORD` dans `.env`.
- Défauts trouvés dans les modules OCA et corrigés par héritage : [docs/CORRECTIFS_OCA.md](docs/CORRECTIFS_OCA.md).

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

## Relecture du khmer

Tous les textes khmers visibles par les clients sont listés dans
[docs/RELECTURE_KM.md](docs/RELECTURE_KM.md), à faire relire par un locuteur natif.
Après correction, noter le texte comme relu dans `docs/relecture-km-statut.json` puis :

```bash
python3 scripts/relecture_km.py
```

## Sauvegarder / restaurer

À venir (étape 8) : `scripts/sauvegarde.sh` et `scripts/restauration.sh`.
