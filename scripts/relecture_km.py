#!/usr/bin/env python3
"""Génère docs/RELECTURE_KM.md : tous les textes khmers visibles par les clients.

Sources :
- les paires de libellés des documents imprimés et des pages de l'espace client
  (<span class="km">…</span><span class="en">…</span>, et km-inline / en-inline) ;
- les fichiers de traduction addons/*/i18n/km.po (texte anglais → texte khmer).

Le statut de relecture est conservé dans docs/relecture-km-statut.json,
indexé par le texte khmer lui-même : {"km": {"<texte khmer>": "ok"}}.
Si un texte est corrigé, il redevient « à relire ».

Usage : python3 scripts/relecture_km.py
"""
import html
import json
import re
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "docs" / "RELECTURE_KM.md"
STATUT = RACINE / "docs" / "relecture-km-statut.json"

SPAN_KM = re.compile(r'<span class="km(?:-inline)?"[^>]*>(?P<km>[^<]+)</span>')
# Ce qui suit un libellé khmer : la traduction anglaise (texte, ou valeur dynamique),
# ou à défaut le texte qui suit directement (ex. « ទំព័រ / Page »).
SUITE_EN = re.compile(
    r'^[\s/(]*<span class="en(?:-inline)?"(?:[^>]*t-out="(?P<dyn>[^"]*)"[^>]*/>|[^>]*>(?P<en>[^<]*)</span>)'
    r'|^[\s/]*(?P<texte>[^<]+)')
KHMER = re.compile(r"[ក-៿]")


def nettoyer(texte):
    return re.sub(r"\s+", " ", html.unescape(texte)).strip()


def textes_des_gabarits():
    for fichier in sorted(RACINE.glob("addons/*/**/*.xml")):
        contenu = fichier.read_text(encoding="utf-8")
        for m in SPAN_KM.finditer(contenu):
            km = nettoyer(m.group("km"))
            if not KHMER.search(km):
                continue
            suite = SUITE_EN.match(contenu[m.end():m.end() + 300])
            if suite and suite.group("dyn"):
                en = f"(valeur variable : {suite.group('dyn')})"
            elif suite and suite.group("en") is not None:
                en = nettoyer(suite.group("en"))
            elif suite and suite.group("texte"):
                en = nettoyer(suite.group("texte")).strip(":( ")
            else:
                en = "?"
            yield km, en, fichier.relative_to(RACINE)


def textes_des_po():
    for fichier in sorted(RACINE.glob("addons/*/i18n/km.po")):
        contenu = fichier.read_text(encoding="utf-8")
        for bloc in contenu.split("\n\n")[1:]:
            msgid = re.search(r'^msgid ((?:".*"\n?)+)', bloc, flags=re.M)
            msgstr = re.search(r'^msgstr ((?:".*"\n?)+)', bloc, flags=re.M)
            if msgid and msgstr:
                en = "".join(re.findall(r'"(.*)"', msgid.group(1)))
                km = "".join(re.findall(r'"(.*)"', msgstr.group(1)))
                if KHMER.search(km):
                    yield texte_po(km), texte_po(en), fichier.relative_to(RACINE)


def texte_po(valeur):
    """Texte lisible d'une chaîne de .po (les courriels HTML sont réduits à leur texte)."""
    valeur = valeur.replace("\\n", " ").replace('\\"', '"')
    valeur = re.sub(r"<[^>]+>", " ", valeur)
    return nettoyer(valeur).replace("|", "/")


def main():
    statut = json.loads(STATUT.read_text(encoding="utf-8")) if STATUT.exists() else {"km": {}}
    relus = statut.setdefault("km", {})

    lignes, vus = [], {}
    for km, en, fichier in list(textes_des_gabarits()) + list(textes_des_po()):
        cle = (km, en)
        if cle in vus:
            vus[cle].add(str(fichier.parts[1]))
            continue
        vus[cle] = {str(fichier.parts[1])}
        lignes.append(cle)

    nb_relus = sum(1 for km, _ in lignes if relus.get(km) == "ok")
    sortie = [
        "# Textes khmers à relire par un locuteur natif",
        "",
        "Fichier généré par `python3 scripts/relecture_km.py`. Ne pas modifier à la main :",
        "corriger le texte khmer dans le module indiqué (gabarit XML ou `i18n/km.po`), puis",
        "noter le texte comme relu dans `docs/relecture-km-statut.json`",
        '(ex. `{ "km": { "វិក្កយបត្រអាករ": "ok" } }`) et relancer le script.',
        "",
        "Tous les textes ci-dessous ont été traduits par Claude depuis l'anglais.",
        "Sur les devis et factures, le khmer est imprimé au-dessus et l'anglais juste en dessous.",
        "",
        f"**{nb_relus} / {len(lignes)} textes relus.**",
        "",
        "| Statut | Khmer | Anglais | Module(s) |",
        "|---|---|---|---|",
    ]
    for km, en in lignes:
        etat = "✅ relu" if relus.get(km) == "ok" else "⏳ à relire"
        modules = ", ".join(sorted(vus[(km, en)]))
        sortie.append(f"| {etat} | {km} | {en} | {modules} |")
    SORTIE.write_text("\n".join(sortie) + "\n", encoding="utf-8")
    if not STATUT.exists():
        STATUT.write_text(json.dumps(statut, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} : {len(lignes)} textes, {nb_relus} relus.")


if __name__ == "__main__":
    main()
