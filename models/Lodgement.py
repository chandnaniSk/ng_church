# -*- coding:utf-8 -*-
"""."""
from odoo import api, fields, models
from .helper import parish
from odoo.exceptions import UserError, ValidationError


class Lodgement(models.Model):
    """."""

    _name = 'ng_church.lodgement'

    def _get_default_journal(self):
        if self.env.user.company_id.transit_journal.id:
            return self.env.user.company_id.transit_journal.id
        raise UserError('Church Transist account is not set.')
    name = fields.Char(string='Name', default='Church Lodgement')
    date = fields.Date(string='Date', required=True)
    amount = fields.Float(string='Amount', required=True)
    description = fields.Text(string='Note', required=True)
    church_id = fields.Many2one('res.company', default=parish)
    journal_id = fields.Many2one('account.journal', string='Journal',
                                 domain=[('type', '=', 'bank')], required=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')],
                             copy=False, default='draft')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method', required=True)

    @api.constrains('amount')
    def _check_valid_amount(self):
        if self.amount < 1:
            raise ValidationError(
                'Please enter a valid amount of money {} amount can\'t be post for lodgement'.format(self.amount))

    def _prepare_account_payment(self):
        """Generate Account Invoice."""
        company = self.env.user.company_id
        payment_obj = self.env['account.payment']
        payload = {
            'company_id': company.id,
            'partner_id': parish(self),
            'partner_type': 'customer',
            'journal_id': self.journal_id.id,
            'amount': self.amount,
            'payment_date': self.date,
            'payment_method_id': self.payment_method_id.id,
            'communication': self.description,
            'payment_type': 'inbound'
        }
        payment_obj = payment_obj.create(payload)
        return payment_obj

    def lodge(self):
        """lodgement."""
        self._prepare_account_payment()
