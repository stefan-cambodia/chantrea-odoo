#!/usr/bin/env bash
# Envoie un courriel d'essai avec les réglages SMTP de .env, pour vérifier l'envoi de
# courriels du serveur (codes de connexion, accusés de réception, alertes de sauvegarde).
# Usage : scripts/essai_courriel.sh adresse@exemple.com
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/lib/commun_sauvegarde.sh

case "${1:-}" in *?@?*.?*) ;; *) echo "Usage : scripts/essai_courriel.sh adresse@exemple.com"; exit 2 ;; esac
[ -f .env ] || echouer "fichier .env absent."
set -a; . ./.env; set +a

journal "Serveur d'envoi : ${SMTP_SERVER:-localhost}:${SMTP_PORT:-25} (STARTTLS : ${SMTP_SSL:-False}, expéditeur : ${EMAIL_FROM:-odoo@localhost})"
ALERTE_EMAIL="$1" alerter "[Chantrea] Courriel d'essai (${DOMAINE:-?})" <<EOF
Courriel d'essai envoyé le $(date '+%d/%m/%Y à %H:%M') par scripts/essai_courriel.sh.
Si vous le lisez, l'envoi de courriels du serveur fonctionne.
EOF
