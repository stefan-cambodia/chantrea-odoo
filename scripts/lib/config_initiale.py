# Exécuté par scripts/init_local.sh dans « odoo shell », AVANT l'installation
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
# Adresse fictive (local) : le code de double authentification arrive dans Mailpit.
vals = {"lang": "fr_FR", "tz": "Asia/Phnom_Penh", "email": "admin@example.com"}
mdp = os.environ.get("ADMIN_LOCAL_PASSWORD")
if mdp:
    vals["password"] = mdp
admin.write(vals)

# Double authentification obligatoire pour les utilisateurs internes.
env["ir.config_parameter"].sudo().set_param("auth_totp.policy", "employee_required")

env.cr.commit()
print("Configuration initiale : société KH/USD, admin en français, 2FA interne obligatoire.")
