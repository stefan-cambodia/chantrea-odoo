# Exécuté par scripts/init_local.sh et scripts/init_serveur.sh dans « odoo shell », AVANT l'installation
# de la comptabilité : le pays de la société doit être le Cambodge pour que
# le plan comptable l10n_kh soit choisi.
# Ces réglages seront repris de façon déclarative par le module chantrea_base.
import os

company = env.ref("base.main_company")
company.write({
    "name": "Chantrea Systems",
    "country_id": env.ref("base.kh").id,
    "currency_id": env.ref("base.USD").id,
    # Société en cours d'immatriculation : champs légaux laissés vides.
    "vat": False,
    "company_registry": False,
})

admin = env.ref("base.user_admin")
# En local : adresse fictive, le code de double authentification arrive dans Mailpit.
# Sur le serveur : init_serveur.sh demande la vraie adresse (ADMIN_EMAIL) et le mot de
# passe (ADMIN_PASSWORD), sans les écrire sur le disque.
vals = {"lang": "fr_FR", "tz": "Asia/Phnom_Penh", "email": os.environ.get("ADMIN_EMAIL") or "admin@example.com"}
mdp = os.environ.get("ADMIN_PASSWORD") or os.environ.get("ADMIN_LOCAL_PASSWORD")
if mdp:
    vals["password"] = mdp
admin.write(vals)

# Adresse publique (serveur) : utilisée dans les liens des courriels envoyés aux clients.
# Elle est figée pour qu'une connexion par une autre adresse ne la change pas.
url_publique = os.environ.get("URL_PUBLIQUE")
if url_publique:
    parametres = env["ir.config_parameter"].sudo()
    parametres.set_param("web.base.url", url_publique)
    parametres.set_param("web.base.url.freeze", "True")

# Double authentification obligatoire pour les utilisateurs internes.
env["ir.config_parameter"].sudo().set_param("auth_totp.policy", "employee_required")

env.cr.commit()
print("Configuration initiale : société KH/USD, admin en français, 2FA interne obligatoire.")
