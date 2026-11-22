"""Un courriel envoyé à l'adresse d'assistance ouvre un ticket (docs/DEPLOIEMENT.md, étape 6).

On donne à Odoo le courriel brut, comme le fait la relève de la boîte aux lettres.
"""
from unittest.mock import patch

from odoo.tests import TransactionCase, tagged
from odoo.tools import config

COURRIEL = """\
From: {de}
To: {a}
Subject: {sujet}
Message-ID: {identifiant}
{entetes}MIME-Version: 1.0
Content-Type: text/plain; charset="utf-8"

{corps}
"""


@tagged("post_install", "-at_install", "chantrea")
class TestTicketsParCourriel(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        env = cls.env
        cls.domaine = env["mail.alias.domain"].create({"name": "exemple.test"})
        env.company.alias_domain_id = cls.domaine
        cls.equipe = env.ref("chantrea_portail.equipe_assistance")
        cls.equipe.alias_name = "assistance"
        cls.adresse = "assistance@exemple.test"
        societe = env["res.partner"].create({"name": "Hôtel (test courriel)", "is_company": True})
        cls.cliente = env["res.partner"].create({
            "name": "Dara (test courriel)", "parent_id": societe.id,
            "email": "dara@client.test", "lang": "km_KH"})
        cls.compte = env["res.users"].with_context(no_reset_password=True).create({
            "name": cls.cliente.name, "login": "dara-courriel-test", "partner_id": cls.cliente.id,
            "group_ids": [(6, 0, env.ref("base.group_portal").ids)]})
        cls.numero = 0

    def recevoir(self, de, sujet, corps="Bonjour.", a=None, en_reponse_a=None):
        type(self).numero += 1
        entetes = f"In-Reply-To: {en_reponse_a}\nReferences: {en_reponse_a}\n" if en_reponse_a else ""
        courriel = COURRIEL.format(
            de=de, a=a or self.adresse, sujet=sujet, corps=corps, entetes=entetes,
            identifiant=f"<test-{self.numero}@client.test>")
        return self.env["mail.thread"].message_process(False, courriel)

    def accuses(self, ticket):
        """Les accusés de réception du ticket : publiés au nom de la société."""
        return ticket.message_ids.filtered(
            lambda m: m.author_id == self.env.company.partner_id and ticket.number in (m.subject or ""))

    def test_courriel_d_un_client_connu(self):
        Ticket = self.env["helpdesk.ticket"]
        self.recevoir("Dara <dara@client.test>", "Le Wi-Fi ne marche plus (test courriel)")
        ticket = Ticket.search([("name", "=", "Le Wi-Fi ne marche plus (test courriel)")])
        self.assertEqual(len(ticket), 1)
        self.assertEqual(ticket.team_id, self.equipe)
        self.assertEqual(ticket.partner_id, self.cliente)
        self.assertEqual(ticket.channel_id, self.env.ref("helpdesk_mgmt.helpdesk_ticket_channel_email"))
        self.assertNotEqual(ticket.number, "/")
        # La cliente le retrouve dans son espace.
        self.assertIn(ticket, Ticket.with_user(self.compte).search([]).sudo())
        # Accusé de réception dans sa langue ; sa réponse reviendra à l'adresse d'assistance.
        accuse = self.accuses(ticket)
        self.assertEqual(len(accuse), 1)
        self.assertIn("សំណើ", accuse.subject)
        self.assertIn(self.adresse, accuse.reply_to)
        self.assertIn(self.env.company.name, accuse.email_from, "l'expéditeur doit porter le nom de la société")
        self.assertEqual(accuse.notification_ids.res_partner_id, self.cliente)

        # Sa réponse à l'accusé de réception arrive dans le même ticket.
        nb_tickets, nb_messages = Ticket.search_count([]), len(ticket.message_ids)
        self.recevoir("Dara <dara@client.test>", "Re: " + accuse.subject,
                      corps="Le routeur est dans le bureau.", en_reponse_a=accuse.message_id)
        self.assertEqual(Ticket.search_count([]), nb_tickets, "une réponse ne doit pas ouvrir un second ticket")
        self.assertEqual(len(ticket.message_ids), nb_messages + 1)
        self.assertEqual(ticket.message_ids[0].author_id, self.cliente)
        self.assertEqual(len(self.accuses(ticket)), 1, "pas de second accusé de réception")

    def test_courriel_d_un_inconnu(self):
        """Ticket créé sans client, à rattacher à la main ; rien n'est envoyé à l'inconnu
        (une adresse d'expéditeur se falsifie : pas de réponse automatique à n'importe qui)."""
        self.recevoir("Inconnu <quelquun@ailleurs.test>", "Demande de devis (test courriel)")
        ticket = self.env["helpdesk.ticket"].search([("name", "=", "Demande de devis (test courriel)")])
        self.assertEqual(len(ticket), 1)
        self.assertEqual(ticket.team_id, self.equipe)
        self.assertFalse(ticket.partner_id)
        self.assertIn("quelquun@ailleurs.test", ticket.partner_email)
        self.assertFalse(self.accuses(ticket))
        # Aucun client ne le voit dans son espace.
        self.assertNotIn(ticket, self.env["helpdesk.ticket"].with_user(self.compte).search([]).sudo())

    @patch.dict(config.options, {"email_from": "erp@exemple.test"})
    def test_expediteur_de_l_accuse_de_reception(self):
        """Le client voit le nom de la société. Sans adresse sur la société, l'accusé part
        de l'adresse d'expédition du serveur ; avec, les réponses reviennent à la société."""
        Ticket = self.env["helpdesk.ticket"]
        societe = self.env.company
        societe.alias_domain_id = False
        self.equipe.alias_name = False

        societe.email = False
        ticket = Ticket.create({"name": "Sans adresse (test courriel)", "description": "<p>x</p>",
                                "partner_id": self.cliente.id, "team_id": self.equipe.id})
        self.assertEqual(self.accuses(ticket).email_from, f'"{societe.name}" <erp@exemple.test>')

        societe.email = "contact@exemple.test"
        ticket = Ticket.create({"name": "Avec adresse (test courriel)", "description": "<p>x</p>",
                                "partner_id": self.cliente.id, "team_id": self.equipe.id})
        accuse = self.accuses(ticket)
        self.assertEqual(accuse.email_from, f'"{societe.name}" <contact@exemple.test>')
        self.assertIn("contact@exemple.test", accuse.reply_to)
