#!/usr/bin/env bash
# Crée la base locale à partir de zéro et installe tous les modules.
# ATTENTION : refuse de tourner si la base existe déjà (rien n'est écrasé).
# Usage : scripts/init_local.sh
set -euo pipefail
cd "$(dirname "$0")/.."

[ -f .env ] || { echo "Fichier .env absent : cp .env.example .env puis le remplir."; exit 1; }
set -a; . ./.env; set +a
DB="${ODOO_DB_NAME:-chantrea}"

git submodule update --init

docker compose build odoo
docker compose up -d db mailpit

if docker compose exec -T db psql -U "${POSTGRES_USER:-odoo}" -d postgres -tAc \
     "SELECT 1 FROM pg_database WHERE datname='${DB}'" | grep -q 1; then
  echo "La base « ${DB} » existe déjà. Pour mettre à jour : scripts/mettre_a_jour.sh"
  exit 1
fi

run() { docker compose run --rm -T odoo "$@"; }

echo "==> 1/4 Création de la base « ${DB} » en français"
run odoo -d "$DB" -i base --load-language=fr_FR --stop-after-init --no-http

echo "==> 2/4 Société (Cambodge, USD), admin en français, double authentification"
run odoo shell -d "$DB" --no-http < scripts/lib/config_initiale.py

echo "==> 3/4 Installation des modules"
MODULES=$(grep -vE '^\s*(#|$)' scripts/modules.txt | paste -sd, -)
run odoo -d "$DB" -i "$MODULES" --stop-after-init --no-http
run odoo shell -d "$DB" --no-http --log-level=warn < scripts/lib/recuperer_taux.py

echo "==> 4/4 Démarrage"
docker compose up -d
scripts/verifier_modules.sh
echo
echo "Odoo : https://${DOMAINE}:${HTTPS_PORT}   (identifiant : admin)"
echo "Courriels de test (Mailpit) : http://localhost:8025"
