# Génère N faux clients dans une base d'ESSAI (jamais la base de travail : voir
# scripts/essai_clients.sh, qui la copie). Exécuté dans « odoo shell ».
#
# Chaque client a un profil de langues, des contacts avec accès à l'espace client,
# des factures (payées, en partie, à payer, avoirs), des devis, des commandes, des
# tickets, du matériel, parfois un contrat mensuel et une intervention. Tout ce qui
# le concerne porte sa marque « [E007] » : une page qui montre la marque d'un autre
# client est une fuite.
#
# Écrit dans /sortie/attendu.json ce que chaque client doit voir, pour
# scripts/lib/essai_clients_verif.py, et /sortie/factures.pdf (toutes ses factures).
import json
import os
import random
import time
from datetime import date, timedelta

from odoo import fields

NOMBRE = int(os.environ.get("ESSAI_NOMBRE", "40"))
SORTIE = "/sortie"
MDP = os.environ.get("DEMO_CLIENT_PASSWORD")
if not MDP:
    raise SystemExit("DEMO_CLIENT_PASSWORD manquant dans .env")
hasard = random.Random(int(os.environ.get("ESSAI_GRAINE", "40")))
company = env.company
kh = env.ref("base.kh")
portail = env.ref("base.group_portal")
equipe = env.ref("chantrea_portail.equipe_assistance")
aujourd_hui = fields.Date.context_today(env["res.partner"])
debut = time.time()

# Profils de langues : (clé, langues des textes, langue du compte du 1er contact, du 2e).
PROFILS = (
    [("km", ("km",), "km_KH", "km_KH")] * 14
    + [("en", ("en",), "en_US", "en_US")] * 8
    + [("fr", ("fr",), "fr_FR", "fr_FR")] * 3
    + [("fr_km", ("fr", "km"), "fr_FR", "km_KH")] * 5
    + [("en_km", ("en", "km"), "en_US", "km_KH")] * 6
    + [("en_fr", ("en", "fr"), "en_US", "fr_FR")] * 4
)
hasard.shuffle(PROFILS)

ACTIVITES = [
    {"fr": "Hôtel", "en": "Hotel", "km": "សណ្ឋាគារ"},
    {"fr": "Restaurant", "en": "Restaurant", "km": "ភោជនីយដ្ឋាន"},
    {"fr": "Pharmacie", "en": "Pharmacy", "km": "ឱសថស្ថាន"},
    {"fr": "École", "en": "School", "km": "សាលារៀន"},
    {"fr": "Café", "en": "Café", "km": "ហាងកាហ្វេ"},
    {"fr": "Garage", "en": "Garage", "km": "យានដ្ឋាន"},
    {"fr": "Clinique", "en": "Clinic", "km": "គ្លីនិក"},
    {"fr": "Agence de voyages", "en": "Travel agency", "km": "ទីភ្នាក់ងារទេសចរណ៍"},
    {"fr": "Cabinet d'avocats", "en": "Law office", "km": "ការិយាល័យមេធាវី"},
    {"fr": "Maison d'hôtes", "en": "Guesthouse", "km": "ផ្ទះសំណាក់"},
]
NOMS = [
    {"fr": "Mékong", "en": "Mekong", "km": "មេគង្គ"}, {"fr": "Bokor", "en": "Bokor", "km": "បូកគោ"},
    {"fr": "Kep", "en": "Kep", "km": "កែប"}, {"fr": "Teuk Chhou", "en": "Teuk Chhou", "km": "ទឹកឈូ"},
    {"fr": "Durian", "en": "Durian", "km": "ធូរេន"}, {"fr": "Lotus", "en": "Lotus", "km": "ឈូក"},
    {"fr": "Sovann", "en": "Sovann", "km": "សុវណ្ណ"}, {"fr": "Poivre", "en": "Pepper", "km": "ម្រេច"},
    {"fr": "Soleil", "en": "Sunrise", "km": "ថ្ងៃរះ"}, {"fr": "Rivière", "en": "River", "km": "ទន្លេ"},
]
RUES = {"fr": "Rue {n}", "en": "Street {n}", "km": "ផ្លូវលេខ {n}"}
CONTACTS = {
    "km": ["សុខ ដារ៉ា", "ចាន់ ស្រីមុំ", "គីម សុភាព", "ហេង វុទ្ធី", "លឹម បុប្ផា", "មាស រដ្ឋា", "អ៊ុក ចន្ណា", "ប្រាក់ សុខា"],
    "en": ["Emma Clarke", "James Wilson", "Sarah Johnson", "Daniel Brown", "Srey Leak", "Vanna Ly"],
    "fr": ["Marie Dubois", "Thomas Bernard", "Lucas Martin", "Claire Petit", "Julien Moreau"],
}
TEXTES = {  # désignations des lignes, des tickets et du matériel
    "maint": {"fr": "Maintenance informatique (heures)", "en": "IT maintenance (hours)", "km": "ការថែទាំកុំព្យូទ័រ (ម៉ោង)"},
    "wifi": {"fr": "Installation d'un point d'accès Wi-Fi", "en": "Wi-Fi access point installation",
             "km": "ការដំឡើងចំណុចចូលប្រើវ៉ាយហ្វាយ"},
    "onduleur": {"fr": "Onduleur 1500 VA", "en": "1500 VA UPS", "km": "ឧបករណ៍ថាមពលបម្រុង UPS"},
    "licence": {"fr": "Licence antivirus, un an", "en": "Antivirus licence, one year", "km": "អាជ្ញាប័ណ្ណកំចាត់មេរោគ មួយឆ្នាំ"},
    "ssd": {"fr": "Disque SSD 1 To, posé", "en": "1 TB SSD, fitted", "km": "ថាស SSD ១ TB ដំឡើងរួច"},
    "t_imprimante": {"fr": "L'imprimante ne répond plus", "en": "Printer not responding", "km": "ម៉ាស៊ីនបោះពុម្ពលែងដំណើរការ"},
    "t_wifi": {"fr": "Wi-Fi très lent", "en": "Very slow Wi-Fi", "km": "វ៉ាយហ្វាយយឺតខ្លាំង"},
    "t_courriel": {"fr": "Courriels bloqués", "en": "Emails stuck", "km": "អ៊ីមែលជាប់គាំង"},
    "t_virus": {"fr": "Message de virus sur un poste", "en": "Virus warning on a computer", "km": "សារមេរោគលើកុំព្យូទ័រ"},
    "t_sauvegarde": {"fr": "Sauvegarde en échec", "en": "Backup failed", "km": "ការបម្រុងទុកបរាជ័យ"},
    "e_poste": {"fr": "Poste de l'accueil", "en": "Front desk computer", "km": "កុំព្យូទ័រកន្លែងទទួលភ្ញៀវ"},
    "e_wifi": {"fr": "Borne Wi-Fi", "en": "Wi-Fi access point", "km": "ចំណុចវ៉ាយហ្វាយ"},
    "e_onduleur": {"fr": "Onduleur de la baie", "en": "Rack UPS", "km": "UPS ក្នុងទូ"},
    "e_pare_feu": {"fr": "Pare-feu", "en": "Firewall", "km": "ជញ្ជាំងភ្លើង"},
    "e_stockage": {"fr": "Serveur de fichiers", "en": "File server", "km": "ម៉ាស៊ីនមេឯកសារ"},
    "e_switch": {"fr": "Commutateur réseau", "en": "Network switch", "km": "ឧបករណ៍ប្ដូរបណ្ដាញ"},
}
CATEGORIES_TICKET = {"t_imprimante": "materiel", "t_wifi": "reseau", "t_courriel": "messagerie",
                     "t_virus": "securite", "t_sauvegarde": "sauvegarde"}
EQUIPEMENTS = {"e_poste": ("poste", "Dell", "OptiPlex 7010"), "e_wifi": ("wifi", "Ubiquiti", "U6 Lite"),
               "e_onduleur": ("onduleur", "APC", "Smart-UPS 1500"), "e_pare_feu": ("pare_feu", "Fortinet", "FortiGate 40F"),
               "e_stockage": ("stockage", "Synology", "DS224+"), "e_switch": ("switch", "TP-Link", "TL-SG108")}


def texte(langues, code, valeurs=None):
    return " / ".join(TEXTES[code][l] if valeurs is None else valeurs[l] for l in langues)


# --- Produits et taxes ----------------------------------------------------------
taxe_t = env["account.tax"].search([("name", "=", "10% M T"), ("company_id", "=", company.id)], limit=1)
taxe_nt = env["account.tax"].search([("name", "=", "10% M NT"), ("company_id", "=", company.id)], limit=1)
heure = env.ref("uom.product_uom_hour")
PRODUITS = {}
for code, prix, uom in [("maint", 25.0, heure), ("wifi", 60.0, None), ("onduleur", 180.0, None),
                        ("licence", 35.0, None), ("ssd", 85.0, None)]:
    nom = TEXTES[code]["fr"] + " (ESSAI)"
    produit = env["product.product"].search([("name", "=", nom)], limit=1)
    if not produit:
        vals = {"name": nom, "list_price": prix, "type": "service", "taxes_id": [(6, 0, taxe_t.ids)]}
        if uom:
            vals["uom_id"] = uom.id
        produit = env["product.product"].create(vals)
    PRODUITS[code] = produit
Contrat = env["contract.contract"]
modele_contrat = env.ref("chantrea_portail.modele_contrat_maintenance_mensuelle")
etape_fermee = env["helpdesk.ticket.stage"].search([("closed", "=", True)], order="sequence", limit=1)
JOURS_FACTURE = [date(2026, 11, j) for j in range(2, 27)]


def lignes(langues, marque, taxe, n):
    resultat = []
    for code in hasard.sample(list(PRODUITS), n):
        quantite = hasard.choice([1, 2, 3]) if code != "maint" else hasard.choice([1, 1.5, 2, 4])
        resultat.append((0, 0, {"product_id": PRODUITS[code].id, "name": f"{texte(langues, code)} {marque}",
                                "quantity": quantite, "price_unit": PRODUITS[code].list_price,
                                "tax_ids": [(6, 0, taxe.ids)]}))
    return resultat


def payer(facture, montant=None):
    valeurs = {"amount": montant} if montant else {}
    env["account.payment.register"].with_context(
        active_model="account.move", active_ids=facture.ids).create(valeurs).action_create_payments()


attendus = []
toutes_factures = env["account.move"]
contrats_crees = Contrat
for i in range(1, NOMBRE + 1):
    marque = f"[E{i:03d}]"
    cle, langues, langue_1, langue_2 = PROFILS[(i - 1) % len(PROFILS)]
    if env["res.partner"].search_count([("name", "like", marque)]):
        raise SystemExit(f"La base contient déjà {marque} : ce script ne se relance pas sur la même base.")
    activite, nom = ACTIVITES[i % len(ACTIVITES)], NOMS[(i * 7) % len(NOMS)]
    noms = {"fr": f"{activite['fr']} {nom['fr']}", "en": f"{nom['en']} {activite['en']}",
            "km": f"{activite['km']}{nom['km']}"}
    avec_tva = hasard.random() < 0.5
    taxe = taxe_t if avec_tva else taxe_nt
    societe = env["res.partner"].create({
        "name": f"{texte(langues, None, noms)} {marque}", "is_company": True,
        "street": texte(langues, None, {l: RUES[l].format(n=hasard.randint(1, 300)) for l in RUES}),
        "city": "Kampot", "country_id": kh.id, "phone": f"+855 00 {i:03d} 000",
        "vat": f"ESSAI-{i:09d}" if avec_tva else False, "lang": langue_1})

    # Contacts : le premier a toujours un accès, un collègue en a un une fois sur trois.
    comptes, contacts = [], env["res.partner"]
    for rang, langue in enumerate([langue_1] + ([langue_2] if hasard.random() < 0.35 else [])):
        cle_langue = langue[:2]
        courriel = f"e{i:03d}{'ab'[rang]}@essai.example"
        contact = env["res.partner"].create({
            "name": f"{hasard.choice(CONTACTS[cle_langue])} {marque}", "parent_id": societe.id,
            "email": courriel, "lang": langue})
        env["res.users"].with_context(no_reset_password=True).create({
            "name": contact.name, "login": courriel, "partner_id": contact.id,
            "group_ids": [(6, 0, portail.ids)], "password": MDP})
        contacts |= contact
        comptes.append({"login": courriel, "lang": langue.replace("_", "-")})

    # Factures : payées, en partie, à payer ; parfois un avoir.
    factures = env["account.move"]
    for _n in range(hasard.randint(1, 5)):
        jour = hasard.choice(JOURS_FACTURE)
        facture = env["account.move"].create({
            "move_type": "out_invoice", "partner_id": societe.id, "invoice_date": jour,
            "invoice_date_due": jour + timedelta(days=hasard.choice([0, 15, 30])),
            "invoice_line_ids": lignes(langues, marque, taxe, hasard.randint(1, 3))})
        facture.action_post()
        tirage = hasard.random()
        if tirage < 0.4:
            payer(facture)
        elif tirage < 0.6:
            payer(facture, round(facture.amount_total / 2, 2))
        factures |= facture
    avoirs = env["account.move"]
    a_payer = factures.filtered(lambda f: f.payment_state == "not_paid")
    if a_payer and hasard.random() < 0.25:
        origine = a_payer[0]
        avoir = env["account.move"].create({
            "move_type": "out_refund", "partner_id": societe.id, "invoice_date": origine.invoice_date,
            "reversed_entry_id": origine.id,
            "invoice_line_ids": [(0, 0, {"product_id": PRODUITS["maint"].id, "quantity": 1, "price_unit": 25.0,
                                         "name": f"{texte(langues, 'maint')} {marque}",
                                         "tax_ids": [(6, 0, taxe.ids)]})]})
        avoir.action_post()
        # Odoo lettre parfois l'avoir d'office avec sa facture : seulement ce qui reste à lettrer.
        a_lettrer = (avoir.line_ids | origine.line_ids).filtered(
            lambda l: l.account_id.account_type == "asset_receivable" and not l.reconciled)
        if len(a_lettrer) > 1:
            a_lettrer.reconcile()
        avoirs |= avoir
    # Un brouillon de temps en temps : il ne doit apparaître nulle part dans l'espace client.
    brouillon = env["account.move"]
    if hasard.random() < 0.3:
        brouillon = env["account.move"].create({
            "move_type": "out_invoice", "partner_id": societe.id,
            "invoice_line_ids": lignes(langues, marque, taxe, 1)})
    toutes_factures |= factures | avoirs

    # Devis et commandes : brouillons (invisibles), envoyés (à valider), confirmés.
    def commande(etat):
        so = env["sale.order"].create({
            "partner_id": societe.id,
            "order_line": [(0, 0, {"product_id": PRODUITS[c].id, "name": f"{texte(langues, c)} {marque}",
                                   "product_uom_qty": hasard.randint(1, 3)})
                           for c in hasard.sample(list(PRODUITS), hasard.randint(1, 3))]})
        if etat == "sent":
            so.action_quotation_sent()
        elif etat == "sale":
            so.action_confirm()
        return so
    devis_brouillons = [commande("draft") for _n in range(hasard.randint(0, 2))]
    devis_envoyes = [commande("sent") for _n in range(hasard.randint(0, 2))]
    commandes = [commande("sale") for _n in range(hasard.randint(0, 2))]

    # Tickets, dont certains clos ; ouverts par l'un ou l'autre contact.
    tickets = env["helpdesk.ticket"]
    for code in hasard.sample(list(CATEGORIES_TICKET), hasard.randint(0, 4)):
        ticket = env["helpdesk.ticket"].create({
            "name": f"{texte(langues, code)} {marque}", "description": "<p>Ticket d'essai.</p>",
            "partner_id": hasard.choice(contacts).id, "team_id": equipe.id,
            "category_id": env.ref(f"chantrea_portail.categorie_{CATEGORIES_TICKET[code]}").id})
        if hasard.random() < 0.25:
            ticket.stage_id = etape_fermee
        tickets |= ticket

    # Matériel : garanties expirées, valides, ou qui finissent dans les 60 jours.
    equipements = env["fsm.equipment"]
    for code in hasard.sample(list(EQUIPEMENTS), hasard.randint(0, 6)):
        categorie, marque_eq, modele = EQUIPEMENTS[code]
        fin = aujourd_hui + timedelta(days=hasard.choice([-200, -10, 5, 30, 59, 61, 200, 700]))
        equipements |= env["fsm.equipment"].create({
            "name": f"{texte(langues, code)} {marque}", "chantrea_client_id": societe.id,
            "chantrea_categorie": categorie, "chantrea_marque": marque_eq, "chantrea_modele": modele,
            "chantrea_numero_serie": f"SN-E{i:03d}-{len(equipements) + 1}",
            "chantrea_date_achat": fin - timedelta(days=1095), "chantrea_fin_garantie": fin,
            "notes": f"<p>Note interne {marque} : jamais visible par le client.</p>"})

    # Contrat mensuel une fois sur deux, à partir du 16/11 (facture en brouillon).
    contrats = Contrat
    if hasard.random() < 0.5:
        nouveau = Contrat.new({"name": f"Maintenance mensuelle {marque}", "partner_id": societe.id,
                               "contract_template_id": modele_contrat.id, "user_id": env.ref("base.user_admin").id})
        nouveau._onchange_contract_template_id()
        contrats = Contrat.create(nouveau._convert_to_write(nouveau._cache))
        contrats.contract_line_ids.write({"price_unit": hasard.choice([60.0, 80.0, 120.0, 150.0, 250.0]),
                                          "date_start": "2026-11-16", "recurring_next_date": "2026-11-16"})
        contrats_crees |= contrats

    # Intervention ouverte, créée depuis un ticket, une fois sur quatre.
    interventions = env["fsm.order"]
    if tickets and hasard.random() < 0.25:
        site = env["fsm.location"].create({"name": f"{societe.name} – site", "owner_id": societe.id})
        contexte = tickets[0].action_create_order()["context"]
        interventions = env["fsm.order"].with_context(**contexte).create({
            "location_id": site.id, "description": f"<p>Intervention d'essai {marque}.</p>",
            "todo": f"<p>Instruction interne {marque}.</p>"})

    env.cr.commit()
    ouvertes = factures.filtered(lambda f: f.payment_state in ("not_paid", "partial"))
    attendus.append({
        "marque": marque, "profil": cle, "societe": societe.name, "comptes": comptes,
        "tableau": {
            "tickets": len(tickets.filtered(lambda t: not t.stage_id.closed)),
            "interventions": len(interventions.filtered(lambda o: not o.stage_id.is_closed)),
            "equipements": len(equipements),
            "garanties": len(equipements.filtered(lambda e: e.chantrea_etat_garantie == "bientot")),
            "contrats": len(contrats), "devis": len(devis_envoyes),
            "factures": len(ouvertes), "montant": round(sum(ouvertes.mapped("amount_residual")), 2)},
        "listes": {
            "/my/invoices": (factures | avoirs).mapped("name"),
            "/my/tickets": tickets.mapped("name"), "/my/equipments": equipements.mapped("name"),
            "/my/contracts": contrats.mapped("name"), "/my/quotes": [s.name for s in devis_envoyes],
            "/my/orders": [s.name for s in commandes], "/my/fsm_orders": interventions.mapped("name")},
        # Devis en brouillon : absents des listes. Facture en brouillon : page refusée.
        "invisibles": [s.name for s in devis_brouillons],
        "refuses": {"/my/invoices/%d": brouillon.ids},
        "details": {
            "/my/invoices/%d": (factures | avoirs).ids, "/my/ticket/%d": tickets.ids,
            "/my/equipment/%d": equipements.ids, "/my/contracts/%d": contrats.ids,
            "/my/orders/%d": [s.id for s in devis_envoyes + commandes] + [s.id for s in devis_brouillons],
            "/my/fsm_order/%d": interventions.ids},
    })
duree_donnees = time.time() - debut

# Tâches planifiées, comme le matin sur le serveur : factures des contrats, alertes de garantie.
debut = time.time()
Contrat.cron_recurring_create_invoice(date_ref=fields.Date.to_date("2026-11-16"))
env["fsm.equipment"]._chantrea_cron_alertes_garantie()
env.cr.commit()
duree_taches = time.time() - debut
factures_contrats = env["account.move"].union(*(c._get_related_invoices() for c in contrats_crees))
activites = factures_contrats.activity_ids.filtered(lambda a: a.summary == "Valider la facture mensuelle")

# Toutes les factures et avoirs en un seul PDF, rendu par lots de 100 (comme on imprime
# une sélection depuis la liste des factures).
from odoo.tools.pdf import merge_pdf  # noqa: E402

debut = time.time()
lots = [toutes_factures[n:n + 100] for n in range(0, len(toutes_factures), 100)]
pdf = merge_pdf([env["ir.actions.report"]._render_qweb_pdf("account.account_invoices", lot.ids)[0] for lot in lots])
duree_pdf = time.time() - debut
with open(os.path.join(SORTIE, "factures.pdf"), "wb") as fichier:
    fichier.write(pdf)
os.chmod(os.path.join(SORTIE, "factures.pdf"), 0o644)
env.cr.commit()

bilan = {
    "clients": NOMBRE, "comptes": sum(len(a["comptes"]) for a in attendus),
    "factures": len(toutes_factures), "contrats": len(contrats_crees),
    "factures_contrats_brouillon": len(factures_contrats.filtered(lambda f: f.state == "draft")),
    "activites_validation": len(activites),
    "tickets": sum(len(a["listes"]["/my/tickets"]) for a in attendus),
    "equipements": sum(a["tableau"]["equipements"] for a in attendus),
    "duree_donnees": round(duree_donnees, 1), "duree_taches": round(duree_taches, 1),
    "duree_pdf": round(duree_pdf, 1), "octets_pdf": len(pdf),
}
with open(os.path.join(SORTIE, "attendu.json"), "w", encoding="utf-8") as fichier:
    json.dump({"bilan": bilan, "clients": attendus}, fichier, ensure_ascii=False, indent=1)
os.chmod(os.path.join(SORTIE, "attendu.json"), 0o644)
print("BILAN", json.dumps(bilan, ensure_ascii=False))
