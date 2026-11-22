#!/usr/bin/env bash
# Restaure une archive produite par scripts/sauvegarde.sh : base PostgreSQL et fichiers
# d'Odoo. L'archive est d'abord restaurée À CÔTÉ de la base en service, puis VÉRIFIÉE :
# mêmes chiffres que ceux notés au moment de la sauvegarde, chaque pièce jointe présente
# et intacte. La base en service n'est remplacée qu'après cette vérification, et
# l'ancienne est gardée sous un autre nom.
#
# Usage :
#   scripts/restauration.sh ARCHIVE            # restaure la base (refuse si elle existe déjà)
#   scripts/restauration.sh --dernier          # … la plus récente du dossier local
#   scripts/restauration.sh --depuis-sftp      # … la plus récente du second stockage (téléchargée)
#
# Options :
#   --essai       restaure dans une base provisoire, vérifie, puis la supprime.
#                 Ne touche PAS à la base en service : à lancer régulièrement.
#   --remplacer   autorise le remplacement d'une base existante (confirmation demandée) ;
#                 l'ancienne base est renommée « <base>_avant_restauration_<date> ».
#   --oui         ne pose aucune question (tâches automatiques)
#   --sans-neutraliser  voir ci-dessous
#
# Sauvegarde d'un AUTRE domaine (par exemple celle du serveur, restaurée sur votre poste) :
# la copie est « neutralisée » avant d'être mise en service — envois de courriels, relève
# des boîtes aux lettres et tâches planifiées désactivés — pour qu'elle n'agisse pas à la
# place du vrai serveur. --sans-neutraliser l'évite (déménagement vers un nouveau nom).
#
# La phrase secrète SAUVEGARDE_PHRASE doit être dans .env (celle du jour de la sauvegarde).
set -euo pipefail
export LC_COLLATE=C
cd "$(dirname "$0")/.."
. scripts/lib/commun_sauvegarde.sh

ESSAI=0; REMPLACER=0; OUI=0; NEUTRALISER=1; NEUTRALISEE=0; SOURCE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --essai) ESSAI=1 ;;
    --remplacer) REMPLACER=1 ;;
    --oui) OUI=1 ;;
    --sans-neutraliser) NEUTRALISER=0 ;;
    --dernier|--depuis-sftp) SOURCE="$1" ;;
    -h|--help) sed -n '2,26p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "Option inconnue : $1 (voir scripts/restauration.sh --help)"; exit 2 ;;
    *) SOURCE="$1" ;;
  esac
  shift
done
[ -n "$SOURCE" ] || { echo "Indiquez une archive, --dernier ou --depuis-sftp (voir --help)."; exit 2; }

charger_env
exiger docker gpg tar gzip
exiger_phrase

TRAVAIL=$(mktemp -d -p "$DOSSIER" .restauration.XXXXXX)
JOURNAL="$TRAVAIL/journal.txt"
exec > >(tee -a "$JOURNAL") 2>&1
# Base provisoire : la restauration et la vérification s'y font, à côté de la base en service.
if [ "$ESSAI" = 1 ]; then PROVISOIRE="${DB}_essai_restauration"; else PROVISOIRE="${DB}_restauration_en_cours"; fi
PROVISOIRE_CREEE=0

supprimer_base() {  # base PostgreSQL et dossier de fichiers
  psql_db -d postgres -qc "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$1'" >/dev/null
  docker compose exec -T db dropdb -U "$UTILISATEUR_PG" --if-exists "$1"
  dans_odoo odoo rm -rf "/var/lib/odoo/filestore/$1"
}

renommer_base() {  # ancien nom, nouveau nom
  psql_db -d postgres -qc "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='$1'" >/dev/null
  psql_db -d postgres -qc "ALTER DATABASE \"$1\" RENAME TO \"$2\""
  dans_odoo odoo bash -c 'cd /var/lib/odoo/filestore && rm -rf "$2" && { [ ! -d "$1" ] || mv "$1" "$2"; }' _ "$1" "$2"
}

fin() {
  local code=$?
  if [ "$code" -ne 0 ]; then
    journal "ÉCHEC de la restauration (code $code). La base en service n'a pas été modifiée."
    if [ "$ESSAI" = 1 ]; then
      { echo "L'essai de restauration de la base « $DB » (${DOMAINE:-?}) a échoué le $(date '+%d/%m/%Y à %H:%M')."
        echo "Les sauvegardes ne sont peut-être pas utilisables : à vérifier sans attendre. Fin du journal :"
        echo
        tail -n 40 "$JOURNAL" 2>/dev/null
      } | alerter "[Chantrea] ÉCHEC de l'essai de restauration de $DB" || true
    fi
  fi
  # Ne jamais laisser de base provisoire derrière soi.
  if [ "$PROVISOIRE_CREEE" = 1 ]; then supprimer_base "$PROVISOIRE" >/dev/null 2>&1 || true; fi
  rm -rf "$TRAVAIL"
  exit "$code"
}
trap fin EXIT

# --- 1. Choix de l'archive -----------------------------------------------------------
case "$SOURCE" in
  --dernier)
    ARCHIVE=$(ls "$DOSSIER"/"${DB}"_*.tar.gz.gpg 2>/dev/null | sort | tail -n1)
    [ -n "$ARCHIVE" ] || echouer "aucune archive de « $DB » dans $DOSSIER."
    ;;
  --depuis-sftp)
    exiger sftp
    exiger_sftp
    NOM=$(sftp_lister | tail -n1)
    [ -n "$NOM" ] || echouer "aucune archive de « $DB » sur le second stockage."
    ARCHIVE="$TRAVAIL/$NOM"
    journal "Téléchargement de $NOM depuis ${SAUVEGARDE_SFTP_HOTE}"
    sftp_lot <<<"get $DOSSIER_SFTP/$NOM $ARCHIVE" >/dev/null
    ;;
  *)
    ARCHIVE="$SOURCE"
    [ -r "$ARCHIVE" ] || echouer "archive illisible : $ARCHIVE"
    ;;
esac
journal "Archive : $(basename "$ARCHIVE") ($(numfmt --to=iec "$(stat -c %s "$ARCHIVE")"))"

# --- 2. Garde-fous, avant tout travail -------------------------------------------------
attendre_db
if [ "$ESSAI" != 1 ] && base_existe "$DB"; then
  [ "$REMPLACER" = 1 ] \
    || echouer "la base « $DB » existe déjà. Pour essayer sans risque : --essai. Pour la remplacer : --remplacer."
  if [ "$OUI" != 1 ]; then
    echo
    echo "ATTENTION : la base « $DB » existe. Elle sera REMPLACÉE par la sauvegarde : ce qui a"
    echo "été saisi depuis cette sauvegarde ne sera plus dans la base en service."
    read -r -p "Pour confirmer, tapez le nom de la base : " reponse < /dev/tty
    [ "$reponse" = "$DB" ] || echouer "restauration annulée."
  fi
fi
if base_existe "$PROVISOIRE"; then
  journal "Reste d'une restauration précédente (« $PROVISOIRE ») : supprimé"
  supprimer_base "$PROVISOIRE"
fi

# --- 3. Déchiffrement -------------------------------------------------------------------
journal "1/5 Déchiffrement"
dechiffrer "$ARCHIVE" | tar -C "$TRAVAIL" -xzf - \
  || echouer "déchiffrement impossible : mauvaise phrase secrète (SAUVEGARDE_PHRASE) ou archive abîmée."
for attendu in MANIFESTE.txt base.dump filestore.tar; do
  [ -s "$TRAVAIL/$attendu" ] || echouer "archive incomplète : $attendu absent."
done
COMMIT=$(grep '^commit=' "$TRAVAIL/MANIFESTE.txt" | cut -d= -f2)
journal "    sauvegarde du $(grep '^date_utc=' "$TRAVAIL/MANIFESTE.txt" | cut -d= -f2) UTC, code ${COMMIT:0:8}"

# --- 4. Restauration dans la base provisoire -----------------------------------------------
journal "2/5 Base de données, dans « $PROVISOIRE » (pg_restore)"
docker compose exec -T db createdb -U "$UTILISATEUR_PG" -O "$UTILISATEUR_PG" "$PROVISOIRE"
PROVISOIRE_CREEE=1
docker compose exec -T db pg_restore -U "$UTILISATEUR_PG" -d "$PROVISOIRE" --no-owner --role="$UTILISATEUR_PG" --exit-on-error \
  < "$TRAVAIL/base.dump"

journal "3/5 Fichiers d'Odoo (filestore)"
dans_odoo odoo bash -c 'rm -rf "/var/lib/odoo/filestore/$1" && mkdir -p "/var/lib/odoo/filestore/$1" && tar -C "/var/lib/odoo/filestore/$1" -xf -' _ "$PROVISOIRE" \
  < "$TRAVAIL/filestore.tar" 2>>"$JOURNAL"

# --- 5. Vérification ---------------------------------------------------------------------------
journal "4/5 Vérification"
sed -n '/^\[chiffres\]$/,/^\[sous-modules\]$/p' "$TRAVAIL/MANIFESTE.txt" | grep '=' | sort > "$TRAVAIL/chiffres_sauvegarde.txt"
chiffres_de_controle "$PROVISOIRE" | sort > "$TRAVAIL/chiffres_restaures.txt"
[ -s "$TRAVAIL/chiffres_sauvegarde.txt" ] || echouer "manifeste sans chiffres de contrôle."
if ! diff "$TRAVAIL/chiffres_sauvegarde.txt" "$TRAVAIL/chiffres_restaures.txt" >/dev/null; then
  diff "$TRAVAIL/chiffres_sauvegarde.txt" "$TRAVAIL/chiffres_restaures.txt" || true
  echouer "les chiffres de la base restaurée diffèrent de ceux de la sauvegarde."
fi
journal "    chiffres identiques à ceux de la sauvegarde : $(tr '\n' ' ' < "$TRAVAIL/chiffres_restaures.txt")"

# Chaque pièce jointe : fichier présent et contenu intact (Odoo nomme un fichier par
# l'empreinte SHA-1 de son contenu).
psql_db -d "$PROVISOIRE" -tAc "SELECT DISTINCT store_fname FROM ir_attachment WHERE store_fname IS NOT NULL ORDER BY 1" \
  > "$TRAVAIL/fichiers_attendus.txt"
ANOMALIES=$(dans_odoo odoo bash -c '
cd "/var/lib/odoo/filestore/$1" || exit 1
while IFS= read -r fichier; do
  [ -n "$fichier" ] || continue
  if [ ! -f "$fichier" ]; then echo "ABSENT $fichier"
  elif [ "$(sha1sum < "$fichier" | cut -d" " -f1)" != "${fichier##*/}" ]; then echo "ALTERE $fichier"
  fi
done' _ "$PROVISOIRE" < "$TRAVAIL/fichiers_attendus.txt" 2>>"$JOURNAL")
if [ -n "$ANOMALIES" ]; then
  echo "$ANOMALIES" | head -n 20
  echouer "$(echo "$ANOMALIES" | wc -l) pièce(s) jointe(s) absente(s) ou altérée(s)."
fi
journal "    $(grep -c . "$TRAVAIL/fichiers_attendus.txt" || true) pièces jointes présentes et intactes"

# --- 6. Sauvegarde d'un autre domaine : copie neutralisée ------------------------------------------
ORIGINE=$(grep '^domaine=' "$TRAVAIL/MANIFESTE.txt" | cut -d= -f2)
if [ "$ESSAI" != 1 ] && [ "$NEUTRALISER" = 1 ] && [ -n "$ORIGINE" ] && [ "$ORIGINE" != "${DOMAINE:-}" ]; then
  journal "    cette sauvegarde vient de « $ORIGINE », cette installation est « ${DOMAINE:-} » :"
  journal "    la copie est NEUTRALISÉE (courriels, relève des boîtes et tâches planifiées désactivés)"
  docker compose run --rm -T odoo odoo neutralize -d "$PROVISOIRE" --log-level=warn >>"$JOURNAL" 2>&1 \
    || echouer "neutralisation impossible : la copie n'est pas mise en service."
  NEUTRALISEE=1
fi

# --- 7. Fin --------------------------------------------------------------------------------------
if [ "$ESSAI" = 1 ]; then
  journal "5/5 Suppression de la base d'essai"
  supprimer_base "$PROVISOIRE"
  PROVISOIRE_CREEE=0
  journal "ESSAI DE RESTAURATION RÉUSSI : l'archive $(basename "$ARCHIVE") est utilisable."
else
  journal "5/5 Mise en service de la base restaurée"
  docker compose stop odoo >/dev/null 2>&1 || true
  if base_existe "$DB"; then
    ANCIENNE="${DB}_avant_restauration_$(date -u '+%Y%m%d_%H%M%S')"
    renommer_base "$DB" "$ANCIENNE"
    journal "    ancienne base gardée sous le nom « $ANCIENNE »"
  fi
  renommer_base "$PROVISOIRE" "$DB"
  PROVISOIRE_CREEE=0
  docker compose up -d >/dev/null 2>&1
  journal "RESTAURATION TERMINÉE : base « $DB » restaurée et vérifiée, Odoo redémarré."
  journal "Code du jour de la sauvegarde : commit $COMMIT."
  journal "Si le code du serveur a changé depuis : scripts/mettre_a_jour.sh"
  if [ "$NEUTRALISEE" = 1 ]; then
    journal "Copie NEUTRALISÉE (sauvegarde de « $ORIGINE »). Pour une vraie remise en service sous un"
    journal "nouveau nom de domaine, relancer la restauration avec --sans-neutraliser."
  fi
  if [ -n "${ANCIENNE:-}" ]; then
    journal "Quand tout est contrôlé, supprimer l'ancienne base :"
    journal "  docker compose exec db dropdb -U $UTILISATEUR_PG $ANCIENNE"
    journal "  docker compose run --rm --no-deps odoo rm -rf /var/lib/odoo/filestore/$ANCIENNE"
  fi
fi
