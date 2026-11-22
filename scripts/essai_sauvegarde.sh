#!/usr/bin/env bash
# Essai complet des sauvegardes sur le poste LOCAL, sans toucher à la base de travail :
#   1. sauvegarde chiffrée de la base locale, copiée sur un serveur SFTP provisoire ;
#   2. ménage : une archive de plus de 30 jours disparaît, une archive récente reste ;
#   3. restauration d'essai depuis le serveur SFTP, avec vérification du contenu ;
#   4. échec provoqué : le courriel d'alerte doit arriver (dans Mailpit).
# Le serveur SFTP, les clés et les archives de l'essai sont supprimés à la fin.
# Vos réglages de sauvegarde dans .env ne sont pas utilisés.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . ./.env; set +a
[ "${DOMAINE:-}" = "localhost" ] || { echo "Refusé : essai réservé au poste local (DOMAINE=localhost)."; exit 1; }
for outil in docker gpg sftp ssh-keygen ssh-keyscan openssl curl; do
  command -v "$outil" >/dev/null 2>&1 || { echo "Outil manquant : $outil"; exit 1; }
done

# Serveur SFTP d'essai (image épinglée, voir docs/MODULES.md).
IMAGE_SFTP="atmoz/sftp@sha256:c5fb9e4beb8b7054a4c0b65c5e11df47cc20da95ad6002e88aecff62bab06372"
PORT_SFTP=2222
CONTENEUR="chantrea-essai-sftp"
DB="${ODOO_DB_NAME:-chantrea}"
ESSAI=$(mktemp -d)
nettoyer() {
  docker rm -f "$CONTENEUR" >/dev/null 2>&1 || true
  rm -rf "$ESSAI"
}
trap nettoyer EXIT

etape() { echo; echo "==> $*"; }
verifier() {  # libellé, commande…
  local libelle="$1"; shift
  if "$@"; then echo "    OK : $libelle"; else echo "    ÉCHEC : $libelle"; exit 1; fi
}

etape "Serveur SFTP provisoire sur 127.0.0.1:$PORT_SFTP"
ssh-keygen -q -t ed25519 -N "" -C essai-sauvegarde -f "$ESSAI/cle"
docker rm -f "$CONTENEUR" >/dev/null 2>&1 || true
docker run -d --name "$CONTENEUR" -p "127.0.0.1:$PORT_SFTP:22" \
  -v "$ESSAI/cle.pub:/home/sauvegarde/.ssh/keys/cle.pub:ro" "$IMAGE_SFTP" "sauvegarde::1001::depot" >/dev/null
for _ in $(seq 1 30); do
  ssh-keyscan -p "$PORT_SFTP" -t ed25519 127.0.0.1 > "$ESSAI/hotes_connus" 2>/dev/null || true
  [ -s "$ESSAI/hotes_connus" ] && break
  sleep 1
done
[ -s "$ESSAI/hotes_connus" ] || { echo "Le serveur SFTP d'essai ne répond pas."; exit 1; }

cat > "$ESSAI/reglages.env" <<EOF
SAUVEGARDE_DOSSIER=$ESSAI/archives
SAUVEGARDE_JOURS=30
SAUVEGARDE_PHRASE=$(openssl rand -base64 32)
SAUVEGARDE_SFTP_HOTE=127.0.0.1
SAUVEGARDE_SFTP_PORT=$PORT_SFTP
SAUVEGARDE_SFTP_UTILISATEUR=sauvegarde
SAUVEGARDE_SFTP_DOSSIER=depot/chantrea
SAUVEGARDE_SFTP_CLE=$ESSAI/cle
SAUVEGARDE_SFTP_HOTES_CONNUS=$ESSAI/hotes_connus
ALERTE_EMAIL=alerte-sauvegarde@example.com
EOF
export SAUVEGARDE_ENV="$ESSAI/reglages.env"

sftp_essai() {
  sftp -q -b - -P "$PORT_SFTP" -i "$ESSAI/cle" -o IdentitiesOnly=yes -o BatchMode=yes \
       -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$ESSAI/hotes_connus" sauvegarde@127.0.0.1
}

# Deux fausses archives, ici et sur le serveur SFTP : une de 40 jours, une de 10 jours.
VIEILLE="${DB}_$(date -u -d '40 days ago' '+%Y-%m-%d')_020000.tar.gz.gpg"
RECENTE="${DB}_$(date -u -d '10 days ago' '+%Y-%m-%d')_020000.tar.gz.gpg"
mkdir -p "$ESSAI/archives"
echo "fausse archive" > "$ESSAI/archives/$VIEILLE"
echo "fausse archive" > "$ESSAI/archives/$RECENTE"
sftp_essai >/dev/null <<EOF
-mkdir depot/chantrea
put $ESSAI/archives/$VIEILLE depot/chantrea/$VIEILLE
put $ESSAI/archives/$RECENTE depot/chantrea/$RECENTE
EOF

etape "1. Sauvegarde chiffrée de la base « $DB » et copie SFTP"
scripts/sauvegarde.sh
ARCHIVE=$(ls "$ESSAI"/archives/"${DB}"_*.tar.gz.gpg | sort | tail -n1)
verifier "l'archive n'est pas lisible sans la phrase secrète" \
  bash -c "! tar -tzf '$ARCHIVE' >/dev/null 2>&1 && ! grep -aq 'PGDMP' '$ARCHIVE'"

etape "2. Ménage des archives de plus de 30 jours"
DISTANT=$(sftp_essai <<<"ls -1 depot/chantrea")
verifier "archive de 40 jours supprimée ici" test ! -e "$ESSAI/archives/$VIEILLE"
verifier "archive de 10 jours gardée ici" test -e "$ESSAI/archives/$RECENTE"
verifier "archive de 40 jours supprimée sur le serveur SFTP" bash -c "! grep -q '$VIEILLE' <<<'$DISTANT'"
verifier "archive de 10 jours gardée sur le serveur SFTP" grep -q "$RECENTE" <<<"$DISTANT"
verifier "archive du jour présente sur le serveur SFTP" grep -q "$(basename "$ARCHIVE")" <<<"$DISTANT"

etape "3. Restauration d'essai depuis le serveur SFTP (la base de travail n'est pas touchée)"
rm -f "$ARCHIVE"   # l'archive locale disparaît : seule la copie distante peut servir
scripts/restauration.sh --essai --depuis-sftp --oui
verifier "aucune base d'essai ne reste" bash -c \
  "! docker compose exec -T db psql -U '${POSTGRES_USER:-odoo}' -d postgres -tAc \"SELECT datname FROM pg_database\" | grep -q essai_restauration"

etape "4. Échec provoqué (serveur SFTP injoignable) : le courriel d'alerte doit arriver"
total_mailpit() { curl -s "http://localhost:8025/api/v1/search?query=subject:%22sauvegarde%20de%20$DB%22" | grep -o '"messages_count":[0-9]*' | cut -d: -f2; }
AVANT=$(total_mailpit || echo 0)
sed -i "s/^SAUVEGARDE_SFTP_PORT=.*/SAUVEGARDE_SFTP_PORT=2229/" "$ESSAI/reglages.env"
if scripts/sauvegarde.sh > "$ESSAI/echec.txt" 2>&1; then
  echo "    ÉCHEC : la sauvegarde aurait dû échouer"; exit 1
fi
tail -n 4 "$ESSAI/echec.txt" | sed 's/^/    | /'
sleep 2
APRES=$(total_mailpit || echo 0)
verifier "code de sortie différent de 0" true
verifier "courriel d'alerte reçu dans Mailpit (http://localhost:8025)" test "${APRES:-0}" -gt "${AVANT:-0}"

etape "ESSAI RÉUSSI : sauvegarde, copie SFTP, ménage, restauration vérifiée et alerte fonctionnent."
