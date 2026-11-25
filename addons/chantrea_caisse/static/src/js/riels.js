// Calculs en riels de la caisse, sans dépendance à Odoo (testés par tests/riels.test.mjs avec Node).
// Même règle d'arrondi que models/pos_config.py : arrondir_riels.

const EPS = 1e-6;

/** Arrondit au pas des billets : « haut » pour ce que le client paie, « proche » pour la monnaie rendue. */
export function arrondirRiels(montant, pas = 100, sens = "proche") {
    pas = pas || 1;
    if (sens === "haut") {
        return Math.ceil(Math.round((montant / pas) * 1e6) / 1e6) * pas;
    }
    return Math.floor(montant / pas + 0.5) * pas;
}

/** Montant en dollars à payer en riels : arrondi au billet supérieur (la caisse n'y perd jamais). */
export function aPayerEnRiels(usd, taux, pas = 100) {
    if (!taux || usd <= 0) {
        return 0;
    }
    return arrondirRiels(usd * taux, pas, "haut");
}

/** Valeur en dollars (au centime) d'un montant en riels. */
export function valeurEnDollars(khr, taux) {
    if (!taux || !khr) {
        return 0;
    }
    return Math.round((khr / taux) * 100) / 100;
}

/** Dollars + riels remis par le client → montant en dollars de la ligne de paiement. */
export function montantRecu(usd, khr, taux) {
    return Math.round(((usd || 0) + valeurEnDollars(khr, taux)) * 100) / 100;
}

/**
 * Monnaie à rendre, en dollars et en riels.
 * - « mixte » : les dollars entiers en billets, les centimes en riels (pas de pièces de dollar au Cambodge) ;
 * - « riels » : tout en riels ;
 * - « dollars » : tout en dollars.
 * Les riels sont arrondis au billet le plus proche.
 */
export function renduMonnaie(changeUsd, taux, pas = 100, mode = "mixte") {
    if (!changeUsd || changeUsd <= 0) {
        return { usd: 0, khr: 0 };
    }
    if (mode === "dollars" || !taux) {
        return { usd: Math.round(changeUsd * 100) / 100, khr: 0 };
    }
    if (mode === "riels") {
        return { usd: 0, khr: arrondirRiels(changeUsd * taux, pas) };
    }
    const dollars = Math.floor(changeUsd + EPS);
    const reste = Math.max(changeUsd - dollars, 0);
    return { usd: dollars, khr: arrondirRiels(reste * taux, pas) };
}
