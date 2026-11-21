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
(Cambodge, USD, riel actif), installe tous les modules et affiche leur état.
Il refuse de tourner si la base existe déjà.

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

## Sauvegarder / restaurer

À venir (étape 8) : `scripts/sauvegarde.sh` et `scripts/restauration.sh`.
