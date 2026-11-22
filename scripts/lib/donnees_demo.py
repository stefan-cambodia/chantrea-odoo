# Données de DÉMONSTRATION, pour le poste local uniquement (jamais sur le serveur).
# Exécuté par scripts/donnees_demo.sh dans « odoo shell ». Peut être relancé :
# les enregistrements déjà créés sont réutilisés.
# Tous les noms contiennent « DÉMO » ; les numéros de TVA sont visiblement fictifs.
import os

from odoo import fields

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

# --- Espace client : un accès par client de démo, un ticket chacun -------------
mdp_client = os.environ.get("DEMO_CLIENT_PASSWORD")
if not mdp_client:
    raise SystemExit("DEMO_CLIENT_PASSWORD manquant dans .env")
portail = env.ref("base.group_portal")
acces = []
for societe, nom, courriel, langue, sujet, categorie in [
    (hotel, "Dara (DÉMO)", "dara@demo.example", "km_KH", "Imprimante de la réception en panne (DÉMO)",
     "chantrea_portail.categorie_materiel"),
    (cafe, "Sophea (DÉMO)", "sophea@demo.example", "en_US", "Wi-Fi des clients très lent (DÉMO)",
     "chantrea_portail.categorie_reseau"),
]:
    contact = trouver_ou_creer("res.partner", [("email", "=", courriel)], {
        "name": nom, "parent_id": societe.id, "email": courriel, "lang": langue})
    utilisateur = env["res.users"].with_context(active_test=False).search([("login", "=", courriel)])
    if not utilisateur:
        utilisateur = env["res.users"].with_context(no_reset_password=True).create({
            "name": nom, "login": courriel, "partner_id": contact.id,
            "group_ids": [(6, 0, portail.ids)]})
    utilisateur.password = mdp_client
    trouver_ou_creer("helpdesk.ticket", [("name", "=", sujet)], {
        "name": sujet, "description": "<p>Ticket de démonstration.</p>", "partner_id": contact.id,
        "category_id": env.ref(categorie).id, "team_id": env.ref("chantrea_portail.equipe_assistance").id})
    acces.append((courriel, langue, societe.name))

# --- Contrat de maintenance mensuel (première facture créée en brouillon) -------
# Démarre le 16/11/2026 : le GDT a publié un taux ce jour-là, la facture peut donc
# être validée dans la démo sans saisir de taux.
Contrat = env["contract.contract"]
contrat = Contrat.search([("name", "=", "Maintenance mensuelle (DÉMO)")])
if not contrat:
    brouillon = Contrat.new({
        "name": "Maintenance mensuelle (DÉMO)", "partner_id": hotel.id,
        "contract_template_id": env.ref("chantrea_portail.modele_contrat_maintenance_mensuelle").id,
        "user_id": env.ref("base.user_admin").id})
    brouillon._onchange_contract_template_id()
    contrat = Contrat.create(brouillon._convert_to_write(brouillon._cache))
    contrat.contract_line_ids.write({"price_unit": 120.0, "date_start": "2026-11-16",
                                     "recurring_next_date": "2026-11-16"})
    Contrat.cron_recurring_create_invoice(date_ref=fields.Date.to_date("2026-11-16"))
facture_contrat = contrat._get_related_invoices()[:1]

# --- Parc matériel (garanties calculées par rapport à aujourd'hui) -------------
from datetime import timedelta  # noqa: E402

aujourd_hui = fields.Date.context_today(env["fsm.equipment"])
site_hotel = trouver_ou_creer("fsm.location", [("name", "=", "Riverside Guesthouse – réception (DÉMO)")], {
    "name": "Riverside Guesthouse – réception (DÉMO)", "owner_id": hotel.id})
for nom, client, site, categorie, marque, modele, serie, achat, fin in [
    ("Pare-feu de la réception (DÉMO)", hotel, site_hotel, "pare_feu", "Fortinet", "FortiGate 40F", "FGT40F-DEMO-001",
     aujourd_hui - timedelta(days=700), aujourd_hui + timedelta(days=400)),
    ("Onduleur de la baie (DÉMO)", hotel, site_hotel, "onduleur", "APC", "Smart-UPS 1500", "AS1500-DEMO-002",
     aujourd_hui - timedelta(days=1050), aujourd_hui + timedelta(days=45)),
    ("Borne Wi-Fi du jardin (DÉMO)", hotel, site_hotel, "wifi", "Ubiquiti", "U6 Mesh", "U6M-DEMO-003",
     aujourd_hui - timedelta(days=900), aujourd_hui - timedelta(days=170)),
    ("Poste de caisse (DÉMO)", cafe, False, "poste", "Lenovo", "ThinkCentre M70q", "M70Q-DEMO-004",
     aujourd_hui - timedelta(days=300), aujourd_hui + timedelta(days=760)),
]:
    trouver_ou_creer("fsm.equipment", [("name", "=", nom)], {
        "name": nom, "chantrea_client_id": client.id, "location_id": site.id if site else False,
        "chantrea_categorie": categorie, "chantrea_marque": marque, "chantrea_modele": modele,
        "chantrea_numero_serie": serie, "chantrea_date_achat": achat, "chantrea_fin_garantie": fin,
        "chantrea_contrat_id": contrat.id if client == hotel else False,
        "notes": "<p>Note interne de démonstration : jamais visible par le client.</p>"})
env["fsm.equipment"]._chantrea_cron_alertes_garantie()

# --- Intervention signée, créée depuis un ticket de l'hôtel ---------------------
import base64  # noqa: E402
import io  # noqa: E402
import math  # noqa: E402

from PIL import Image, ImageDraw  # noqa: E402

onduleur = env["fsm.equipment"].search([("name", "=", "Onduleur de la baie (DÉMO)")])
ticket_onduleur = trouver_ou_creer("helpdesk.ticket", [("name", "=", "L'onduleur bipe toutes les heures (DÉMO)")], {
    "name": "L'onduleur bipe toutes les heures (DÉMO)", "description": "<p>Bip régulier dans la baie.</p>",
    "partner_id": env["res.partner"].search([("email", "=", "dara@demo.example")]).id,
    "team_id": env.ref("chantrea_portail.equipe_assistance").id,
    "category_id": env.ref("chantrea_portail.categorie_materiel").id,
    "chantrea_equipement_ids": [(6, 0, onduleur.ids)]})
intervention = env["fsm.order"].search([("ticket_id", "=", ticket_onduleur.id)], limit=1)
if not intervention:
    contexte = ticket_onduleur.action_create_order()["context"]
    intervention = env["fsm.order"].with_context(**contexte).create({
        "location_id": site_hotel.id,
        "description": "<p>Diagnostic de l'onduleur qui bipe.</p>",
        "todo": "<p>Prévoir une batterie de rechange dans la camionnette.</p>",
        "resolution": "<p>Batterie usée remplacée ; test de coupure réussi (autonomie 12 min).</p>",
    })
    # Signature de démonstration : un simple tracé.
    image = Image.new("RGBA", (420, 120), (255, 255, 255, 0))
    dessin = ImageDraw.Draw(image)
    points = [(20 + x, 70 + 28 * math.sin(x / 22) * math.exp(-x / 400)) for x in range(0, 380, 4)]
    dessin.line(points, fill=(15, 20, 18, 255), width=4)
    tampon = io.BytesIO()
    image.save(tampon, format="PNG")
    env["fsm.order.sign.wizard"].create({
        "order_id": intervention.id, "signed_by": "Dara (DÉMO)",
        "signature": base64.b64encode(tampon.getvalue())}).action_sign()
    intervention.action_complete()

env.cr.commit()

# --- PDF -------------------------------------------------------------------
Rapport = env["ir.actions.report"]
for nom, rapport, docs in [
    ("facture_tva", "account.account_invoices", f_tva),
    ("facture_commerciale", "account.account_invoices", f_com),
    ("devis", "sale.action_report_saleorder", devis),
    ("facture_contrat_brouillon", "account.account_invoices", facture_contrat),
    ("rapport_intervention", "fieldservice.action_report_fsm_order", intervention),
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
print(f"Contrat « {contrat.name} » : facture {facture_contrat.state} du {facture_contrat.invoice_date}, "
      f"{facture_contrat.amount_total:.2f} USD, activité : {facture_contrat.activity_ids.summary}")
print("PDF écrits dans", SORTIE)
print(f"Intervention {intervention.name} : {intervention.stage_id.name}, signée par {intervention.signed_by}")
for courriel, langue, societe in acces:
    print(f"Accès client : {courriel} ({langue}, {societe}) — mot de passe : DEMO_CLIENT_PASSWORD de .env")
