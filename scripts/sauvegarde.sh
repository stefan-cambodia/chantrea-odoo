#!/usr/bin/env bash
# Sauvegarde de la base PostgreSQL et des fichiers d'Odoo (pièces jointes) dans une
# archive chiffrée, copiée sur un second stockage (SFTP). Les archives de plus de
# SAUVEGARDE_JOURS jours (30 par défaut) sont supprimées, ici et sur le second stockage.
#
# Usage :
#   scripts/sauvegarde.sh               # sauvegarde + copie SFTP + ménage
#   scripts/sauvegarde.sh --sans-copie  # archive locale seulement (essais)
#
# En cas d'échec : code de sortie différent de 0 et courriel à ALERTE_EMAIL.
# Réglages dans .env (voir .env.example) ; restauration : scripts/restauration.sh.
set -euo pipefail
export LC_COLLATE=C
cd "$(dirname "$0")/.."
. scripts/lib/commun_sauvegarde.sh

COPIE=1
case "${1:-}" in
  "") ;;
  --sans-copie) COPIE=0 ;;
  *) echo "Usage : scripts/sauvegarde.sh [--sans-copie]"; exit 2 ;;
esac

charger_env
exiger docker gpg tar gzip flock
exiger_phrase
if [ "$COPIE" = 1 ]; then exiger sftp; exiger_sftp; fi

# Une seule sauvegarde à la fois.
exec 9>"$DOSSIER/.verrou"
flock -n 9 || echouer "une autre sauvegarde est déjà en cours."

TRAVAIL=$(mktemp -d -p "$DOSSIER" .en-cours.XXXXXX)
JOURNAL="$TRAVAIL/journal.txt"
exec > >(tee -a "$JOURNAL") 2>&1

fin() {
  local code=$?
  if [ "$code" -ne 0 ]; then
    journal "ÉCHEC de la sauvegarde (code $code)."
    { echo "La sauvegarde de la base « $DB » (${DOMAINE:-?}) a échoué le $(date '+%d/%m/%Y à %H:%M')."
      echo "La sauvegarde de cette nuit est absente ou n'a pas été copiée sur le second stockage."
      echo "Fin du journal :"
      echo
      tail -n 40 "$JOURNAL" 2>/dev/null
    } | alerter "[Chantrea] ÉCHEC de la sauvegarde de $DB" || true
  fi
  rm -rf "$TRAVAIL"
  exit "$code"
}
trap fin EXIT

HORODATAGE=$(date -u '+%Y-%m-%d_%H%M%S')
NOM="${DB}_${HORODATAGE}.tar.gz.gpg"
journal "Sauvegarde de la base « $DB » → $NOM"

# --- 1. Base de données ----------------------------------------------------------
attendre_db
base_existe "$DB" || echouer "la base « $DB » n'existe pas."
journal "1/5 Base de données (pg_dump)"
docker compose exec -T db pg_dump -U "$UTILISATEUR_PG" -Fc -d "$DB" > "$TRAVAIL/base.dump"
# La table des matières du dump doit être lisible et contenir des tables.
TABLES=$(docker compose exec -T db pg_restore -l < "$TRAVAIL/base.dump" | grep -c ' TABLE DATA ' || true)
[ "$TABLES" -gt 50 ] || echouer "dump illisible ou incomplet ($TABLES tables)."

# --- 2. Fichiers (pièces jointes) ---------------------------------------------------
journal "2/5 Fichiers d'Odoo (filestore)"
dans_odoo odoo bash -c 'mkdir -p "/var/lib/odoo/filestore/$1" && tar -C "/var/lib/odoo/filestore/$1" -cf - .' _ "$DB" \
  > "$TRAVAIL/filestore.tar" 2>>"$JOURNAL"
FICHIERS=$(tar -tf "$TRAVAIL/filestore.tar" | grep -vc '/$' || true)

# --- 3. Manifeste ---------------------------------------------------------------------
{
  echo "Sauvegarde chantrea-odoo"
  echo "date_utc=$(date -u '+%Y-%m-%d %H:%M:%S')"
  echo "base=$DB"
  echo "domaine=${DOMAINE:-}"
  echo "commit=$(git rev-parse HEAD 2>/dev/null || echo inconnu)"
  echo "modifications_non_commitees=$(git status --porcelain 2>/dev/null | wc -l)"
  echo "postgresql=$(docker compose exec -T db pg_dump --version | tr -d '\r')"
  echo "tables=$TABLES"
  echo "fichiers_archive=$FICHIERS"
  echo "[chiffres]"
  chiffres_de_controle "$DB"
  echo "[sous-modules]"
  git submodule status 2>/dev/null || true
} > "$TRAVAIL/MANIFESTE.txt"

# --- 4. Archive chiffrée -----------------------------------------------------------------
journal "3/5 Archive chiffrée"
ARCHIVE="$DOSSIER/$NOM"
tar -C "$TRAVAIL" -czf - MANIFESTE.txt base.dump filestore.tar | chiffrer "$ARCHIVE.partiel"
chmod 600 "$ARCHIVE.partiel"
# Relecture complète : déchiffrement et liste du contenu.
CONTENU=$(dechiffrer "$ARCHIVE.partiel" | tar -tzf - | sort | tr '\n' ' ')
[ "$CONTENU" = "MANIFESTE.txt base.dump filestore.tar " ] || echouer "archive illisible après chiffrement ($CONTENU)."
mv "$ARCHIVE.partiel" "$ARCHIVE"
TAILLE=$(stat -c %s "$ARCHIVE")
journal "    $NOM : $(numfmt --to=iec "$TAILLE"), $TABLES tables, $FICHIERS fichiers"

# --- 5. Copie sur le second stockage ---------------------------------------------------------
if [ "$COPIE" = 1 ]; then
  journal "4/5 Copie SFTP vers ${SAUVEGARDE_SFTP_UTILISATEUR}@${SAUVEGARDE_SFTP_HOTE}:${DOSSIER_SFTP}/"
  # Envoi sous un nom provisoire, puis renommage : jamais d'archive tronquée sous son vrai nom.
  sftp_lot <<<"-mkdir $DOSSIER_SFTP" >/dev/null 2>&1 || true   # le dossier existe déjà après la première fois
  sftp_lot <<EOF >/dev/null
put $ARCHIVE $DOSSIER_SFTP/$NOM.partiel
rename $DOSSIER_SFTP/$NOM.partiel $DOSSIER_SFTP/$NOM
EOF
  sftp_lot <<<"ls -l $DOSSIER_SFTP/$NOM" | grep -qw "$TAILLE" \
    || echouer "la copie distante n'a pas la taille attendue ($TAILLE octets)."
  journal "    copie vérifiée ($TAILLE octets)"
else
  journal "4/5 Copie SFTP : non demandée (--sans-copie). CETTE ARCHIVE N'EXISTE QUE SUR CETTE MACHINE."
fi

# --- 6. Ménage : archives de plus de $JOURS jours ----------------------------------------------
journal "5/5 Ménage (plus de $JOURS jours)"
LIMITE=$(date -u -d "$JOURS days ago" '+%Y-%m-%d_%H%M%S')
perimee() {  # nom d'archive → vrai si plus ancienne que la limite
  local date_archive
  date_archive=$(grep -oE "$MOTIF_DATE" <<<"$1" | head -n1)
  [ -n "$date_archive" ] && [[ "$date_archive" < "$LIMITE" ]]
}
for fichier in "$DOSSIER"/"${DB}"_*.tar.gz.gpg; do
  [ -e "$fichier" ] || continue
  if perimee "$(basename "$fichier")"; then
    rm -f "$fichier"
    journal "    supprimée ici : $(basename "$fichier")"
  fi
done
if [ "$COPIE" = 1 ]; then
  # Seulement après une copie réussie : il reste toujours au moins l'archive du jour.
  for nom in $(sftp_lister); do
    if perimee "$nom"; then
      sftp_lot <<<"rm $DOSSIER_SFTP/$nom" >/dev/null
      journal "    supprimée sur le second stockage : $nom"
    fi
  done
  journal "Sauvegarde terminée : $(ls "$DOSSIER"/"${DB}"_*.tar.gz.gpg 2>/dev/null | wc -l) archive(s) ici, $(sftp_lister | wc -l) sur le second stockage."
else
  journal "Sauvegarde locale terminée : $ARCHIVE"
fi
