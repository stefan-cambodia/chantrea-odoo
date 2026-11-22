#!/usr/bin/env bash
# Lance les tests automatiques des modules maison dans une base SÉPARÉE
# (« <base>_test »), jamais dans la base de travail.
# Usage :
#   scripts/tests.sh            # recrée la base de test de zéro (installation complète, ~6 min)
#   scripts/tests.sh --rapide   # réutilise la base de test existante (mise à jour seulement)
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a
DB="${ODOO_DB_NAME:-chantrea}_test"
MODULES_MAISON=$(ls -d addons/chantrea_*/ | xargs -n1 basename | paste -sd, -)
TAGS=$(echo "$MODULES_MAISON" | sed 's/[^,]*/\/&/g')

run() { docker compose run --rm -T odoo "$@"; }
existe() {
  docker compose exec -T db psql -U "${POSTGRES_USER:-odoo}" -d postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname='${DB}'" | grep -q 1
}

docker compose up -d db

if [ "${1:-}" = "--rapide" ] && existe; then
  # -i installe un module maison encore absent, -u met à jour les autres.
  ACTION=(-i "$MODULES_MAISON" -u "$MODULES_MAISON")
else
  if existe; then
    docker compose exec -T db dropdb -U "${POSTGRES_USER:-odoo}" "$DB"
  fi
  run odoo -d "$DB" -i base --load-language=fr_FR --stop-after-init --no-http
  run odoo shell -d "$DB" --no-http < scripts/lib/config_initiale.py
  MODULES=$(grep -vE '^\s*(#|$)' scripts/modules.txt | paste -sd, -)
  ACTION=(-i "$MODULES")
fi

JOURNAL=$(mktemp)
# Serveur web actif (tests des pages de l'espace client), un seul processus,
# et filtre de base adapté à la base de test.
run odoo -d "$DB" "${ACTION[@]}" --test-enable --test-tags "$TAGS" \
  --workers=0 --db-filter="^${DB}\$" --stop-after-init 2>&1 | tee "$JOURNAL" | grep -E "Running tests|tests in|FAIL|ERROR|Traceback|^\s+File|Error:" || true

echo
NB=$(grep -c " Starting Test" "$JOURNAL" || true)
if grep -qE "(FAIL|ERROR): Test| (ERROR|CRITICAL) [^ ]+ odoo\.(addons\.chantrea|tests|modules)" "$JOURNAL"; then
  echo "ÉCHEC : voir le détail ci-dessus (journal complet : $JOURNAL)"
  exit 1
fi
if [ "$NB" -eq 0 ]; then
  echo "ÉCHEC : aucun test n'a été exécuté (journal complet : $JOURNAL)"
  exit 1
fi
grep -E "odoo.tests.stats" "$JOURNAL" | sed -E 's/^.*odoo.tests.stats: //'
echo "Tests réussis : $NB tests exécutés, aucun échec."
