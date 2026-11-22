# Fonctions communes à scripts/sauvegarde.sh et scripts/restauration.sh.
# À inclure avec « . scripts/lib/commun_sauvegarde.sh » depuis la racine du dépôt.

# Nom d'une archive : <base>_AAAA-MM-JJ_HHMMSS.tar.gz.gpg (heure UTC).
MOTIF_DATE='[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{6}'

journal() { echo "[$(date '+%F %T')] $*"; }

echouer() { journal "ERREUR : $*"; exit 1; }

charger_env() {
  [ -f .env ] || echouer "fichier .env absent (cp .env.example .env puis le remplir)."
  set -a
  . ./.env
  # Réglages d'essai : scripts/essai_sauvegarde.sh remplace les réglages de .env.
  if [ -n "${SAUVEGARDE_ENV:-}" ]; then . "$SAUVEGARDE_ENV"; fi
  set +a
  DB="${ODOO_DB_NAME:-chantrea}"
  UTILISATEUR_PG="${POSTGRES_USER:-odoo}"
  DOSSIER="${SAUVEGARDE_DOSSIER:-sauvegardes}"
  JOURS="${SAUVEGARDE_JOURS:-30}"
  mkdir -p "$DOSSIER"
  chmod 700 "$DOSSIER"
}

exiger() {
  local outil
  for outil in "$@"; do
    command -v "$outil" >/dev/null 2>&1 || echouer "outil manquant : $outil (voir docs/DEPLOIEMENT.md)."
  done
}

exiger_phrase() {
  [ "${#SAUVEGARDE_PHRASE}" -ge 20 ] 2>/dev/null \
    || echouer "SAUVEGARDE_PHRASE absente ou trop courte dans .env (générer avec : openssl rand -base64 32)."
}

# --- Chiffrement (GnuPG, AES-256, phrase secrète de .env) ---------------------
# La phrase passe par un descripteur de fichier : elle n'apparaît ni dans la liste
# des processus ni sur le disque. Un dossier GnuPG temporaire évite de toucher au
# trousseau de l'utilisateur.
_gpg() {
  local maison code=0
  maison=$(mktemp -d)
  gpg --homedir "$maison" --batch --yes --quiet --no-tty --pinentry-mode loopback \
      --passphrase-fd 3 "$@" 3<<<"$SAUVEGARDE_PHRASE" || code=$?
  rm -rf "$maison"
  return $code
}

chiffrer() {    # entrée standard → fichier $1
  _gpg --symmetric --cipher-algo AES256 --s2k-digest-algo SHA512 --compress-algo none --output "$1"
}

dechiffrer() {  # fichier $1 → sortie standard
  _gpg --decrypt "$1"
}

# --- Base de données et fichiers ---------------------------------------------------
psql_db() { docker compose exec -T db psql -U "$UTILISATEUR_PG" -v ON_ERROR_STOP=1 "$@"; }

base_existe() {
  psql_db -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$1'" | grep -q 1
}

attendre_db() {
  docker compose up -d db >/dev/null 2>&1
  local essai
  for essai in $(seq 1 30); do
    docker compose exec -T db pg_isready -U "$UTILISATEUR_PG" -d postgres >/dev/null 2>&1 && return 0
    sleep 2
  done
  echouer "PostgreSQL ne répond pas."
}

# Commande dans un conteneur Odoo jetable : fonctionne même si le service est arrêté.
dans_odoo() { docker compose run --rm --no-deps -T "$@"; }

# Chiffres de contrôle d'une base, une ligne « nom=valeur » par chiffre.
chiffres_de_controle() {
  psql_db -d "$1" -tA -F= <<'SQL'
SELECT 'contacts', count(*) FROM res_partner
UNION ALL SELECT 'utilisateurs', count(*) FROM res_users
UNION ALL SELECT 'pieces_comptables', count(*) FROM account_move
UNION ALL SELECT 'pieces_jointes', count(*) FROM ir_attachment
UNION ALL SELECT 'fichiers', count(DISTINCT store_fname) FROM ir_attachment WHERE store_fname IS NOT NULL
ORDER BY 1;
SQL
}

# --- Second stockage (SFTP) ---------------------------------------------------------
sftp_configure() {
  [ -n "${SAUVEGARDE_SFTP_HOTE:-}" ] && [ -n "${SAUVEGARDE_SFTP_UTILISATEUR:-}" ]
}

exiger_sftp() {
  sftp_configure || echouer "second stockage non réglé : SAUVEGARDE_SFTP_HOTE et SAUVEGARDE_SFTP_UTILISATEUR dans .env."
  [ -r "${SAUVEGARDE_SFTP_CLE:-}" ] || echouer "clé SSH illisible : SAUVEGARDE_SFTP_CLE=${SAUVEGARDE_SFTP_CLE:-}"
  [ -r "${SAUVEGARDE_SFTP_HOTES_CONNUS:-}" ] \
    || echouer "fichier des hôtes connus illisible : SAUVEGARDE_SFTP_HOTES_CONNUS=${SAUVEGARDE_SFTP_HOTES_CONNUS:-}"
  DOSSIER_SFTP="${SAUVEGARDE_SFTP_DOSSIER:-chantrea}"
}

# Exécute les commandes SFTP lues sur l'entrée standard. S'arrête à la première erreur.
# L'empreinte du serveur est vérifiée (StrictHostKeyChecking) : pas de connexion à un
# serveur inconnu ou remplacé.
sftp_lot() {
  sftp -q -b - -P "${SAUVEGARDE_SFTP_PORT:-22}" -i "$SAUVEGARDE_SFTP_CLE" \
       -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes \
       -o UserKnownHostsFile="$SAUVEGARDE_SFTP_HOTES_CONNUS" -o ConnectTimeout=20 \
       "${SAUVEGARDE_SFTP_UTILISATEUR}@${SAUVEGARDE_SFTP_HOTE}"
}

# Archives de cette base présentes sur le second stockage, de la plus ancienne à la plus récente.
sftp_lister() {
  sftp_lot <<<"ls -1 $DOSSIER_SFTP" | grep -oE "${DB}_${MOTIF_DATE}\.tar\.gz\.gpg" | sort -u
}

# --- Alerte par courriel --------------------------------------------------------------
# Envoyée par un conteneur Odoo jetable, avec les réglages SMTP de .env : fonctionne
# même si Odoo est arrêté. Le texte est lu sur l'entrée standard.
alerter() {
  local sujet="$1"
  if [ -z "${ALERTE_EMAIL:-}" ]; then
    journal "ALERTE_EMAIL non réglé dans .env : aucun courriel d'alerte envoyé."
    cat >/dev/null
    return 0
  fi
  local erreur
  if erreur=$(ALERTE_SUJET="$sujet" dans_odoo -e ALERTE_EMAIL -e ALERTE_SUJET odoo python3 -c '
import os, smtplib, sys
from email.message import EmailMessage

message = EmailMessage()
message["Subject"] = os.environ["ALERTE_SUJET"]
message["From"] = os.environ.get("EMAIL_FROM") or "odoo@localhost"
message["To"] = os.environ["ALERTE_EMAIL"]
message.set_content(sys.stdin.read())
serveur = smtplib.SMTP(os.environ.get("SMTP_SERVER") or "localhost", int(os.environ.get("SMTP_PORT") or 25), timeout=30)
if (os.environ.get("SMTP_SSL") or "").strip().lower() in ("true", "1"):
    serveur.starttls()
if os.environ.get("SMTP_USER"):
    serveur.login(os.environ["SMTP_USER"], os.environ.get("SMTP_PASSWORD", ""))
serveur.send_message(message)
serveur.quit()
' 2>&1 >/dev/null); then
    journal "Courriel envoyé à $ALERTE_EMAIL."
  else
    journal "Le courriel n'a pas pu être envoyé à $ALERTE_EMAIL (réglages SMTP_* de .env) : $(tail -n1 <<<"$erreur")"
  fi
}
