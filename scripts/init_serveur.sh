#!/usr/bin/env bash
# Crée la base sur le SERVEUR à partir de zéro : mêmes modules qu'en local, sans Mailpit
# ni données de démonstration. Refuse de tourner si la base existe déjà (rien n'est écrasé).
# Mode d'emploi complet : docs/DEPLOIEMENT.md.
#
# Usage : scripts/init_serveur.sh
# L'adresse courriel et le mot de passe de l'administrateur sont demandés au clavier :
# ils ne sont écrits dans aucun fichier.
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/lib/commun_sauvegarde.sh

[ -f .env ] || { echo "Fichier .env absent : cp .env.example .env puis le remplir (docs/DEPLOIEMENT.md)."; exit 1; }
set -a; . ./.env; set +a
DB="${ODOO_DB_NAME:-chantrea}"
UTILISATEUR_PG="${POSTGRES_USER:-odoo}"

# --- Réglages du serveur : on vérifie avant de commencer ---------------------------
erreurs=0
probleme() { echo "  - $*"; erreurs=1; }
case "${COMPOSE_FILE:-}" in
  *local*) probleme ".env : supprimez la ligne COMPOSE_FILE (elle ajoute les outils du poste local)." ;;
esac
for variable in DOMAINE POSTGRES_PASSWORD ODOO_ADMIN_PASSWD; do
  [ -n "${!variable:-}" ] || probleme ".env : $variable est vide."
done
[ "${SMTP_SERVER:-}" != "mailpit" ] || probleme ".env : SMTP_SERVER=mailpit est le réglage local ; indiquez votre serveur d'envoi."
[ -z "${ADMIN_LOCAL_PASSWORD:-}${DEMO_CLIENT_PASSWORD:-}" ] \
  || probleme ".env : videz ADMIN_LOCAL_PASSWORD et DEMO_CLIENT_PASSWORD (ils ne servent qu'en local)."
if [ "$erreurs" = 1 ]; then echo "Corrigez ces points puis relancez."; exit 1; fi

# --- Compte administrateur ----------------------------------------------------------
if [ -z "${ADMIN_EMAIL:-}" ]; then
  echo "Adresse courriel de l'administrateur : elle recevra le code demandé à chaque connexion."
  read -r -p "Adresse : " ADMIN_EMAIL
fi
case "$ADMIN_EMAIL" in *?@?*.?*) ;; *) echo "Adresse invalide : $ADMIN_EMAIL"; exit 1 ;; esac
if [ -z "${ADMIN_PASSWORD:-}" ]; then
  read -r -s -p "Mot de passe de l'administrateur (12 caractères au moins) : " ADMIN_PASSWORD; echo
  read -r -s -p "Encore une fois : " confirmation; echo
  [ "$ADMIN_PASSWORD" = "$confirmation" ] || { echo "Les deux saisies sont différentes."; exit 1; }
fi
[ "${#ADMIN_PASSWORD}" -ge 12 ] || { echo "Mot de passe trop court (12 caractères au moins)."; exit 1; }
URL_PUBLIQUE="https://${DOMAINE}"
[ "${HTTPS_PORT:-443}" = "443" ] || URL_PUBLIQUE="${URL_PUBLIQUE}:${HTTPS_PORT}"
export ADMIN_EMAIL ADMIN_PASSWORD URL_PUBLIQUE

git submodule update --init
docker compose build odoo
attendre_db
if base_existe "$DB"; then
  echo "La base « ${DB} » existe déjà. Pour mettre à jour : scripts/mettre_a_jour.sh"
  exit 1
fi

run() { docker compose run --rm -T "$@"; }

echo "==> 1/5 Création de la base « ${DB} » en français"
run odoo odoo -d "$DB" -i base --load-language=fr_FR --stop-after-init --no-http

echo "==> 2/5 Société (Cambodge, USD), administrateur, double authentification, adresse publique"
run -e ADMIN_EMAIL -e ADMIN_PASSWORD -e URL_PUBLIQUE odoo odoo shell -d "$DB" --no-http < scripts/lib/config_initiale.py

echo "==> 3/5 Installation des modules"
MODULES=$(grep -vE '^\s*(#|$)' scripts/modules.txt | paste -sd, -)
run odoo odoo -d "$DB" -i "$MODULES" --stop-after-init --no-http
run odoo odoo shell -d "$DB" --no-http --log-level=warn < scripts/lib/recuperer_taux.py \
  || echo "    Taux USD/KHR non récupéré : la tâche quotidienne réessaiera, ou saisissez-le à la main."

echo "==> 4/5 Démarrage"
docker compose up -d
scripts/verifier_modules.sh

echo "==> 5/5 Courriel d'essai à ${ADMIN_EMAIL}"
ALERTE_EMAIL="$ADMIN_EMAIL" alerter "[Chantrea] Courriel d'essai du serveur ${DOMAINE}" <<EOF
Ceci est le courriel d'essai envoyé à la fin de l'installation de ${URL_PUBLIQUE}.
Si vous le lisez, l'envoi de courriels fonctionne : vous recevrez de la même façon
le code demandé à chaque connexion.
EOF

cat <<EOF

Installation terminée : ${URL_PUBLIQUE}   (identifiant : admin)

AVANT de vous connecter, vérifiez que le courriel d'essai est arrivé à ${ADMIN_EMAIL}.
Le code de connexion arrive par courriel : sans envoi de courriels, pas de connexion.
S'il n'est pas arrivé : corrigez SMTP_* dans .env, puis « docker compose up -d »
(voir docs/DEPLOIEMENT.md, « Dépannage »).

Étapes suivantes : sauvegardes (scripts/sauvegarde.sh) et tâches planifiées, dans docs/DEPLOIEMENT.md.
EOF
