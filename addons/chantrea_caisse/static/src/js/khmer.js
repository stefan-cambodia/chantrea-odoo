// Fonctions pures du ticket khmer/anglais, sans dépendance à Odoo (testées avec Node).
// Mêmes règles que les documents imprimés (chantrea_base/outils_km.py) :
// chiffres khmers U+17E0–17E9, mois du calendrier solaire, séparateurs anglais.

export const MOIS_KM = [
    "មករា", "កុម្ភៈ", "មីនា", "មេសា", "ឧសភា", "មិថុនា",
    "កក្កដា", "សីហា", "កញ្ញា", "តុលា", "វិច្ឆិកា", "ធ្នូ",
];

const CHIFFRES_KM = "០១២៣៤៥៦៧៨៩";

/** Remplace les chiffres occidentaux par des chiffres khmers (le reste est gardé). */
export function chiffresKhmers(texte) {
    return String(texte ?? "").replace(/[0-9]/g, (c) => CHIFFRES_KM[Number(c)]);
}

const deuxChiffres = (n) => String(n).padStart(2, "0");

/** {jour, mois, annee} → « ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦ ». */
export function dateKhmere({ jour, mois, annee }) {
    return `ថ្ងៃទី${chiffresKhmers(deuxChiffres(jour))} ខែ${MOIS_KM[mois - 1]} ឆ្នាំ${chiffresKhmers(annee)}`;
}

/** {jour, mois, annee, heure, minute} → « ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦ ម៉ោង ០៥:៣៥ ». */
export function dateHeureKhmere(moment) {
    const heure = `${deuxChiffres(moment.heure)}:${deuxChiffres(moment.minute)}`;
    return `${dateKhmere(moment)} ម៉ោង ${chiffresKhmers(heure)}`;
}

/** {jour, mois, annee, heure, minute} → « 26/11/2026 05:35 », comme la date anglaise des documents. */
export function dateHeureAnglaise(moment) {
    const date = `${deuxChiffres(moment.jour)}/${deuxChiffres(moment.mois)}/${moment.annee}`;
    return `${date} ${deuxChiffres(moment.heure)}:${deuxChiffres(moment.minute)}`;
}

/** Nombre écrit à l'anglaise : 1234.5 → « 1,234.50 » (2 décimales), 30200 → « 30,200 » (0). */
export function nombreAnglais(valeur, decimales = 2) {
    const n = Number(valeur) || 0;
    const [entier, fraction] = Math.abs(n).toFixed(decimales).split(".");
    const groupe = entier.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    const signe = n < 0 && Number(Math.abs(n).toFixed(decimales)) !== 0 ? "-" : "";
    return signe + groupe + (fraction ? `.${fraction}` : "");
}

/**
 * Montant à l'anglaise avec le symbole de la devise ({symbol, position, decimal_places}) :
 * « $ 7.43 », « 30,200 ៛ » (espace insécable, comme Odoo).
 */
export function montantAnglais(valeur, devise) {
    const decimales = devise?.decimal_places ?? 2;
    const nombre = nombreAnglais(valeur, decimales);
    if (!devise?.symbol) {
        return nombre;
    }
    return devise.position === "after" ? `${nombre} ${devise.symbol}` : `${devise.symbol} ${nombre}`;
}

/** Quantité sans zéros inutiles, à l'anglaise : 2 → « 2 », 1.5 → « 1.5 », 1234 → « 1,234 ». */
export function quantiteAnglaise(quantite) {
    const arrondie = Math.round((Number(quantite) || 0) * 1000) / 1000;
    const decimales = (String(arrondie).split(".")[1] || "").length;
    return nombreAnglais(arrondie, decimales);
}

/**
 * Ligne de produit du ticket en chiffres khmers, sous la ligne habituelle et comme elle :
 * quantité à gauche, montant à droite ({quantite: "២", montant: "$ ៧.១៥"}). Pas de
 * « quantité × prix » : Odoo arrondit le prix unitaire affiché, le calcul paraîtrait faux.
 */
export function ligneKhmere(quantite, montant, devise) {
    return {
        quantite: chiffresKhmers(quantiteAnglaise(quantite)),
        montant: chiffresKhmers(montantAnglais(montant, devise)),
    };
}
