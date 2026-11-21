#!/bin/bash
# Génère odoo.conf à partir des variables d'environnement, puis lance
# l'entrypoint officiel. Aucun secret n'est écrit dans le dépôt : ils
# viennent du fichier .env (non commité) au démarrage du conteneur.
set -euo pipefail

: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD manquant dans .env}"
: "${ODOO_ADMIN_PASSWD:?ODOO_ADMIN_PASSWD (mot de passe maître) manquant dans .env}"
: "${ODOO_DB_NAME:?ODOO_DB_NAME manquant dans .env}"

OCA=/opt/chantrea/oca
ADDONS_PATH="/opt/chantrea/addons,${OCA}/helpdesk,${OCA}/contract,${OCA}/field-service,${OCA}/timesheet,${OCA}/sign,/usr/lib/python3/dist-packages/odoo/addons"

umask 077
cat > "${ODOO_RC}" <<EOF
[options]
addons_path = ${ADDONS_PATH}
data_dir = /var/lib/odoo

db_host = db
db_port = 5432
db_user = ${POSTGRES_USER:-odoo}
db_password = ${POSTGRES_PASSWORD}
db_name = ${ODOO_DB_NAME}
dbfilter = ^${ODOO_DB_NAME}\$
list_db = False
admin_passwd = ${ODOO_ADMIN_PASSWD}

proxy_mode = True
# Écoute sur le réseau Docker interne uniquement (aucun port publié) :
# seul Caddy peut joindre Odoo.
http_interface = 0.0.0.0
workers = ${ODOO_WORKERS:-2}
max_cron_threads = ${ODOO_MAX_CRON_THREADS:-1}
gevent_port = 8072
limit_memory_soft = 1073741824
limit_memory_hard = 1610612736
limit_time_cpu = 600
limit_time_real = 1200

smtp_server = ${SMTP_SERVER:-localhost}
smtp_port = ${SMTP_PORT:-25}
smtp_ssl = ${SMTP_SSL:-False}
EOF

# Options facultatives : écrites seulement si elles sont renseignées.
if [ -n "${SMTP_USER:-}" ]; then echo "smtp_user = ${SMTP_USER}" >> "${ODOO_RC}"; fi
if [ -n "${SMTP_PASSWORD:-}" ]; then echo "smtp_password = ${SMTP_PASSWORD}" >> "${ODOO_RC}"; fi
if [ -n "${EMAIL_FROM:-}" ]; then echo "email_from = ${EMAIL_FROM}" >> "${ODOO_RC}"; fi

exec /entrypoint.sh "$@"
