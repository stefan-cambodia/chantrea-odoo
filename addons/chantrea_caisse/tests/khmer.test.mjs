// Tests du ticket khmer/anglais (chiffres, dates, montants), lancés par scripts/tests.sh.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

// Même chargement que riels.test.mjs (Node 18 de l'image Odoo).
const source = readFileSync(new URL("../static/src/js/khmer.js", import.meta.url), "utf8");
const {
    MOIS_KM, chiffresKhmers, dateKhmere, dateHeureKhmere, dateHeureAnglaise, nombreAnglais, montantAnglais,
    quantiteAnglaise, ligneKhmere,
} =
    await import("data:text/javascript," + encodeURIComponent(source));

const MOMENT = { jour: 26, mois: 11, annee: 2026, heure: 5, minute: 35 };

test("mois identiques à ceux des documents imprimés (outils_km.py)", () => {
    const python = readFileSync(new URL("../../chantrea_base/outils_km.py", import.meta.url), "utf8");
    const bloc = python.match(/MOIS = \(([^)]*)\)/)[1];
    assert.deepEqual([...bloc.matchAll(/"([^"]+)"/g)].map((m) => m[1]), MOIS_KM);
    assert.equal(MOIS_KM.length, 12);
});

test("chiffres khmers", () => {
    assert.equal(chiffresKhmers("0123456789"), "០១២៣៤៥៦៧៨៩");
    assert.equal(chiffresKhmers("$ 1,234.50"), "$ ១,២៣៤.៥០");
    assert.equal(chiffresKhmers(null), "");
});

test("date et heure en khmer et à l'anglaise", () => {
    assert.equal(dateKhmere(MOMENT), "ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦");
    assert.equal(dateHeureKhmere(MOMENT), "ថ្ងៃទី២៦ ខែវិច្ឆិកា ឆ្នាំ២០២៦ ម៉ោង ០៥:៣៥");
    assert.equal(dateKhmere({ jour: 1, mois: 1, annee: 2027 }), "ថ្ងៃទី០១ ខែមករា ឆ្នាំ២០២៧");
    assert.equal(dateHeureAnglaise(MOMENT), "26/11/2026 05:35");
});

test("nombres à l'anglaise, quelle que soit la langue de la caissière", () => {
    assert.equal(nombreAnglais(7.43), "7.43");
    assert.equal(nombreAnglais(1234.5), "1,234.50");
    assert.equal(nombreAnglais(30200, 0), "30,200");
    assert.equal(nombreAnglais(1234567.891), "1,234,567.89");
    assert.equal(nombreAnglais(-2.6), "-2.60");
    assert.equal(nombreAnglais(-0.001), "0.00");
    assert.equal(nombreAnglais(0.1 + 0.2), "0.30");
});

test("montants avec le symbole de la devise", () => {
    const usd = { symbol: "$", position: "before", decimal_places: 2 };
    const khr = { symbol: "៛", position: "after", decimal_places: 0 };
    assert.equal(montantAnglais(7.43, usd), "$ 7.43");
    assert.equal(montantAnglais(48100, khr), "48,100 ៛");
    assert.equal(montantAnglais(5, null), "5.00");
});

test("lignes de produits du ticket en chiffres khmers", () => {
    const usd = { symbol: "$", position: "before", decimal_places: 2 };
    assert.equal(quantiteAnglaise(2), "2");
    assert.equal(quantiteAnglaise(1.5), "1.5");
    assert.equal(quantiteAnglaise(1234), "1,234");
    assert.equal(quantiteAnglaise(0.1 + 0.2), "0.3");
    assert.deepEqual(ligneKhmere(1, 3.58, usd), { quantite: "១", montant: "$\u00a0៣.៥៨" });
    assert.deepEqual(ligneKhmere(2, 7.15, usd), { quantite: "២", montant: "$\u00a0៧.១៥" });
    assert.deepEqual(ligneKhmere(-1, -3.58, usd), { quantite: "-១", montant: "$\u00a0-៣.៥៨" });
});
