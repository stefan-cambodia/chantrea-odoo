# Essai avec 500 faux clients — 26/11/2026

**Résultat : ESSAI RÉUSSI, aucun défaut.**

Commande : `scripts/essai_clients.sh 500` (commit `f329f06`), sur le poste local.
L'essai travaille sur une copie de la base locale (`chantrea_essai_clients`), servie par
un Odoo provisoire à 2 processus (comme le serveur prévu) et sans tâches planifiées.
La copie a été supprimée à la fin ; la base de travail n'a pas été touchée.

## Données créées

| | |
|---|---|
| Clients (sociétés) | 500, dont 184 avec deux comptes (un collègue) |
| Comptes de l'espace client | 684 : 289 en khmer, 265 en anglais, 130 en français |
| Factures et avoirs validés | 1 614 (929 restant à payer, 255 085,91 $ dus au total) |
| Devis envoyés / en brouillon | 523 / 523 |
| Tickets | 996, dont 739 ouverts |
| Équipements | 1 513, dont 573 avec une garantie qui finit dans les 60 jours |
| Contrats mensuels | 253 |
| Interventions ouvertes | 101 |

Profils de langues des 500 clients (la première langue est celle du compte, les textes sont
saisis dans chaque langue du profil) : khmer 176, anglais 99, anglais + khmer 76,
français + khmer 62, anglais + français 50, français 37.

Tout ce qui concerne un client porte sa marque (`[E001]` … `[E500]`), y compris ses notes
internes et les instructions internes des interventions.

## Ce qui a été vérifié, pour chacun des 684 comptes

Connexion à l'espace client comme un navigateur, puis :

1. **Langue** : la page est dans la langue du compte.
2. **Accueil** : chaque chiffre du tableau de bord (tickets ouverts, interventions ouvertes,
   équipements, garanties proches, contrats, devis à valider, factures à payer et montant dû)
   est exactement celui de SA société.
3. **Listes** (factures, tickets, matériel, contrats, devis, commandes, interventions) :
   tous ses documents y sont, et aucun devis en brouillon.
4. **Ses propres pages** : les 5 998 pages de documents des clients s'ouvrent pour chacun de
   leurs comptes ; les 144 factures en brouillon sont refusées.
5. **Pages des autres** : les documents de trois autres clients tirés au hasard (un de chaque
   sorte) sont refusés.
6. **Sur chaque page** : aucune marque d'un autre client, aucune note ni instruction interne.

Puis les 684 comptes à nouveau, dix à la fois : connexion, accueil (chiffres revérifiés), factures.

Le contrôle a été vérifié lui-même sur 40 clients : en remplaçant exprès dans la copie les
règles d'accès des tickets et du matériel par « tout voir », il signale aussitôt, pour chaque
compte, les chiffres faux et les marques des autres clients.

## Temps mesurés

| | |
|---|---|
| Pages de l'espace client, un compte après l'autre | 24 156 pages en 40 min ; médiane 73 ms, 95 % sous 147 ms, la plus lente 1,8 s |
| Les mêmes, dix comptes à la fois | 2 736 pages en 6 min ; médiane 1,2 s, 95 % sous 2,7 s, la plus lente 4,4 s |
| Tâches du matin (factures des 253 contrats + alertes de garantie) | 2 min 16 s |
| PDF des 1 614 factures (par lots de 100) | 12 min 13 s, environ 0,45 s par facture, 43 Mo |
| Création des données par le script d'essai | 33 min (ce n'est pas un temps d'Odoo en service) |

Avec 40 clients, la médiane des pages était de 83 ms : le volume ne ralentit pas l'espace client.
Ces temps sont ceux du poste local ; le serveur prévu (2 processeurs) sera sans doute un peu plus lent.

## Fichiers

- `rapport.json` : pour chaque compte, sa langue, son profil, le nombre de pages vues et les défauts (aucun).
- `attendu.json` : ce que chaque client devait voir (chiffres, documents, pages), tel que le script l'a créé.
- `factures-extrait.pdf` : 14 des 1 614 factures (clients E001 à E500), compressé pour le dépôt ;
  le rendu est identique, mais le texte khmer ne se copie plus correctement depuis cet extrait.
  Le PDF complet (43 Mo) n'est pas dans le dépôt : `scripts/essai_clients.sh 500` le refait
  dans `essai-clients/`.

Un premier lancement avait échoué pendant la création des données : le script tentait de
lettrer un avoir qu'Odoo avait déjà lettré lui-même avec sa facture. Corrigé dans `f329f06`.
