#!/usr/bin/env bash
# Essai avec de nombreux faux clients, sur le poste LOCAL, sans toucher à la base de travail :
#   1. copie de la base locale dans « <base>_essai_clients » ;
#   2. 40 faux clients (langues, factures, devis, tickets, matériel, contrats, interventions),
#      tâches du matin (factures des contrats, alertes de garantie), toutes les factures en PDF ;
#   3. un Odoo provisoire sur cette copie (http://127.0.0.1:8070, sans tâches planifiées) ;
#   4. connexion à l'espace client avec chaque compte : langue, chiffres de l'accueil,
#      listes, pages des autres clients refusées ; puis tous les comptes en même temps.
# La copie et l'Odoo provisoire sont supprimés à la fin, sauf avec --garder.
# Résultats : essai-clients/ (attendu.json, rapport.json, factures.pdf).
# Usage :
#   scripts/essai_clients.sh             # 40 clients
#   scripts/essai_clients.sh 80          # autre nombre
#   scripts/essai_clients.sh --garder    # laisse l'Odoo d'essai ouvert pour y naviguer
#   scripts/essai_clients.sh --nettoyer  # supprime ce qu'un --garder a laissé
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/lib/commun_sauvegarde.sh
charger_env
[ "${DOMAINE:-}" = "localhost" ] || echouer "essai réservé au poste local (DOMAINE=localhost)."
[ -n "${DEMO_CLIENT_PASSWORD:-}" ] || echouer "DEMO_CLIENT_PASSWORD manquant dans .env."
exiger docker curl python3

NOMBRE=40 GARDER=0 NETTOYER=0
for argument in "$@"; do
  case "$argument" in
    --garder) GARDER=1 ;;
    --nettoyer) NETTOYER=1 ;;
    ''|*[!0-9]*) echouer "argument inconnu : $argument" ;;
    *) NOMBRE="$argument" ;;
  esac
done
ESSAI="${DB}_essai_clients"
CONTENEUR="chantrea-essai-clients"
PORT=8070
SORTIE="$PWD/essai-clients"

nettoyer() {
  docker rm -f "$CONTENEUR" >/dev/null 2>&1 || true
  if base_existe "$ESSAI"; then
    docker compose exec -T db dropdb -U "$UTILISATEUR_PG" --force "$ESSAI"
  fi
  dans_odoo odoo rm -rf "/var/lib/odoo/filestore/$ESSAI"
}

attendre_db
if [ "$NETTOYER" = 1 ]; then nettoyer; journal "Base d'essai et Odoo provisoire supprimés."; exit 0; fi
base_existe "$DB" || echouer "la base « $DB » n'existe pas."
nettoyer  # restes d'un essai précédent
if [ "$GARDER" = 0 ]; then trap nettoyer EXIT; fi
mkdir -p "$SORTIE" && chmod 777 "$SORTIE"
rm -f "$SORTIE"/attendu.json "$SORTIE"/rapport.json "$SORTIE"/factures.pdf

journal "1/4 Copie de « $DB » dans « $ESSAI »"
docker compose exec -T db createdb -U "$UTILISATEUR_PG" -O "$UTILISATEUR_PG" "$ESSAI"
docker compose exec -T db bash -c 'pg_dump -U "$1" -Fc "$2" | pg_restore -U "$1" -d "$3" --no-owner --exit-on-error' \
  _ "$UTILISATEUR_PG" "$DB" "$ESSAI"
dans_odoo odoo bash -c 'cp -a "/var/lib/odoo/filestore/$1" "/var/lib/odoo/filestore/$2"' _ "$DB" "$ESSAI"

journal "2/4 $NOMBRE faux clients, tâches du matin, factures en PDF"
dans_odoo -e ODOO_DB_NAME="$ESSAI" -e ESSAI_NOMBRE="$NOMBRE" -v "$SORTIE:/sortie" \
  odoo odoo shell -d "$ESSAI" --no-http --log-level=warn < scripts/lib/essai_clients.py | grep -v '^$' || true
[ -s "$SORTIE/attendu.json" ] || echouer "la génération des faux clients a échoué (voir ci-dessus)."

journal "3/4 Odoo provisoire sur http://127.0.0.1:$PORT"
docker compose run -d --rm --no-deps --name "$CONTENEUR" -p "127.0.0.1:$PORT:8069" \
  -e ODOO_DB_NAME="$ESSAI" -e ODOO_MAX_CRON_THREADS=0 odoo >/dev/null
for _ in $(seq 1 60); do
  curl -fsS -o /dev/null "http://127.0.0.1:$PORT/web/login" 2>/dev/null && break
  sleep 2
done
curl -fsS -o /dev/null "http://127.0.0.1:$PORT/web/login" || echouer "l'Odoo provisoire ne répond pas."

journal "4/4 Connexion de chaque client à l'espace client"
code=0
python3 -I scripts/lib/essai_clients_verif.py "http://127.0.0.1:$PORT" "$SORTIE/attendu.json" "$SORTIE/rapport.json" \
  || code=$?

if [ "$GARDER" = 1 ]; then
  journal "Odoo d'essai laissé ouvert : http://127.0.0.1:$PORT (comptes e001a@essai.example…, mot de passe DEMO_CLIENT_PASSWORD)."
  journal "Pour tout supprimer : scripts/essai_clients.sh --nettoyer"
fi
[ "$code" = 0 ] && journal "ESSAI RÉUSSI" || journal "ESSAI EN ÉCHEC : voir les défauts ci-dessus"
exit "$code"
