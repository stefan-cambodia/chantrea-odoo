from odoo import models

from ..hooks import apres_plan_comptable


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    def _post_load_data(self, template_code, company, template_data):
        resultat = super()._post_load_data(template_code, company, template_data)
        company = company or self.env.company
        # Le plan cambodgien impose le KHR : on revient à l'USD (voir hooks.py).
        if template_code == "kh" and not company.parent_id:
            apres_plan_comptable(self.env, company)
        return resultat
