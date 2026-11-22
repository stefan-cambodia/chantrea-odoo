import re
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError

CATEGORIES = [
    ("serveur", "Server"),
    ("switch", "Switch"),
    ("pare_feu", "Firewall"),
    ("wifi", "Wi-Fi"),
    ("onduleur", "UPS"),
    ("stockage", "Storage"),
    ("poste", "Workstation"),
    ("licence", "License"),
]

# Ce qu'on ne veut JAMAIS voir dans Odoo : adresses IP et identifiants d'accès.
# (Un numéro de version s'écrit avec un préfixe : « v1.0.2.15 ».)
MOTIF_IPV4 = re.compile(r"(?<![\w.])(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)(?![\w.])")
MOTIF_IPV6 = re.compile(
    r"(?<![\w:])(?:[0-9a-f]{1,4}:){7}[0-9a-f]{1,4}(?![\w:])"            # forme complète, 8 groupes
    r"|(?<![\w:])(?:[0-9a-f]{1,4}(?::[0-9a-f]{1,4}){0,6})?::"            # forme abrégée « :: »
    r"(?:[0-9a-f]{1,4}(?::[0-9a-f]{1,4}){0,6})?(?![\w:])",
    re.IGNORECASE)
MOTIF_IDENTIFIANT = re.compile(
    r"(?<![\w])(?:password|passwd|pwd|pass|mot\s+de\s+passe|mdp|login|username|user\s*name|identifiant|"
    r"code\s+wi-?fi|wifi\s+key|clé\s+wi-?fi|ពាក្យសម្ងាត់)\s*[:=]",
    re.IGNORECASE)
CHAMPS_SURVEILLES = ("name", "notes", "chantrea_marque", "chantrea_modele", "chantrea_numero_serie")


def contenu_interdit(texte):
    """Renvoie la nature du contenu interdit trouvé dans le texte, sinon None."""
    if not texte:
        return None
    texte = re.sub(r"<[^>]+>", " ", str(texte))
    if MOTIF_IPV4.search(texte) or MOTIF_IPV6.search(texte):
        return "ip"
    if MOTIF_IDENTIFIANT.search(texte):
        return "identifiant"
    return None


class FsmEquipment(models.Model):
    _inherit = "fsm.equipment"

    # Notes internes : jamais lisibles par un client, même par l'API.
    notes = fields.Html("Internal notes", groups="base.group_user")

    chantrea_client_id = fields.Many2one(
        "res.partner", string="Customer", index=True, tracking=True,
        compute="_compute_chantrea_client_id", store=True, readonly=False,
        help="Company that owns the equipment. It sees this record (read only) in its customer area.")
    chantrea_categorie = fields.Selection(CATEGORIES, string="Category", tracking=True)
    chantrea_marque = fields.Char("Brand", tracking=True)
    chantrea_modele = fields.Char("Model", tracking=True)
    chantrea_numero_serie = fields.Char("Serial number", tracking=True, index="trigram")
    chantrea_fournisseur_id = fields.Many2one("res.partner", string="Supplier", groups="base.group_user")
    chantrea_date_achat = fields.Date("Purchase date")
    chantrea_fin_garantie = fields.Date("Warranty end", tracking=True)
    chantrea_etat_garantie = fields.Selection(
        [("inconnue", "Unknown"), ("valide", "Under warranty"), ("bientot", "Ends within 60 days"),
         ("expiree", "Expired")],
        string="Warranty status", compute="_compute_chantrea_etat_garantie",
        search="_search_chantrea_etat_garantie")
    chantrea_contrat_id = fields.Many2one(
        "contract.contract", string="Contract",
        domain="[('partner_id', 'child_of', chantrea_client_id)]")
    chantrea_responsable_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user,
        domain=[("share", "=", False)], groups="base.group_user",
        help="Receives the warranty alerts (60 and 30 days before the end).")
    chantrea_alerte_60 = fields.Boolean("60-day alert sent", copy=False, groups="base.group_user")
    chantrea_alerte_30 = fields.Boolean("30-day alert sent", copy=False, groups="base.group_user")

    chantrea_ticket_ids = fields.Many2many(
        "helpdesk.ticket", "chantrea_equipement_ticket_rel", "equipment_id", "ticket_id", string="Tickets")
    chantrea_ticket_count = fields.Integer(compute="_compute_chantrea_compteurs", string="Ticket count")
    chantrea_intervention_count = fields.Integer(compute="_compute_chantrea_compteurs",
                                                 string="Field service order count")

    # ------------------------------------------------------------------
    @api.depends("location_id.owner_id")
    def _compute_chantrea_client_id(self):
        for equipement in self:
            if not equipement.chantrea_client_id and equipement.location_id.owner_id:
                equipement.chantrea_client_id = equipement.location_id.owner_id.commercial_partner_id

    @api.depends("chantrea_fin_garantie")
    def _compute_chantrea_etat_garantie(self):
        aujourd_hui = fields.Date.context_today(self)
        for equipement in self:
            fin = equipement.chantrea_fin_garantie
            if not fin:
                equipement.chantrea_etat_garantie = "inconnue"
            elif fin < aujourd_hui:
                equipement.chantrea_etat_garantie = "expiree"
            elif fin <= aujourd_hui + timedelta(days=60):
                equipement.chantrea_etat_garantie = "bientot"
            else:
                equipement.chantrea_etat_garantie = "valide"

    def _search_chantrea_etat_garantie(self, operateur, valeur):
        if operateur not in ("=", "in"):
            raise NotImplementedError(operateur)
        valeurs = [valeur] if operateur == "=" else list(valeur)
        aujourd_hui = fields.Date.context_today(self)
        dans_60 = aujourd_hui + timedelta(days=60)
        domaines = {
            "inconnue": [("chantrea_fin_garantie", "=", False)],
            "expiree": [("chantrea_fin_garantie", "<", aujourd_hui)],
            "bientot": ["&", ("chantrea_fin_garantie", ">=", aujourd_hui), ("chantrea_fin_garantie", "<=", dans_60)],
            "valide": [("chantrea_fin_garantie", ">", dans_60)],
        }
        resultat = []
        for v in valeurs:
            resultat = ["|"] + resultat + domaines[v] if resultat else domaines[v]
        return resultat or [("id", "=", 0)]

    def _chantrea_interventions(self):
        return self.env["fsm.order"].search([("equipment_ids", "in", self.ids)])

    def _compute_chantrea_compteurs(self):
        for equipement in self:
            equipement.chantrea_ticket_count = len(equipement.chantrea_ticket_ids)
            equipement.chantrea_intervention_count = self.env["fsm.order"].search_count(
                [("equipment_ids", "in", equipement.ids)])

    # ------------------------------------------------------------------
    # Aucun mot de passe, adresse IP ni identifiant d'accès
    # ------------------------------------------------------------------
    @api.constrains(*CHAMPS_SURVEILLES)
    def _check_chantrea_aucun_secret(self):
        for equipement in self:
            for champ in CHAMPS_SURVEILLES:
                nature = contenu_interdit(equipement.sudo()[champ])
                if nature:
                    libelle = equipement._fields[champ]._description_string(self.env)
                    if nature == "ip":
                        message = self.env._(
                            "« %(field)s » seems to contain an IP address. IP addresses, passwords and "
                            "access credentials must never be stored in Odoo. (For a version number, "
                            "write it with a prefix, e.g. v1.0.2.15.)", field=libelle)
                    else:
                        message = self.env._(
                            "« %(field)s » seems to contain a password or a login. Passwords, IP "
                            "addresses and access credentials must never be stored in Odoo.", field=libelle)
                    raise ValidationError(message)

    # ------------------------------------------------------------------
    # Alertes de fin de garantie (60 et 30 jours)
    # ------------------------------------------------------------------
    def write(self, vals):
        if "chantrea_fin_garantie" in vals:
            vals = dict(vals, chantrea_alerte_60=False, chantrea_alerte_30=False)
        return super().write(vals)

    @api.model
    def _chantrea_cron_alertes_garantie(self):
        aujourd_hui = fields.Date.context_today(self)
        type_activite = self.env.ref("chantrea_parc.activite_fin_garantie")
        # 30 jours d'abord : un équipement qui entre directement sous les 30 jours
        # ne reçoit qu'une alerte.
        for seuil, drapeau in ((30, "chantrea_alerte_30"), (60, "chantrea_alerte_60")):
            equipements = self.search([
                ("chantrea_fin_garantie", ">=", aujourd_hui),
                ("chantrea_fin_garantie", "<=", aujourd_hui + timedelta(days=seuil)),
                (drapeau, "=", False),
            ])
            for equipement in equipements:
                restant = (equipement.chantrea_fin_garantie - aujourd_hui).days
                responsable = equipement.chantrea_responsable_id or self.env.ref("base.user_admin")
                equipement.activity_schedule(
                    activity_type_id=type_activite.id,
                    summary=self.env._("Warranty ends on %(date)s (in %(days)s days)",
                                       date=equipement.chantrea_fin_garantie.strftime("%d/%m/%Y"), days=restant),
                    note=self.env._("Customer: %(customer)s. Offer a renewal or a replacement.",
                                    customer=equipement.chantrea_client_id.display_name or "-"),
                    user_id=responsable.id,
                    date_deadline=equipement.chantrea_fin_garantie,
                )
                valeurs = {drapeau: True}
                if seuil == 30:
                    valeurs["chantrea_alerte_60"] = True
                super(FsmEquipment, equipement).write(valeurs)

    # ------------------------------------------------------------------
    # Boutons
    # ------------------------------------------------------------------
    def action_chantrea_voir_tickets(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window", "res_model": "helpdesk.ticket", "name": self.env._("Tickets"),
            "view_mode": "list,form", "domain": [("id", "in", self.chantrea_ticket_ids.ids)],
            "context": {"default_chantrea_equipement_ids": [(6, 0, self.ids)],
                        "default_partner_id": self.chantrea_client_id.id},
        }

    def action_chantrea_voir_interventions(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window", "res_model": "fsm.order",
            "name": self.env._("Field service orders"),
            "view_mode": "list,form", "domain": [("equipment_ids", "in", self.ids)],
            "context": {"default_equipment_ids": [(6, 0, self.ids)],
                        "default_location_id": self.location_id.id},
        }
