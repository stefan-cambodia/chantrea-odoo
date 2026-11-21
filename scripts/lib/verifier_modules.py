# Exécuté dans « odoo shell » : affiche l'état et la licence de chaque module
# demandé (scripts/modules.txt) et de ses dépendances hors Odoo standard.
from odoo.modules.module import get_module_path

with open("/tmp/modules.txt") as f:
    demandes = [l.strip() for l in f if l.strip() and not l.startswith("#")]

Module = env["ir.module.module"]


def origine(mod):
    chemin = get_module_path(mod.name, display_warning=False) or ""
    if "/opt/chantrea/oca/" in chemin:
        return "OCA/" + chemin.split("/opt/chantrea/oca/")[1].split("/")[0]
    if "/opt/chantrea/addons/" in chemin:
        return "maison"
    return "Odoo"


installes = Module.search([("state", "=", "installed")])
hors_odoo = installes.filtered(lambda m: origine(m) != "Odoo")
a_afficher = Module.search([("name", "in", demandes)]) | hors_odoo

ok = True
print(f"{'MODULE':30} {'ORIGINE':20} {'LICENCE':10} {'VERSION':14} ÉTAT")
for m in a_afficher.sorted(lambda m: (origine(m), m.name)):
    marque = "" if m.name in demandes else "  (dépendance)"
    print(f"{m.name:30} {origine(m):20} {m.license or '':10} {m.installed_version or '':14} {m.state}{marque}")
    ok &= m.state == "installed"

manquants = set(demandes) - set(Module.search([("name", "in", demandes)]).mapped("name"))
for n in sorted(manquants):
    print(f"{n:30} INTROUVABLE")
    ok = False

langues = env["res.lang"].search([("active", "=", True)]).mapped("code")
print("\nLangues actives :", ", ".join(langues))
print("Langue de l'admin :", env.ref("base.user_admin").lang)
print("Pays / devise société :", env.company.country_id.code, "/", env.company.currency_id.name)
print("Plan comptable :", env.company.chart_template)
print("Double authentification :", env["ir.config_parameter"].sudo().get_param("auth_totp.policy"))
print("\nRÉSULTAT :", "tous les modules demandés sont installés" if ok else "PROBLÈME, voir ci-dessus")
