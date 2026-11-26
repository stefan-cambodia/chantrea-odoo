# Clients de DÉMONSTRATION par combinaison de langues, pour le poste local uniquement.
# Exécuté par scripts/donnees_demo.sh à la suite de donnees_demo.py (même « odoo shell » :
# trouver_ou_creer, produit, taxe_t, taxe_nt, maintenance, wifi, onduleur, mdp_client,
# portail, SORTIE sont repris de ce script). Peut être relancé sans créer de doublons.
#
# Un profil par combinaison. La première langue est celle du compte du client (espace client,
# courriels) ; ses textes (nom, adresse, désignations, ticket, équipement) sont saisis dans
# les deux langues de la paire, « première / seconde ». Les documents imprimés restent
# khmer + anglais pour tous : seuls les textes saisis changent.
#   fr_km : compte en français, textes « Français / ខ្មែរ »
#   km    : compte en khmer, textes en khmer seulement
#   en_fr : compte en anglais, textes « English / Français »
#   en_km : compte en anglais, textes « English / ខ្មែរ »
from datetime import date, timedelta

TEXTES = {
    "fr": {
        "wifi": "Installation d'un point d'accès Wi-Fi",
        "cable": "Câblage réseau (heures)",
        "onduleur": "Onduleur 1500 VA, livré et installé",
        "maint": "Maintenance mensuelle — novembre",
        "depannage": "Dépannage sur place (heures)",
        "geste": "Geste commercial : déplacement offert",
    },
    "en": {
        "wifi": "Wi-Fi access point installation",
        "cable": "Network cabling (hours)",
        "onduleur": "1500 VA UPS, delivered and installed",
        "maint": "Monthly maintenance — November",
        "depannage": "On-site troubleshooting (hours)",
        "geste": "Goodwill credit: travel free of charge",
    },
    "km": {
        "wifi": "ការដំឡើងចំណុចចូលប្រើវ៉ាយហ្វាយ",
        "cable": "ការតខ្សែបណ្ដាញ (ម៉ោង)",
        "onduleur": "ឧបករណ៍ថាមពលបម្រុង UPS ១៥០០ VA ដឹកជញ្ជូន និងដំឡើង",
        "maint": "ការថែទាំប្រចាំខែ — ខែវិច្ឆិកា",
        "depannage": "ការជួសជុលនៅនឹងកន្លែង (ម៉ោង)",
        "geste": "ការបញ្ចុះតម្លៃ៖ មិនគិតថ្លៃធ្វើដំណើរ",
    },
}

PROFILS = [
    {
        "cle": "fr_km", "langues": ("fr", "km"), "langue_compte": "fr_FR", "tva": "DEMO-000000101",
        "societe": "Boulangerie du Port – ហាងនំប៉័ងកំពង់ផែ (DÉMO)",
        "rue": "12, quai de la Rivière – ផ្ទះលេខ ១២ មាត់ទន្លេ", "ville": "Kampot", "tel": "+855 00 000 101",
        "contact": "Claire Martin (DÉMO)", "courriel": "claire@demo.example",
        "ticket": ("L'imprimante de tickets ne répond plus / ម៉ាស៊ីនបោះពុម្ពបង្កាន់ដៃលែងដំណើរការ (DÉMO)",
                   "Depuis ce matin, plus rien ne sort. / តាំងពីព្រឹកមិញ មិនបោះពុម្ពអ្វីសោះ។",
                   "chantrea_portail.categorie_materiel"),
        "equipement": ("Caisse enregistreuse – ម៉ាស៊ីនគិតលុយ (DÉMO)", "poste", "Epson", "TM-T88VI", "TM88-DEMO-101"),
        "avoir": False, "brouillon": True,
    },
    {
        "cle": "km", "langues": ("km",), "langue_compte": "km_KH", "tva": "DEMO-000000102",
        "societe": "សណ្ឋាគារ ទន្លេខៀវ (DÉMO)",
        "rue": "ផ្លូវលេខ ៧៣៣", "ville": "ក្រុងកំពត", "tel": "+855 00 000 102",
        "contact": "សុខ វិចិត្រ (DÉMO)", "courriel": "vichet@demo.example",
        "ticket": ("អ៊ីនធឺណិតដាច់ញឹកញាប់ (DÉMO)",
                   "អ៊ីនធឺណិតនៅជាន់ទី២ ដាច់រៀងរាល់ល្ងាច។",
                   "chantrea_portail.categorie_reseau"),
        "equipement": ("រ៉ោតទ័រវ៉ាយហ្វាយ ជាន់ទី២ (DÉMO)", "wifi", "TP-Link", "Deco X50", "DECO-DEMO-102"),
        "avoir": True, "brouillon": False,
    },
    {
        "cle": "en_fr", "langues": ("en", "fr"), "langue_compte": "en_US", "tva": False,
        "societe": "Kampot Pepper Export – Exportation de poivre (DÉMO)",
        "rue": "Road 33 – Route 33", "ville": "Kampot", "tel": "+855 00 000 103",
        "contact": "James Wilson (DÉMO)", "courriel": "james@demo.example",
        "ticket": ("Shared drive not accessible / Lecteur partagé inaccessible (DÉMO)",
                   "Nobody in the office can open the shared drive. / Personne au bureau n'ouvre le lecteur partagé.",
                   "chantrea_portail.categorie_sauvegarde"),
        "equipement": ("Backup NAS / Sauvegarde NAS (DÉMO)", "stockage", "Synology", "DS224+", "DS224-DEMO-103"),
        "avoir": True, "brouillon": False,
    },
    {
        "cle": "en_km", "langues": ("en", "km"), "langue_compte": "en_US", "tva": False,
        "societe": "Mekong Dive School – សាលាមុជទឹកមេគង្គ (DÉMO)",
        "rue": "Riverside Road – ផ្លូវមាត់ទន្លេ", "ville": "Kampot", "tel": "+855 00 000 104",
        "contact": "Srey Leak (DÉMO)", "courriel": "sreyleak@demo.example",
        "ticket": ("Email not syncing on phone / អ៊ីមែលមិនធ្វើសមកាលកម្មនៅលើទូរស័ព្ទ (DÉMO)",
                   "New emails only appear on the laptop. / អ៊ីមែលថ្មីបង្ហាញតែនៅលើកុំព្យូទ័រយួរដៃ។",
                   "chantrea_portail.categorie_messagerie"),
        "equipement": ("Office laptop / កុំព្យូទ័រយួរដៃការិយាល័យ (DÉMO)", "poste", "Dell", "Latitude 5440", "LAT-DEMO-104"),
        "avoir": False, "brouillon": True,
    },
]

# Produits retrouvés par leur nom : dans donnees_demo.py, « onduleur » désigne ensuite un équipement.
produit_onduleur = env["product.product"].with_context(lang="fr_FR").search(
    [("name", "=", "Onduleur 1500 VA (DÉMO)")], limit=1).with_env(env)
PRODUITS = {"wifi": wifi, "cable": maintenance, "onduleur": produit_onduleur,
            "maint": env.ref("chantrea_portail.produit_maintenance_mensuelle"), "depannage": maintenance,
            "geste": wifi}
PRIX = {"wifi": 60.0, "cable": 25.0, "onduleur": 180.0, "maint": 120.0, "depannage": 25.0, "geste": 25.0}


def texte(profil, code):
    return " / ".join(TEXTES[langue][code] for langue in profil["langues"])


def lignes_facture(profil, taxe, lignes):
    return [(0, 0, {"product_id": PRODUITS[code].id, "name": texte(profil, code), "quantity": quantite,
                    "price_unit": PRIX[code], "tax_ids": [(6, 0, taxe.ids)]})
            for code, quantite in lignes]


def piece(profil, ref, type_, client, taxe, lignes, jour, valider=True, **autres):
    existante = env["account.move"].search([("ref", "=", ref)], limit=1)
    if existante:
        return existante
    move = env["account.move"].create({
        "move_type": type_, "partner_id": client.id, "ref": ref, "invoice_date": jour,
        "invoice_line_ids": lignes_facture(profil, taxe, lignes), **autres})
    if valider:
        move.action_post()
    return move


def devis_demo(profil, ref, client, lignes, confirmer):
    existant = env["sale.order"].search([("client_order_ref", "=", ref)], limit=1)
    if existant:
        return existant
    commande = env["sale.order"].create({
        "partner_id": client.id, "client_order_ref": ref,
        "order_line": [(0, 0, {"product_id": PRODUITS[code].id, "name": texte(profil, code),
                               "product_uom_qty": quantite, "price_unit": PRIX[code]})
                       for code, quantite in lignes]})
    if confirmer:
        commande.action_confirm()
    return commande


dossier_langues = os.path.join(SORTIE, "langues")
os.makedirs(dossier_langues, exist_ok=True)
os.chmod(dossier_langues, 0o777)
aujourd_hui_langues = fields.Date.context_today(env["res.partner"])
resume = []

for profil in PROFILS:
    cle = profil["cle"]
    avec_tva = bool(profil["tva"])
    taxe = taxe_t if avec_tva else taxe_nt
    societe = trouver_ou_creer("res.partner", [("name", "=", profil["societe"])], {
        "name": profil["societe"], "is_company": True, "street": profil["rue"], "city": profil["ville"],
        "country_id": env.ref("base.kh").id, "phone": profil["tel"], "vat": profil["tva"],
        "lang": profil["langue_compte"]})
    contact = trouver_ou_creer("res.partner", [("email", "=", profil["courriel"])], {
        "name": profil["contact"], "parent_id": societe.id, "email": profil["courriel"],
        "lang": profil["langue_compte"]})
    utilisateur = env["res.users"].with_context(active_test=False).search([("login", "=", profil["courriel"])])
    if not utilisateur:
        utilisateur = env["res.users"].with_context(no_reset_password=True).create({
            "name": profil["contact"], "login": profil["courriel"], "partner_id": contact.id,
            "group_ids": [(6, 0, portail.ids)]})
    utilisateur.password = mdp_client

    # Devis en brouillon et commande confirmée.
    devis_brouillon = devis_demo(profil, f"DEMO-{cle}-DEVIS", societe, [("wifi", 3), ("cable", 6), ("onduleur", 1)], False)
    commande = devis_demo(profil, f"DEMO-{cle}-COMMANDE", societe, [("maint", 1), ("depannage", 2)], True)

    # Factures : une payée, une à payer ; puis un avoir ou un brouillon selon le profil.
    payee = piece(profil, f"DEMO-{cle}-F1", "out_invoice", societe, taxe,
                  [("maint", 1), ("depannage", 1.5)], date(2026, 11, 5))
    if payee.payment_state == "not_paid":
        env["account.payment.register"].with_context(
            active_model="account.move", active_ids=payee.ids).create({}).action_create_payments()
    a_payer = piece(profil, f"DEMO-{cle}-F2", "out_invoice", societe, taxe,
                    [("wifi", 2), ("cable", 4), ("onduleur", 1)], date(2026, 11, 19),
                    invoice_date_due=date(2026, 12, 19))
    pieces = [("devis", "sale.action_report_saleorder", devis_brouillon),
              ("commande", "sale.action_report_saleorder", commande),
              ("facture_payee", "account.account_invoices", payee),
              ("facture_a_payer", "account.account_invoices", a_payer)]
    if profil["avoir"]:
        avoir = piece(profil, f"DEMO-{cle}-AVOIR", "out_refund", societe, taxe, [("geste", 1)],
                      date(2026, 11, 20), reversed_entry_id=a_payer.id)
        pieces.append(("avoir", "account.account_invoices", avoir))
    if profil["brouillon"]:
        brouillon = piece(profil, f"DEMO-{cle}-F3", "out_invoice", societe, taxe, [("maint", 1)],
                          False, valider=False)
        pieces.append(("facture_brouillon", "account.account_invoices", brouillon))

    # Ticket et équipement.
    sujet, description, categorie = profil["ticket"]
    trouver_ou_creer("helpdesk.ticket", [("name", "=", sujet)], {
        "name": sujet, "description": f"<p>{description}</p>", "partner_id": contact.id,
        "category_id": env.ref(categorie).id, "team_id": env.ref("chantrea_portail.equipe_assistance").id})
    nom_eq, categorie_eq, marque, modele, serie = profil["equipement"]
    trouver_ou_creer("fsm.equipment", [("name", "=", nom_eq)], {
        "name": nom_eq, "chantrea_client_id": societe.id, "chantrea_categorie": categorie_eq,
        "chantrea_marque": marque, "chantrea_modele": modele, "chantrea_numero_serie": serie,
        "chantrea_date_achat": aujourd_hui_langues - timedelta(days=400),
        "chantrea_fin_garantie": aujourd_hui_langues + timedelta(days=330)})

    env.cr.commit()
    for nom, rapport, docs in pieces:
        pdf, _type = env["ir.actions.report"]._render_qweb_pdf(rapport, docs.ids)
        chemin = os.path.join(dossier_langues, f"{cle}_{nom}.pdf")
        with open(chemin, "wb") as fichier:
            fichier.write(pdf)
        os.chmod(chemin, 0o644)
    resume.append((profil, societe, [(nom, docs) for nom, _r, docs in pieces]))

print()
print("Clients par combinaison de langues (PDF dans demo-pdf/langues/) :")
for profil, societe, pieces in resume:
    print(f"  {profil['cle']:6} {societe.name} — accès {profil['courriel']} ({profil['langue_compte']})")
    for nom, docs in pieces:
        etat = docs.state if docs._name == "sale.order" else f"{docs.state}/{docs.payment_state}"
        print(f"         {nom:18} {docs.name or '(brouillon)':14} {docs.amount_total:>8.2f} USD  {etat}")
