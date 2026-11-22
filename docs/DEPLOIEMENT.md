# Installer chantrea-odoo sur un serveur

Ce guide décrit, pas à pas, l'installation sur un serveur Linux loué (VPS), par exemple à
Singapour. Comptez une demi-journée. Rien n'est fait automatiquement depuis votre poste :
c'est vous qui lancez chaque commande sur le serveur.

Les commandes sont écrites pour **Ubuntu Server 24.04 LTS**. Elles conviennent aussi à
Debian 12 ou 13 (une seule différence, signalée à l'étape 2).

Ce qui a été essayé avant de vous livrer ce guide, et ce qui ne pouvait pas l'être, est
listé [à la fin](#ce-qui-a-été-essayé).

## Sommaire

1. [Ce qu'il vous faut](#1-ce-quil-vous-faut)
2. [Préparer le serveur](#2-préparer-le-serveur)
3. [Récupérer le code](#3-récupérer-le-code)
4. [Régler `.env`](#4-régler-env)
5. [Créer la base](#5-créer-la-base)
6. [Courriels](#6-courriels)
7. [Sauvegardes](#7-sauvegardes)
8. [Restaurer](#8-restaurer)
9. [Mettre à jour](#9-mettre-à-jour)
10. [Surveiller et dépanner](#10-surveiller-et-dépanner)
11. [Liste de contrôle avant la mise en service](#11-liste-de-contrôle-avant-la-mise-en-service)

## 1. Ce qu'il vous faut

| Quoi | Détail |
|---|---|
| Un serveur | 2 processeurs, 4 Go de mémoire, 40 Go de disque au minimum. Ubuntu Server 24.04 LTS. Une adresse IP fixe. |
| Un nom de domaine | Par exemple `erp.votre-domaine.com`, avec un enregistrement DNS de type **A** vers l'adresse IP du serveur (et **AAAA** si le serveur a une adresse IPv6). Le certificat HTTPS est obtenu automatiquement, à condition que ce nom pointe déjà vers le serveur. |
| Un service d'envoi de courriels (SMTP) | **Indispensable** : le code demandé à chaque connexion d'un utilisateur interne arrive par courriel. Il vous faut le nom du serveur SMTP, le port (587 en général), un identifiant, un mot de passe et une adresse d'expédition autorisée. |
| Un espace SFTP | Le second stockage des sauvegardes. De préférence chez un autre hébergeur que le serveur, et dans un autre lieu. Connexion par clé SSH. |
| Un gestionnaire de mots de passe | Pour garder le contenu de `.env` et surtout la **phrase secrète des sauvegardes**. |

La société étant en cours d'immatriculation, les champs légaux (numéro d'enregistrement, numéro de
TVA) restent vides : vous les saisirez dans Odoo le moment venu (Paramètres › Sociétés).

## 2. Préparer le serveur

Connectez-vous en `root` avec l'accès fourni par l'hébergeur.

### Un utilisateur qui n'est pas `root`

```bash
adduser chantrea
usermod -aG sudo chantrea
```

Depuis **votre poste**, copiez votre clé SSH puis vérifiez que la connexion fonctionne :

```bash
ssh-copy-id chantrea@ADRESSE_DU_SERVEUR
ssh chantrea@ADRESSE_DU_SERVEUR
```

Une fois connecté en `chantrea` avec votre clé, interdisez les mots de passe et le compte `root`
en SSH. Gardez la session ouverte tant que vous n'avez pas vérifié, dans une seconde fenêtre,
que la connexion marche encore.

```bash
sudo tee /etc/ssh/sshd_config.d/10-chantrea.conf >/dev/null <<'EOF'
PasswordAuthentication no
PermitRootLogin no
EOF
sudo systemctl restart ssh
```

### Pare-feu et mises à jour de sécurité

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 443/udp
sudo ufw enable

sudo apt-get update
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

Seuls les ports 80 et 443 sont publiés par l'application (le proxy Caddy). Odoo et PostgreSQL
ne sont joignables que de l'intérieur.

### Docker, git et les outils

```bash
sudo apt-get install -y ca-certificates curl git gnupg openssh-client
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker chantrea
```

Sur Debian, remplacez `ubuntu` par `debian` dans les deux adresses `download.docker.com`.
La page officielle fait foi : <https://docs.docker.com/engine/install/ubuntu/>.

Limitez la taille des journaux de Docker, sinon ils finissent par remplir le disque :

```bash
sudo tee /etc/docker/daemon.json >/dev/null <<'EOF'
{ "log-driver": "json-file", "log-opts": { "max-size": "20m", "max-file": "5" } }
EOF
sudo systemctl restart docker
```

Déconnectez-vous puis reconnectez-vous en `chantrea`, et vérifiez :

```bash
docker run --rm hello-world
docker compose version
```

L'utilisateur `chantrea` peut désormais piloter Docker, ce qui équivaut à être administrateur du
serveur : ne donnez ce compte à personne d'autre.

## 3. Récupérer le code

Le dépôt GitHub est privé. Le serveur y accède avec une **clé de déploiement en lecture seule**.

```bash
ssh-keygen -t ed25519 -N "" -C "serveur chantrea-odoo" -f ~/.ssh/chantrea_deploiement
cat ~/.ssh/chantrea_deploiement.pub
```

Dans GitHub, ouvrez le dépôt `stefan-cambodia/chantrea-odoo` › Settings › Deploy keys › Add deploy
key, collez la ligne affichée et **laissez décochée** la case « Allow write access ».

```bash
cat >> ~/.ssh/config <<'EOF'
Host github.com
  IdentityFile ~/.ssh/chantrea_deploiement
  IdentitiesOnly yes
EOF
sudo mkdir /opt/chantrea-odoo
sudo chown chantrea: /opt/chantrea-odoo
git clone --recurse-submodules --branch main git@github.com:stefan-cambodia/chantrea-odoo.git /opt/chantrea-odoo
cd /opt/chantrea-odoo
```

Le serveur suit la branche `main`. Les changements se préparent sur `developpement` et ne passent
dans `main` que sur votre décision (demandez-le-moi, ou faites une « pull request » sur GitHub).

## 4. Régler `.env`

```bash
cp .env.example .env
chmod 600 .env
nano .env
```

| Variable | Sur le serveur |
|---|---|
| `COMPOSE_FILE` | **Supprimez la ligne.** Elle ajoute les outils du poste local (Mailpit, code monté en direct). |
| `DOMAINE` | Votre nom de domaine, par exemple `erp.votre-domaine.com`. |
| `HTTP_PORT`, `HTTPS_PORT` | `80` et `443`. |
| `POSTGRES_PASSWORD` | À générer : `openssl rand -base64 32`. |
| `ODOO_ADMIN_PASSWD` | À générer de la même façon (c'est le mot de passe maître d'Odoo, pas celui de l'administrateur). |
| `ODOO_WORKERS` | `2` pour 2 processeurs. |
| `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` | Ceux de votre service d'envoi. |
| `SMTP_SSL` | `True` (connexion chiffrée STARTTLS, port 587). |
| `EMAIL_FROM` | L'adresse d'expédition autorisée par votre service d'envoi. |
| `ADMIN_LOCAL_PASSWORD`, `DEMO_CLIENT_PASSWORD` | **Vides.** Ils ne servent qu'en local. |
| `SAUVEGARDE_…`, `ALERTE_EMAIL` | Voir l'[étape 7](#7-sauvegardes). |

Recopiez le contenu de `.env` dans votre gestionnaire de mots de passe : ce fichier n'est jamais
dans le dépôt, et il n'est pas dans les sauvegardes.

## 5. Créer la base

```bash
scripts/init_serveur.sh
```

Le script vérifie d'abord `.env`, puis demande l'adresse courriel et le mot de passe de
l'administrateur (12 caractères au moins ; ils ne sont écrits dans aucun fichier). Il construit
ensuite l'image, crée la base en français, règle la société (Cambodge, USD, riel actif), installe
tous les modules, récupère le taux USD/KHR, démarre l'application et envoie un **courriel d'essai**
à l'administrateur. Comptez une dizaine de minutes. Il refuse de tourner si la base existe déjà.

À la fin :

1. Vérifiez que le courriel d'essai est arrivé. S'il n'arrive pas, voyez
   [Dépannage](#lenvoi-de-courriels-ne-fonctionne-pas) avant d'aller plus loin : sans courriels,
   vous ne pourrez pas vous connecter.
2. Ouvrez `https://VOTRE_DOMAINE`, identifiant `admin`. Un code vous est envoyé par courriel.
3. Créez un compte par personne (Paramètres › Utilisateurs), avec le groupe **Technicien** ou
   **Direction**, et gardez `admin` pour l'administration.
4. Vérifiez que `https://VOTRE_DOMAINE/web/database/manager` répond « 404 » : le gestionnaire de
   bases n'est pas accessible.

Les données de démonstration ne s'installent pas sur un serveur : `scripts/donnees_demo.sh` refuse
de tourner si `DOMAINE` n'est pas `localhost`.

## 6. Courriels

### Envoi

Tout passe par le serveur SMTP de `.env`. Pour que vos courriels n'arrivent pas dans les
indésirables, déclarez votre service d'envoi dans le DNS de votre domaine (enregistrements SPF et
DKIM : votre fournisseur de courriels donne les valeurs exactes).

Pour refaire un essai à tout moment :

```bash
scripts/essai_courriel.sh vous@votre-domaine.com
```

### Réception : ouvrir un ticket par courriel (facultatif)

Sans réglage supplémentaire, vos clients ouvrent leurs tickets dans l'espace client, et leurs
réponses à un courriel d'Odoo arrivent dans la boîte de l'expéditeur. Pour qu'un courriel envoyé à
une adresse comme `assistance@votre-domaine.com` crée un ticket :

1. Créez cette boîte aux lettres chez votre fournisseur de courriels (accès IMAP).
2. Dans Odoo, activez le mode développeur (Paramètres › tout en bas).
3. Paramètres › Technique › E-mail › **Alias de domaine** : créez votre domaine.
4. Paramètres › Technique › E-mail › **Serveurs de messagerie entrants** : ajoutez la boîte (IMAP,
   SSL), puis « Tester et confirmer ».
5. Assistance › Configuration › Les équipes › « Assistance Chantrea Systems » : donnez-lui l'alias
   de courriel `assistance`.

Cette partie n'a pas pu être essayée en local, faute de vraie boîte aux lettres : faites un essai
avec votre propre adresse avant de la communiquer à vos clients.

## 7. Sauvegardes

Chaque nuit, `scripts/sauvegarde.sh` :

1. exporte la base PostgreSQL et les fichiers d'Odoo (pièces jointes, PDF) ;
2. en fait une archive **chiffrée** (AES-256) avec la phrase secrète de `.env`, et la relit pour
   vérifier qu'elle est lisible ;
3. la copie sur le second stockage par SFTP et vérifie la copie ;
4. supprime les archives de plus de 30 jours, sur le serveur et sur le second stockage ;
5. envoie un courriel à `ALERTE_EMAIL` si quoi que ce soit échoue.

Une archive contient la base, les fichiers et un manifeste (date, version du code, chiffres de
contrôle). Elle ne contient **pas** `.env`.

### 7.1 La phrase secrète

```bash
openssl rand -base64 32
```

Copiez le résultat dans `.env` (`SAUVEGARDE_PHRASE=`) **et dans votre gestionnaire de mots de
passe**. Sans cette phrase, aucune sauvegarde n'est lisible, par personne. Si vous la changez un
jour, les archives déjà faites restent chiffrées avec l'ancienne : gardez les deux.

### 7.2 L'accès au second stockage

```bash
ssh-keygen -t ed25519 -N "" -C "sauvegarde chantrea-odoo" -f ~/.ssh/chantrea_sauvegarde
cat ~/.ssh/chantrea_sauvegarde.pub
```

Donnez cette clé publique à votre hébergeur SFTP (dans son interface, ou dans le fichier
`authorized_keys` du compte). Enregistrez ensuite l'empreinte du serveur SFTP :

```bash
ssh-keyscan -p 22 HOTE_SFTP >> ~/.ssh/known_hosts
ssh-keygen -lf ~/.ssh/known_hosts
```

Comparez l'empreinte affichée avec celle que publie votre hébergeur. Les scripts refusent de se
connecter à un serveur dont l'empreinte est inconnue ou a changé. Essayez la connexion :

```bash
sftp -P 22 -i ~/.ssh/chantrea_sauvegarde UTILISATEUR@HOTE_SFTP
```

Tapez `ls` puis `bye`. Remplissez ensuite `.env` :

| Variable | Valeur |
|---|---|
| `SAUVEGARDE_DOSSIER` | Dossier des archives sur le serveur. `sauvegardes` (dans le dépôt, ignoré par git) convient. |
| `SAUVEGARDE_JOURS` | `30`. |
| `SAUVEGARDE_PHRASE` | La phrase secrète du 7.1. |
| `SAUVEGARDE_SFTP_HOTE`, `SAUVEGARDE_SFTP_PORT`, `SAUVEGARDE_SFTP_UTILISATEUR` | Ceux de votre espace SFTP. |
| `SAUVEGARDE_SFTP_DOSSIER` | Dossier sur le second stockage, par exemple `chantrea`. Si votre hébergeur n'autorise l'écriture que dans un sous-dossier, indiquez-le : `depot/chantrea`. |
| `SAUVEGARDE_SFTP_CLE` | `/home/chantrea/.ssh/chantrea_sauvegarde` |
| `SAUVEGARDE_SFTP_HOTES_CONNUS` | `/home/chantrea/.ssh/known_hosts` |
| `ALERTE_EMAIL` | L'adresse à prévenir en cas d'échec. |

### 7.3 Première sauvegarde et premier essai de restauration, à la main

```bash
scripts/sauvegarde.sh
scripts/restauration.sh --essai --depuis-sftp
```

La première commande doit se terminer par « Sauvegarde terminée : 1 archive(s) ici, 1 sur le second
stockage ». La seconde télécharge cette archive, la restaure dans une base provisoire, vérifie son
contenu, supprime la base provisoire et doit se terminer par « ESSAI DE RESTAURATION RÉUSSI ».
Elle ne touche pas à la base en service.

### 7.4 Tâches planifiées

```bash
sudo cp deploiement/systemd/chantrea-*.service deploiement/systemd/chantrea-*.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now chantrea-sauvegarde.timer chantrea-essai-restauration.timer
systemctl list-timers 'chantrea-*'
```

| Tâche | Quand | Ce qu'elle fait |
|---|---|---|
| `chantrea-sauvegarde` | Chaque nuit à 2 h 30 (heure de Phnom Penh) | `scripts/sauvegarde.sh` |
| `chantrea-essai-restauration` | Chaque lundi à 3 h 30 | `scripts/restauration.sh --essai --depuis-sftp --oui` |

Ces fichiers supposent le dépôt dans `/opt/chantrea-odoo` et l'utilisateur `chantrea` : modifiez-les
si vous avez choisi autre chose. Pour voir le résultat de la dernière exécution :

```bash
journalctl -u chantrea-sauvegarde.service -n 30 --no-pager
journalctl -u chantrea-essai-restauration.service -n 30 --no-pager
```

Vous ne recevez un courriel qu'en cas d'échec. Si le serveur entier est arrêté, il ne peut pas
vous prévenir : jetez un œil à `systemctl list-timers 'chantrea-*'` de temps en temps, par exemple
à chaque mise à jour.

## 8. Restaurer

Dans tous les cas, l'archive est restaurée **à côté** de la base en service, puis vérifiée : mêmes
chiffres qu'au moment de la sauvegarde, chaque pièce jointe présente et intacte. La base en
service n'est touchée qu'après cette vérification.

### 8.1 Essayer, sans rien changer

```bash
scripts/restauration.sh --essai --depuis-sftp     # la dernière archive du second stockage
scripts/restauration.sh --essai --dernier         # la dernière archive du serveur
scripts/restauration.sh --essai sauvegardes/chantrea_2026-11-22_193000.tar.gz.gpg
```

### 8.2 Revenir à une sauvegarde, sur le même serveur

```bash
scripts/restauration.sh --remplacer --depuis-sftp
```

Le script demande de taper le nom de la base pour confirmer. Tout ce qui a été saisi depuis la
sauvegarde choisie n'est plus dans la base en service. L'ancienne base n'est pas supprimée : elle
est gardée sous le nom `chantrea_avant_restauration_<date>`, et le script affiche les deux
commandes pour la supprimer quand vous aurez tout contrôlé.

### 8.3 Le serveur est perdu

1. Louez un nouveau serveur et refaites les étapes 2 à 4, avec le `.env` gardé dans votre
   gestionnaire de mots de passe (la même `SAUVEGARDE_PHRASE`).
2. Refaites l'étape 7.2 : la clé SSH des sauvegardes était sur l'ancien serveur, il en faut une
   nouvelle, à autoriser chez votre hébergeur SFTP.
3. Restaurez :

   ```bash
   docker compose build odoo
   scripts/restauration.sh --depuis-sftp
   ```

4. Faites pointer le nom de domaine vers la nouvelle adresse IP, puis refaites l'étape 7.4.

Les comptes, les mots de passe des utilisateurs et tous les documents reviennent avec la base.

### 8.4 Ouvrir une sauvegarde du serveur sur votre poste

Mettez la phrase secrète dans le `.env` de votre installation locale, puis :

```bash
scripts/restauration.sh --remplacer ARCHIVE
```

Comme la sauvegarde vient d'un autre domaine que `localhost`, la copie est **neutralisée** avant
d'être mise en service : envois de courriels, relève des boîtes aux lettres et tâches planifiées
sont désactivés. Sans cela, votre poste relèverait la vraie boîte d'assistance et facturerait les
contrats à la place du serveur. Votre base locale précédente est gardée sous le nom
`chantrea_avant_restauration_<date>`.

Si vous changez un jour de nom de domaine, restaurez sur le nouveau serveur avec
`--sans-neutraliser`.

## 9. Mettre à jour

```bash
cd /opt/chantrea-odoo
scripts/sauvegarde.sh
git pull
scripts/mettre_a_jour.sh
```

`mettre_a_jour.sh` récupère les modules OCA à la version épinglée, reconstruit l'image, met la base
à jour et redémarre. L'application est indisponible quelques minutes. Si la mise à jour se passe
mal : `scripts/restauration.sh --remplacer --dernier`, après être revenu à la version précédente du
code (`git log` puis `git checkout <commit>`).

Les mises à jour de sécurité d'Ubuntu s'installent seules (étape 2). Les images Docker sont
épinglées par empreinte : leur mise à jour est décrite dans `docs/MODULES.md`.

## 10. Surveiller et dépanner

```bash
docker compose ps                 # état des services
docker compose logs --tail 100 odoo
docker compose logs --tail 50 caddy
df -h /                           # place sur le disque
systemctl list-timers 'chantrea-*'
```

### L'envoi de courriels ne fonctionne pas

```bash
scripts/essai_courriel.sh vous@votre-domaine.com
```

Le script affiche les réglages utilisés et l'erreur renvoyée par le serveur d'envoi. Corrigez
`SMTP_…` et `EMAIL_FROM` dans `.env`, puis appliquez :

```bash
docker compose up -d
```

### Je ne reçois pas le code de connexion

C'est un problème d'envoi de courriels : voyez le point précédent. En dernier recours, vous pouvez
lever l'obligation de code, le temps de réparer :

```bash
docker compose run --rm -T odoo odoo shell -d chantrea --no-http <<'EOF'
env["ir.config_parameter"].sudo().set_param("auth_totp.policy", "")
env.cr.commit()
EOF
```

Remettez-la dès que l'envoi fonctionne, avec la même commande et la valeur `"employee_required"`.

### Le site ne répond pas ou le certificat est refusé

Vérifiez que le nom de domaine pointe vers le serveur (`dig +short VOTRE_DOMAINE`), que les ports
80 et 443 sont ouverts chez l'hébergeur, puis lisez `docker compose logs --tail 50 caddy`.

### J'ai perdu le mot de passe de l'administrateur

```bash
docker compose run --rm -T odoo odoo shell -d chantrea --no-http <<'EOF'
env.ref("base.user_admin").password = "UN-NOUVEAU-MOT-DE-PASSE-LONG"
env.cr.commit()
EOF
```

## 11. Liste de contrôle avant la mise en service

- [ ] `https://VOTRE_DOMAINE` s'ouvre avec un certificat valide ; `/web/database/manager` répond 404.
- [ ] Le courriel d'essai et le code de connexion arrivent.
- [ ] Un compte par personne ; `admin` réservé à l'administration.
- [ ] `.env` et la phrase secrète des sauvegardes sont dans votre gestionnaire de mots de passe.
- [ ] `scripts/sauvegarde.sh` puis `scripts/restauration.sh --essai --depuis-sftp` ont réussi à la main.
- [ ] `systemctl list-timers 'chantrea-*'` montre les deux tâches.
- [ ] Un courriel d'alerte arrive bien à `ALERTE_EMAIL` (essai : mettez un faux port dans
      `SAUVEGARDE_SFTP_PORT`, lancez `scripts/sauvegarde.sh`, puis remettez le bon).
- [ ] Les textes khmers ont été relus (`docs/RELECTURE_KM.md`).
- [ ] Le taux USD/KHR du jour est présent (Facturation › Configuration › Taux USD/KHR).

## Ce qui a été essayé

Essayé sur le poste de développement, le 22/11/2026 :

- `scripts/essai_sauvegarde.sh` : sauvegarde chiffrée, copie sur un serveur SFTP provisoire, ménage
  des archives de plus de 30 jours, restauration d'essai avec vérification, courriel d'alerte après
  un échec provoqué.
- Une répétition « comme sur le serveur », dans une installation Docker séparée, sans les outils
  locaux et avec le code copié dans l'image :
  - `scripts/init_serveur.sh` (5 minutes sur ce poste), page de connexion servie en HTTPS,
    gestionnaire de bases fermé (404), traductions khmères présentes ;
  - `scripts/sauvegarde.sh`, puis destruction complète de l'installation (conteneurs et volumes) ;
  - `scripts/restauration.sh --depuis-sftp` sur l'installation vide : une minute, contenu vérifié,
    donnée témoin et pièce jointe retrouvées à l'identique ;
  - refus de remplacer une base existante sans `--remplacer` ; remplacement avec l'ancienne base
    gardée ; copie neutralisée quand la sauvegarde vient d'un autre domaine.
- La syntaxe et les horaires des tâches planifiées (`systemd-analyze`).

Pas essayé, parce que cela demande le vrai serveur : le certificat Let's Encrypt avec un vrai nom
de domaine, votre service d'envoi de courriels, votre hébergeur SFTP, les commandes de préparation
d'Ubuntu (étape 2), l'exécution des tâches planifiées par systemd, et la réception de courriels
(étape 6).
