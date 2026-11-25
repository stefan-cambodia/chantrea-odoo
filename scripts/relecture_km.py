#!/usr/bin/env python3
"""Génère docs/RELECTURE_KM.md : tous les textes khmers visibles par les clients.

Sources, dans l'ordre du fichier produit :
1. les paires de libellés des documents imprimés et des pages de l'espace client
   (<span class="km">…</span><span class="en">…</span>, et km-inline / en-inline) ;
2. les traductions des modules maison : addons/*/i18n/km.po ;
3. les traductions des textes d'Odoo et de l'OCA vus par les clients :
   addons/*/i18n_clients/km.po.
Les noms de pays (i18n_clients/km_pays.po) viennent du référentiel Unicode CLDR
et ne sont pas à relire.

Le statut de relecture est conservé dans docs/relecture-km-statut.json,
indexé par le texte khmer lui-même : {"km": {"<texte khmer>": "ok"}}.
Si un texte est corrigé, il redevient « à relire ».

Usage : python3 scripts/relecture_km.py
"""
import html
import itertools
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
        # Textes khmers écrits directement dans les données (ex. libellé bilingue
        # « English / ខ្មែរ » d'une ligne de contrat, recopié sur les factures).
        for m in CHAMP_DONNEES.finditer(contenu):
            valeur = nettoyer(m.group(1))
            if KHMER.search(valeur):
                en, _, km = valeur.partition(" / ")
                yield (km or valeur), (en if km else "(libellé bilingue)"), fichier.relative_to(RACINE)


CHAMP_DONNEES = re.compile(r'<field name="[^"]+">([^<]+)</field>')

MOIS_EN = ("January", "February", "March", "April", "May", "June", "July", "August",
           "September", "October", "November", "December")


def textes_des_dates():
    """Mots des dates et des heures écrites en khmer sur les documents (chantrea_base/outils_km.py)."""
    source = (RACINE / "addons/chantrea_base/outils_km.py").read_text(encoding="utf-8")
    mois = re.search(r"MOIS = \(([^)]*)\)", source).group(1)
    for km, en in zip(re.findall(r'"([^"]+)"', mois), MOIS_EN):
        yield f"ខែ{km}", f"(month of) {en}", "chantrea_base"
    yield "ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦", "26 November 2026 (date format)", "chantrea_base"
    yield "ម៉ោង ១៤:៣០", "at 14:30 (time format)", "chantrea_base"


def textes_des_po(motif):
    """Textes d'un ensemble de fichiers .po : (khmer, anglais, origine)."""
    for fichier in sorted(RACINE.glob(motif)):
        contenu = fichier.read_text(encoding="utf-8")
        for bloc in contenu.split("\n\n")[1:]:
            msgid = re.search(r'^msgid ((?:".*"\n?)+)', bloc, flags=re.M)
            msgstr = re.search(r'^msgstr ((?:".*"\n?)+)', bloc, flags=re.M)
            if msgid and msgstr:
                en = "".join(re.findall(r'"(.*)"', msgid.group(1)))
                km = "".join(re.findall(r'"(.*)"', msgstr.group(1)))
                if KHMER.search(km):
                    modules = re.findall(r"^#\. module: (\w+)", bloc, flags=re.M)
                    origine = ", ".join(dict.fromkeys(modules)) if "i18n_clients" in fichier.parts else fichier.parts[1]
                    yield texte_po(km), texte_po(en), origine


def texte_po(valeur):
    """Texte lisible d'une chaîne de .po (les courriels HTML sont réduits à leur texte)."""
    valeur = valeur.replace("\\n", " ").replace('\\"', '"')
    valeur = re.sub(r"<[^>]+>", " ", valeur)
    return nettoyer(valeur).replace("|", "/")


PARTIES = (
    ("1. Documents imprimés et pages Chantrea",
     "Libellés des devis, factures, rapports d'intervention, tickets de caisse et pages du parc matériel ; "
     "mois et format des dates écrites en khmer. "
     "À corriger dans le gabarit XML du module indiqué (les mois : `chantrea_base/outils_km.py`).",
     lambda: itertools.chain(
         ((km, en, fichier.parts[1]) for km, en, fichier in textes_des_gabarits()),
         textes_des_dates())),
    ("2. Modules Chantrea",
     "Catégories de tickets, courriels, accueil de l'espace client… "
     "À corriger dans `addons/<module>/i18n/km.po`.",
     lambda: textes_des_po("addons/*/i18n/km.po")),
    ("3. Textes d'Odoo et de l'OCA vus par les clients",
     "Pages standard de l'espace client, fenêtres et courriels d'Odoo et des modules OCA. "
     "À corriger dans `addons/chantrea_portail/i18n_clients/km.po` (la colonne indique le module d'origine).",
     lambda: textes_des_po("addons/*/i18n_clients/km.po")),
)


def main():
    statut = json.loads(STATUT.read_text(encoding="utf-8")) if STATUT.exists() else {"km": {}}
    relus = statut.setdefault("km", {})

    vus, parties = {}, []
    for titre, aide, source in PARTIES:
        lignes = []
        for km, en, origine in source():
            cle = (km, en)
            if cle in vus:
                vus[cle].update(origine.split(", "))
                continue
            vus[cle] = set(origine.split(", "))
            lignes.append(cle)
        parties.append((titre, aide, lignes))

    total = sum(len(lignes) for _titre, _aide, lignes in parties)
    nb_relus = sum(1 for _titre, _aide, lignes in parties for km, _en in lignes if relus.get(km) == "ok")
    sortie = [
        "# Textes khmers à relire par un locuteur natif",
        "",
        "Fichier généré par `python3 scripts/relecture_km.py`. Ne pas modifier à la main :",
        "corriger le texte khmer à l'endroit indiqué au début de chaque partie, puis",
        "noter le texte comme relu dans `docs/relecture-km-statut.json`",
        '(ex. `{ "km": { "វិក្កយបត្រអាករ": "ok" } }`) et relancer le script.',
        "",
        "Tous les textes ci-dessous ont été traduits par Claude depuis l'anglais.",
        "Sur les devis et factures, le khmer est imprimé au-dessus et l'anglais juste en dessous.",
        "Les noms de pays ne sont pas listés : ils viennent du référentiel Unicode CLDR",
        "(`addons/chantrea_portail/i18n_clients/km_pays.po`).",
        "",
        "Ordre conseillé : parties 1 et 2 d'abord (ce que chaque client voit sur ses documents",
        "et sur l'accueil), puis la partie 3.",
        "",
        f"**{nb_relus} / {total} textes relus.**",
    ]
    for titre, aide, lignes in parties:
        relus_ici = sum(1 for km, _en in lignes if relus.get(km) == "ok")
        sortie += ["", f"## {titre}", "", aide, "", f"{relus_ici} / {len(lignes)} textes relus.", "",
                   "| Statut | Khmer | Anglais | Module(s) |", "|---|---|---|---|"]
        for km, en in lignes:
            etat = "✅ relu" if relus.get(km) == "ok" else "⏳ à relire"
            sortie.append(f"| {etat} | {km} | {en} | {', '.join(sorted(vus[(km, en)]))} |")
    SORTIE.write_text("\n".join(sortie) + "\n", encoding="utf-8")
    if not STATUT.exists():
        STATUT.write_text(json.dumps(statut, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} : {total} textes, {nb_relus} relus.")
    for titre, _aide, lignes in parties:
        print(f"  {titre} : {len(lignes)}")


if __name__ == "__main__":
    main()
