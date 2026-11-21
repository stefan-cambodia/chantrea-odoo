# Exécuté dans « odoo shell » : récupère tout de suite le taux officiel USD/KHR
# (même traitement que la tâche planifiée quotidienne).
r = env["res.currency.rate"]._chantrea_recuperer_taux(env.company)
env.cr.commit()
print(f"Taux USD/KHR : {len(r['crees'])} enregistré(s) ; en vigueur : "
      f"{r['taux_en_vigueur'] or 'aucun'} ({r['date_en_vigueur'] or '-'})")
for probleme in r["problemes"]:
    print("  ⚠", probleme)
