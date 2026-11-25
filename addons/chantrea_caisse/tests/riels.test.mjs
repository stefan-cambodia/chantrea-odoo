// Tests des calculs en riels de la caisse, lancés par scripts/tests.sh (Node de l'image Odoo).
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

// riels.js est un module ES servi par Odoo ; Node 18 (image Odoo) ne le lit pas comme tel
// depuis un fichier .js : on le charge par son texte.
const source = readFileSync(new URL("../static/src/js/riels.js", import.meta.url), "utf8");
const { arrondirRiels, aPayerEnRiels, valeurEnDollars, montantRecu, renduMonnaie } = await import(
    "data:text/javascript," + encodeURIComponent(source)
);

test("arrondi au billet de 100 riels", () => {
    assert.equal(arrondirRiels(50787.5, 100, "haut"), 50800);
    assert.equal(arrondirRiels(50800, 100, "haut"), 50800);
    assert.equal(arrondirRiels(50801, 100, "haut"), 50900);
    assert.equal(arrondirRiels(3049, 100), 3000);
    assert.equal(arrondirRiels(3050, 100), 3100);
    // Imprécision des nombres à virgule : 0.1 * 3 * 1000 vaut 300.00000000000006.
    assert.equal(arrondirRiels(0.1 * 3 * 1000, 100, "haut"), 300);
});

test("total à payer en riels, arrondi au billet supérieur", () => {
    assert.equal(aPayerEnRiels(12.5, 4000), 50000);
    assert.equal(aPayerEnRiels(12.5, 4063), 50800); // 50 787,5
    assert.equal(aPayerEnRiels(0, 4063), 0);
    assert.equal(aPayerEnRiels(12.5, 0), 0, "sans taux, rien n'est inventé");
});

test("riels remis convertis en dollars", () => {
    assert.equal(valeurEnDollars(50000, 4000), 12.5);
    assert.equal(valeurEnDollars(50800, 4063), 12.5); // 12,5031 → 12,50
    assert.equal(montantRecu(10, 10000, 4000), 12.5);
    assert.equal(montantRecu(0, 0, 4000), 0);
});

test("monnaie rendue : dollars entiers + centimes en riels", () => {
    assert.deepEqual(renduMonnaie(1.75, 4000), { usd: 1, khr: 3000 });
    assert.deepEqual(renduMonnaie(1.75, 4063), { usd: 1, khr: 3000 }); // 3 047 → 3 000
    assert.deepEqual(renduMonnaie(2, 4063), { usd: 2, khr: 0 });
    assert.deepEqual(renduMonnaie(0.01, 4063), { usd: 0, khr: 0 }); // 41 riels : rien à rendre
    assert.deepEqual(renduMonnaie(1.9999999, 4000), { usd: 2, khr: 0 });
});

test("monnaie rendue tout en riels ou tout en dollars", () => {
    assert.deepEqual(renduMonnaie(1.75, 4000, 100, "riels"), { usd: 0, khr: 7000 });
    assert.deepEqual(renduMonnaie(1.75, 4063, 100, "riels"), { usd: 0, khr: 7100 }); // 7 110
    assert.deepEqual(renduMonnaie(1.75, 4063, 100, "dollars"), { usd: 1.75, khr: 0 });
    assert.deepEqual(renduMonnaie(0, 4063), { usd: 0, khr: 0 });
});

test("arrondi de 500 riels si la caisse le demande", () => {
    assert.deepEqual(renduMonnaie(1.75, 4000, 500), { usd: 1, khr: 3000 });
    assert.equal(aPayerEnRiels(1.1, 4000, 500), 4500);
});
