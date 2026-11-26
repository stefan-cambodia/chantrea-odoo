#!/usr/bin/env bash
# Charge les données de DÉMONSTRATION dans la base LOCALE et produit des PDF
# de test dans demo-pdf/. Ne jamais lancer sur le serveur.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a

if [ "${DOMAINE:-}" != "localhost" ]; then
  echo "Refusé : DOMAINE n'est pas « localhost ». Les données de démo sont réservées au poste local."
  exit 1
fi

mkdir -p demo-pdf && chmod 777 demo-pdf
# Les deux scripts s'exécutent dans le même « odoo shell » : le second reprend les produits,
# taxes et réglages du premier (clients par combinaison de langues, PDF dans demo-pdf/langues/).
cat scripts/lib/donnees_demo.py scripts/lib/donnees_demo_langues.py | \
  docker compose run --rm -T -v "$PWD/demo-pdf:/sortie" odoo \
  odoo shell -d "${ODOO_DB_NAME:-chantrea}" --no-http --log-level=warn
