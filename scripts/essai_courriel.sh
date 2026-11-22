#!/usr/bin/env bash
# Vérifie l'envoi de courriels du serveur, par deux courriels d'essai :
#   1. avec les seuls réglages SMTP de .env (le chemin des alertes de sauvegarde) ;
#   2. par Odoo lui-même, au nom de l'administrateur (le chemin du code de connexion, des
#      invitations et des courriels aux clients), en contrôlant l'adresse d'expéditeur.
# Usage : scripts/essai_courriel.sh adresse@exemple.com
set -euo pipefail
cd "$(dirname "$0")/.."
. scripts/lib/commun_sauvegarde.sh

case "${1:-}" in *?@?*.?*) ;; *) echo "Usage : scripts/essai_courriel.sh adresse@exemple.com"; exit 2 ;; esac
[ -f .env ] || echouer "fichier .env absent."
set -a; . ./.env; set +a
DB="${ODOO_DB_NAME:-chantrea}"
UTILISATEUR_PG="${POSTGRES_USER:-odoo}"

journal "Serveur d'envoi : ${SMTP_SERVER:-localhost}:${SMTP_PORT:-25} (STARTTLS : ${SMTP_SSL:-False}, expéditeur : ${EMAIL_FROM:-odoo@localhost})"
ALERTE_EMAIL="$1" alerter "[Chantrea] Courriel d'essai 1/2 (${DOMAINE:-?})" <<EOF
Courriel d'essai envoyé le $(date '+%d/%m/%Y à %H:%M') par scripts/essai_courriel.sh.
Si vous le lisez, l'envoi de courriels du serveur fonctionne.
Un second courriel, envoyé par Odoo lui-même, doit arriver en même temps.
EOF

if ! base_existe "$DB" 2>/dev/null; then
  journal "La base « ${DB} » n'existe pas encore : pas de second courriel (celui d'Odoo)."
  exit 0
fi

resultat=$(ESSAI_ADRESSE="$1" dans_odoo -e ESSAI_ADRESSE odoo odoo shell -d "$DB" --no-http --log-level=error 2>&1 <<'EOF' || true
import os
from odoo.tools import email_normalize

admin = env.ref("base.user_admin")
# Même calcul qu'à l'envoi : l'expéditeur qu'Odoo utilisera vraiment, compte tenu de
# EMAIL_FROM et, s'il existe, du domaine d'alias de la société.
domaine = env.company.alias_domain_id
serveurs = env["ir.mail_server"].with_context(domain_notifications_email=domaine.default_from_email or None)
print("EXPEDITEUR=%s" % (email_normalize(serveurs._find_mail_server(admin.email_formatted)[1]) or ""))
courriel = env["mail.mail"].sudo().create({
    "subject": "[Chantrea] Courriel d'essai 2/2, envoyé par Odoo",
    "email_from": admin.email_formatted,
    "email_to": os.environ["ESSAI_ADRESSE"],
    "body_html": "<p>Courriel d'essai envoyé par Odoo lui-même, au nom de l'administrateur.</p>"
                 "<p>Si vous le lisez, le code demandé à chaque connexion et les courriels "
                 "aux clients arriveront de la même façon.</p>",
    "auto_delete": True,
})
try:
    courriel.send(raise_exception=True)
    print("ENVOI=ok")
except Exception as erreur:
    print("ENVOI=%s" % " ".join(str(erreur).split()))
EOF
)
expediteur=$(sed -n 's/^EXPEDITEUR=//p' <<<"$resultat" | tail -n1)
envoi=$(sed -n 's/^ENVOI=//p' <<<"$resultat" | tail -n1)
attendu=$(tr '[:upper:]' '[:lower:]' <<<"${EMAIL_FROM:-}")

if [ "$envoi" = "ok" ]; then
  journal "Second courriel envoyé par Odoo à $1 (expéditeur : ${expediteur:-?})."
else
  journal "Odoo n'a pas pu envoyer le second courriel : ${envoi:-$(tail -n1 <<<"$resultat")}"
fi
if [ -n "$attendu" ] && [ -n "$expediteur" ] && [ "$expediteur" != "$attendu" ]; then
  journal "ATTENTION : Odoo envoie ses courriels avec l'expéditeur ${expediteur}, et non EMAIL_FROM (${attendu})."
  journal "  Votre service d'envoi peut les refuser. Corrigez « Alias d'envoi par défaut » dans Paramètres ›"
  journal "  Technique › E-mail › Alias de domaine : mettez-y ${attendu} (docs/DEPLOIEMENT.md, étape 6)."
fi
[ "$envoi" = "ok" ] || exit 1
