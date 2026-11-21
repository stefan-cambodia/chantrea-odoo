# Données de DÉMONSTRATION, pour le poste local uniquement (jamais sur le serveur).
# Exécuté par scripts/donnees_demo.sh dans « odoo shell ». Peut être relancé :
# les enregistrements déjà créés sont réutilisés.
# Tous les noms contiennent « DÉMO » ; les numéros de TVA sont visiblement fictifs.
import base64
import os

SORTIE = "/sortie"
company = env.company


def trouver_ou_creer(modele, domaine, valeurs):
    existant = env[modele].search(domaine, limit=1)
    return existant or env[modele].create(valeurs)


# --- Clients ---------------------------------------------------------------
hotel = trouver_ou_creer("res.partner", [("name", "=", "Riverside Guesthouse (DÉMO)")], {
    "name": "Riverside Guesthouse (DÉMO)",
    "is_company": True,
    "street": "Rue de la rivière",
    "city": "Kampot",
    "country_id": env.ref("base.kh").id,
    "phone": "+855 00 000 000",
    "vat": "DEMO-000000001",
    "lang": "en_US",
})
cafe = trouver_ou_creer("res.partner", [("name", "=", "ហាងកាហ្វេ សាកល្បង (DÉMO)")], {
    "name": "ហាងកាហ្វេ សាកល្បង (DÉMO)",
    "is_company": True,
    "city": "Kampot",
    "country_id": env.ref("base.kh").id,
    "lang": "km_KH",
})

# --- Produits --------------------------------------------------------------
taxe_t = env["account.tax"].search([("name", "=", "10% M T"), ("company_id", "=", company.id)], limit=1)
taxe_nt = env["account.tax"].search([("name", "=", "10% M NT"), ("company_id", "=", company.id)], limit=1)
heure = env.ref("uom.product_uom_hour")


def produit(nom, prix, type_="service", uom=None):
    vals = {"name": nom, "list_price": prix, "type": type_, "taxes_id": [(6, 0, taxe_t.ids)]}
    if uom:
        vals["uom_id"] = uom.id
    return trouver_ou_creer("product.product", [("name", "=", nom)], vals)


maintenance = produit("Maintenance informatique (DÉMO)", 25.0, uom=heure)
wifi = produit("Installation point d'accès Wi-Fi (DÉMO)", 60.0)
onduleur = produit("Onduleur 1500 VA (DÉMO)", 180.0, type_="consu")


def facture(client, taxe, lignes, ref):
    existante = env["account.move"].search([("ref", "=", ref)], limit=1)
    if existante:
        return existante
    move = env["account.move"].create({
        "move_type": "out_invoice",
        "partner_id": client.id,
        "ref": ref,
        "invoice_line_ids": [
            (0, 0, {"product_id": p.id, "name": nom or p.name, "quantity": q,
                    "price_unit": p.list_price, "tax_ids": [(6, 0, taxe.ids)]})
            for p, nom, q in lignes
        ],
    })
    move.action_post()
    return move


f_tva = facture(hotel, taxe_t, [
    (maintenance, "Maintenance du réseau — novembre / ថែទាំបណ្ដាញ ខែវិច្ឆិកា", 6),
    (wifi, None, 2),
    (onduleur, "Onduleur 1500 VA pour la réception", 1),
], "DEMO-TVA-1")
f_com = facture(cafe, taxe_nt, [
    (maintenance, "Dépannage poste de caisse / ជួសជុលកុំព្យូទ័រគិតលុយ", 1.5),
    (wifi, None, 1),
], "DEMO-COM-1")

devis = env["sale.order"].search([("client_order_ref", "=", "DEMO-DEVIS-1")], limit=1)
if not devis:
    devis = env["sale.order"].create({
        "partner_id": hotel.id,
        "client_order_ref": "DEMO-DEVIS-1",
        "order_line": [
            (0, 0, {"product_id": wifi.id, "product_uom_qty": 4}),
            (0, 0, {"product_id": onduleur.id, "product_uom_qty": 2}),
            (0, 0, {"product_id": maintenance.id, "product_uom_qty": 10}),
        ],
    })

env.cr.commit()

# --- PDF -------------------------------------------------------------------
Rapport = env["ir.actions.report"]
for nom, rapport, docs in [
    ("facture_tva", "account.account_invoices", f_tva),
    ("facture_commerciale", "account.account_invoices", f_com),
    ("devis", "sale.action_report_saleorder", devis),
]:
    pdf, _type = Rapport._render_qweb_pdf(rapport, docs.ids)
    chemin = os.path.join(SORTIE, f"{nom}.pdf")
    with open(chemin, "wb") as fichier:
        fichier.write(pdf)
    os.chmod(chemin, 0o644)

for m in (f_tva | f_com):
    print(f"{m.name:12} {m.chantrea_type_facture:12} {m.amount_total:>9.2f} USD  "
          f"taux {m.chantrea_taux_khr:g} du {m.chantrea_taux_date} ({m.chantrea_taux_source})  "
          f"= {m.chantrea_total_khr:,.0f} KHR")
print(f"{devis.name:12} devis        {devis.amount_total:>9.2f} USD")
print("PDF écrits dans", SORTIE)
