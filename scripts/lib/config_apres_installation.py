# Exécuté par scripts/init_local.sh dans « odoo shell », APRÈS l'installation.
# Le plan comptable l10n_kh impose le riel (KHR) comme devise de la société ;
# Chantrea Systems facture en USD. Le changement n'est possible que tant
# qu'aucune écriture comptable n'existe : il est donc fait ici, juste après
# l'installation. Le module chantrea_base vérifiera ce réglage.
company = env.ref("base.main_company")
if env["account.move.line"].search_count([("company_id", "=", company.id)]):
    raise SystemExit("Des écritures existent déjà : devise non modifiée.")

usd, khr = env.ref("base.USD"), env.ref("base.KHR")
khr.active = True
company.currency_id = usd
env.cr.commit()
print(f"Devise principale : {company.currency_id.name} ; KHR active : {khr.active}")
