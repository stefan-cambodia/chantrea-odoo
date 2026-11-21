#!/usr/bin/env bash
# Affiche l'état et la licence de chaque module demandé.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a

docker compose run --rm -T -v "$PWD/scripts/modules.txt:/tmp/modules.txt:ro" odoo \
  odoo shell -d "${ODOO_DB_NAME:-chantrea}" --no-http --log-level=warn \
  < scripts/lib/verifier_modules.py
