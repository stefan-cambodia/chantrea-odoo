#!/usr/bin/env bash
# Met à jour les modules dans la base après un changement de code
# (module maison modifié, ou sous-module OCA avancé à un nouveau commit).
# Usage :
#   scripts/mettre_a_jour.sh                     # met à jour tous les modules
#   scripts/mettre_a_jour.sh chantrea_parc,...   # seulement ceux-là
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a
DB="${ODOO_DB_NAME:-chantrea}"
MODULES="${1:-all}"

git submodule update --init
docker compose build odoo
docker compose stop odoo
docker compose run --rm -T odoo odoo -d "$DB" -u "$MODULES" --stop-after-init --no-http
docker compose up -d
scripts/verifier_modules.sh
