#!/usr/bin/env python3
"""Se connecte à l'espace client avec chaque faux client de scripts/lib/essai_clients.py
et vérifie ce qu'il voit, comme un vrai navigateur (sans JavaScript).

Usage : essai_clients_verif.py http://127.0.0.1:8070 attendu.json rapport.json
Mot de passe : variable DEMO_CLIENT_PASSWORD.

Contrôles, pour chaque compte :
  - langue de la page (attribut lang) = langue du compte ;
  - chiffres du tableau de bord = ce qui a été créé pour SA société ;
  - chaque liste montre tous ses documents, et aucun devis en brouillon ;
  - ses propres pages s'ouvrent ; sa facture en brouillon est refusée ;
  - les pages des documents d'autres clients sont refusées ;
  - aucune page ne montre la marque d'un autre client, ni une note interne.
Puis les mêmes connexions et tableaux de bord, tous les comptes en même temps.
"""
import html as html_lib
import http.cookiejar
import json
import os
import random
import re
import statistics
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE, ATTENDU, RAPPORT = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3]
MDP = os.environ["DEMO_CLIENT_PASSWORD"]
CHIFFRES_KM = str.maketrans("០១២៣៤៥៦៧៨៩", "0123456789")
PREFIXE_LANGUE = re.compile(r"^/(km|fr|en|km_KH|fr_FR|en_US)(?=/)")
MARQUE = re.compile(r"\[E\d{3}\]")
NOTES_INTERNES = ("Note interne [E", "Instruction interne [E")

with open(ATTENDU, encoding="utf-8") as fichier:
    donnees = json.load(fichier)
clients = donnees["clients"]
b = donnees["bilan"]
print(f"Données : {b['clients']} clients, {b['comptes']} comptes, {b['factures']} factures et avoirs, "
      f"{b['tickets']} tickets, {b['equipements']} équipements, {b['contrats']} contrats "
      f"({b['factures_contrats_brouillon']} factures mensuelles en brouillon, {b['activites_validation']} activités).")
print(f"Créées en {b['duree_donnees']} s ; tâches du matin en {b['duree_taches']} s ; "
      f"PDF des {b['factures']} factures en {b['duree_pdf']} s ({b['octets_pdf'] // 1024} Ko).\n", flush=True)


class Politique(http.cookiejar.DefaultCookiePolicy):
    # Le serveur d'essai est joint en HTTP direct, sans Caddy : on renvoie quand même
    # le cookie de session marqué « secure ».
    def return_ok_secure(self, cookie, request):
        return True


class Navigateur:
    def __init__(self):
        self.ouvreur = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar(policy=Politique())))
        self.durees = []

    def get(self, chemin, donnees=None):
        corps = urllib.parse.urlencode(donnees).encode() if donnees else None
        debut = time.time()
        try:
            reponse = self.ouvreur.open(BASE + chemin if chemin.startswith("/") else chemin, corps, timeout=120)
            statut, url, texte = reponse.status, reponse.url, reponse.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as erreur:
            statut, url, texte = erreur.code, erreur.url, erreur.read().decode("utf-8", "replace")
        self.durees.append(time.time() - debut)
        return statut, urllib.parse.urlparse(url).path, texte

    def connecter(self, login):
        statut, chemin, page = self.get("/web/login")
        jeton = re.search(r'name="csrf_token" value="([^"]+)"', page)
        if statut != 200 or not jeton:
            return f"page de connexion illisible ({statut})"
        statut, chemin, page = self.get(chemin, {"login": login, "password": MDP, "csrf_token": jeton.group(1),
                                                  "redirect": "/my"})
        if statut != 200 or sans_langue(chemin) != "/my":
            return f"connexion refusée (arrivée sur {chemin}, {statut})"
        return None


def sans_langue(chemin):
    return PREFIXE_LANGUE.sub("", chemin)


def nombre(texte):
    chiffres = re.sub(r"[^0-9]", "", html_lib.unescape(texte).translate(CHIFFRES_KM))
    return int(chiffres) if chiffres else None


def tableau_de_bord(page):
    """Chiffres des cartes de l'accueil : {carte: nombre}, plus garanties et montant (en cents)."""
    lu = {}
    for morceau in page.split('data-chantrea-carte="')[1:]:
        carte, reste = morceau.split('"', 1)
        reste = reste.split("</a>", 1)[0]
        valeur = re.search(r'o_chantrea_nombre"[^>]*>(.*?)</div>', reste, re.S)
        lu[carte] = nombre(valeur.group(1)) if valeur else None
        if carte == "equipements":
            alerte = re.search(r'o_chantrea_alerte"[^>]*>(.*?)</div>', reste, re.S)
            # « … 60 jours : 2 » : le nombre après le deux-points (« ៖ » en khmer).
            lu["garanties"] = nombre(re.split(r"[:：៖]", re.sub(r"<[^>]+>", "", alerte.group(1)))[-1]) if alerte else 0
        if carte == "factures":
            montant = re.search(r'oe_currency_value"[^>]*>(.*?)</span>', reste, re.S)
            lu["montant"] = nombre(montant.group(1)) if montant else 0
    return lu


def comparer_tableau(attendu, page):
    lu = tableau_de_bord(page)
    a = attendu["tableau"]
    voulu = {"tickets": a["tickets"], "interventions": a["interventions"], "equipements": a["equipements"],
             "garanties": a["garanties"], "contrats": a["contrats"], "devis": a["devis"],
             "factures": a["factures"], "montant": round(a["montant"] * 100)}
    return [f"tableau de bord : {cle} = {lu.get(cle)}, attendu {valeur}"
            for cle, valeur in voulu.items() if lu.get(cle) != valeur]


def fuites(page, marque):
    autres = sorted(set(MARQUE.findall(page)) - {marque})
    defauts = [f"marque d'un autre client : {', '.join(autres)}"] if autres else []
    defauts += [f"note interne visible : « {n}… »" for n in NOTES_INTERNES if n in page]
    return defauts


def verifier_compte(client, compte, hasard):
    nav, defauts = Navigateur(), []
    erreur = nav.connecter(compte["login"])
    if erreur:
        return nav, [erreur]
    marque = client["marque"]

    statut, _chemin, page = nav.get("/my")
    langue = re.search(r'<html[^>]* lang="([^"]+)"', page)
    if not langue or langue.group(1) != compte["lang"]:
        defauts.append(f"langue {langue.group(1) if langue else '?'}, attendu {compte['lang']}")
    defauts += comparer_tableau(client, page) + fuites(page, marque)

    for liste, noms in client["listes"].items():
        statut, _chemin, page = nav.get(liste)
        if statut != 200:
            defauts.append(f"{liste} : erreur {statut}")
            continue
        texte = html_lib.unescape(page)
        defauts += [f"{liste} : « {n} » absent" for n in noms if n not in texte]
        defauts += [f"{liste} : devis en brouillon « {n} » visible" for n in client["invisibles"]
                    if re.search(rf">\s*{re.escape(n)}\s*<", texte)]
        defauts += [f"{liste} : {d}" for d in fuites(page, marque)]

    for modele, ids in client["details"].items():
        for ident in ids:
            statut, chemin, page = nav.get(modele % ident)
            if statut != 200 or sans_langue(chemin) != modele % ident:
                defauts.append(f"{modele % ident} : sa propre page ne s'ouvre pas ({statut}, {chemin})")
            defauts += [f"{modele % ident} : {d}" for d in fuites(page, marque)]

    for modele, ids in client["refuses"].items():
        for ident in ids:
            statut, chemin, page = nav.get(modele % ident)
            if statut == 200 and sans_langue(chemin) == modele % ident:
                defauts.append(f"{modele % ident} : facture en brouillon ouverte")

    # Documents de trois autres clients : chaque page doit être refusée.
    for autre in hasard.sample([c for c in clients if c is not client], 3):
        for modele, ids in autre["details"].items():
            for ident in ids[:1]:
                statut, chemin, page = nav.get(modele % ident)
                if statut == 200 and sans_langue(chemin) == modele % ident:
                    defauts.append(f"{modele % ident} : document de {autre['marque']} ouvert")
                elif statut >= 500:
                    defauts.append(f"{modele % ident} : erreur {statut} au lieu d'un refus")
                defauts += [f"{modele % ident} : {d}" for d in fuites(page, marque)]
    return nav, defauts


def tableau_seul(client, compte):
    nav = Navigateur()
    erreur = nav.connecter(compte["login"])
    if erreur:
        return nav, [erreur]
    statut, _chemin, page = nav.get("/my")
    defauts = [] if statut == 200 else [f"/my : erreur {statut}"]
    nav.get("/my/invoices")
    return nav, defauts + comparer_tableau(client, page)


def en_ms(durees):
    durees = sorted(durees)
    return {"pages": len(durees), "mediane_ms": round(statistics.median(durees) * 1000),
            "p95_ms": round(durees[int(len(durees) * 0.95) - 1] * 1000), "max_ms": round(durees[-1] * 1000)}


hasard = random.Random(7)
comptes = [(client, compte) for client in clients for compte in client["comptes"]]
resultats, durees = [], []
debut = time.time()
for client, compte in comptes:
    nav, defauts = verifier_compte(client, compte, hasard)
    durees += nav.durees
    resultats.append({"marque": client["marque"], "login": compte["login"], "profil": client["profil"],
                      "lang": compte["lang"], "pages": len(nav.durees), "defauts": defauts})
    print(f"  {client['marque']} {compte['login']:22} {compte['lang']:6} {len(nav.durees):3} pages  "
          + ("ok" if not defauts else f"{len(defauts)} DÉFAUT(S)"), flush=True)
    for defaut in defauts:
        print(f"        - {defaut}", flush=True)
seq = {"duree_s": round(time.time() - debut, 1), **en_ms(durees)}

# Tous les comptes en même temps (10 à la fois) : connexion, accueil, factures.
debut, durees_charge, defauts_charge = time.time(), [], []
with ThreadPoolExecutor(max_workers=10) as groupe:
    for (client, compte), (nav, defauts) in zip(comptes, groupe.map(lambda cc: tableau_seul(*cc), comptes)):
        durees_charge += nav.durees
        defauts_charge += [f"{compte['login']} : {d}" for d in defauts]
charge = {"duree_s": round(time.time() - debut, 1), **en_ms(durees_charge), "defauts": defauts_charge}

total = sum(len(r["defauts"]) for r in resultats) + len(defauts_charge)
with open(RAPPORT, "w", encoding="utf-8") as fichier:
    json.dump({"comptes": resultats, "sequentiel": seq, "simultane": charge, "defauts": total},
              fichier, ensure_ascii=False, indent=1)
print(f"\nUn compte après l'autre : {len(comptes)} comptes, {seq['pages']} pages en {seq['duree_s']} s "
      f"(médiane {seq['mediane_ms']} ms, 95 % sous {seq['p95_ms']} ms, la plus lente {seq['max_ms']} ms)")
print(f"Tous en même temps (10 à la fois) : {charge['pages']} pages en {charge['duree_s']} s "
      f"(médiane {charge['mediane_ms']} ms, la plus lente {charge['max_ms']} ms)")
for defaut in defauts_charge:
    print(f"  - {defaut}")
print("AUCUN DÉFAUT" if not total else f"{total} DÉFAUT(S)")
sys.exit(1 if total else 0)
